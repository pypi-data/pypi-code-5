'''
Created on 12/Jul/2012

@author: Natalia Vale Asari

Define several classes for spectra:

Spec0D: F_lambda(lambda)
Spec1D: F_lambda(lambda, zone/object)
Spec2D: F_lambda(lambda, y, x)
'''

import sys
import os
import re
from copy import copy, deepcopy

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats
import atpy
import astropy.io.fits

import re
import pystarlight.util.cosmo_distances as cdist
import pystarlight.io.starlighttable #@UnusedImport

import StarlightUtils as stutil        


# Physical constants
c_light = 299792.458  # km/s


class WavelengthRange(object):
    '''
    Wavelength arrays helpers
    '''

    def __init__(self, ll = None):
        self.ll = ll

    def fromFits(self, pix_ref = None, lref = None, dl = None, Nl = None):

        if (pix_ref == None) and (lref == None) and (dl == None) and (Nl == None):
            print "!!! WARNING !!!> You need to parse pix_ref, lref, dl and Nl."
            sys.exit(1)

        llow = lref - (pix_ref - 1.0) * dl
        lupp = llow + dl * (Nl - 1)
        self.ll = np.linspace(llow, lupp, Nl)

        return self.ll

    def lobsToRestFrame(self, lobs, redshift):
        if np.array(redshift).shape == ():
            lrest = lobs / (1. + redshift)
        else:
            lrest = lobs[:, np.newaxis] / (1. + redshift[np.newaxis, :])
            
        return lrest

    def lrestToObsFrame(self, lrest, redshift):
        if np.array(redshift).shape == ():
            lobs = lrest * (1. + redshift)
        else:
            lobs = lrest[:, np.newaxis] * (1. + redshift[np.newaxis, :])

        return lobs


class SpecModel(object):
    '''
    Modeling a spec as a sum of several components (only tested for Spec0D so far)
    '''

    def __init__(self, s0d_obs, s0d_syn, smooth = None):
        self.fobs = s0d_obs
        self.cont = s0d_syn                # Synthetic continuum to get equivalent widths from

        if (smooth is None):
            self.smoothdata = deepcopy(self.fobs)
            self.smoothdata._spec__ld *= 0.
        else:
            self.smoothdata = smooth

        self.data = self.fobs - self.cont - self.smoothdata  # Spec instance to fit

        self.fsyn = self.cont
        self.fres = self.data

        self.cont.normalize_spec('lrest', 5590., 5680.)
        self.data.normalize_spec('lrest', 5590., 5680., normalize_by = self.cont.fnorm)

        self.base = deepcopy(self.fobs)
        self.base._spec__ld *= 0.

        
    def copy(self):
        return self.__class__(self.fobs, self.fsyn, smooth=self.smoothdata)

    
    def rectify_spec(self, rms_lim = 1., debug = False):

        data = deepcopy(self.data)
        
        # Initial paramters
        diff = data
        rms = np.std(diff._spec__ld)

        for i in np.arange(1, 3):

            if i == 1: rms_lim = 1.0 * rms_lim
            if i  > 1: rms_lim = 1.0 * rms_lim
                
            # Flag emission lines; note I extend the flags a bit
            flag_lines = np.abs(diff._spec__ld) >= (rms * rms_lim)
            flag_lines = flag_lines | np.append(flag_lines[1:], [0])
            flag_lines = flag_lines | np.append([0], flag_lines[:-1])
            data.add_flagType(flag_lines, flagType_id = 'emlines', flagType_value = 1)

            # Get local rms -- trick to get better at chopping wings of emission lines for next iteration
            meddata = diff.boxFilter_lambda(100, flag = True)
            rmsdata = meddata - diff
            rmslocal = rmsdata.boxFilter_lambda(30, flag = True)
            rms = np.abs(rmslocal._spec__ld)
            
            # Smooth spec
            smoothdata = data.gaussianFilter_lambda(15, flag = True)

            # Save new diff spec
            diff = data - smoothdata

            if debug:
              if i > 1: 
                data.plot(color_spec = "black")
                smoothdata.plot(color_spec = "purple")
                diff.plot(color_spec = "green")
                plt.fill_between(data.lrest, -rms * rms_lim, rms * rms_lim, alpha = 0.5)
                plt.axhline(0.)
                #plt.plot(self.data.lrest, flag_lines)

        self.smoothdata = smoothdata
        self.data._spec__ld[:] = diff._spec__ld

        if debug:
            orig = self.data + self.smoothdata
            orig.plot(color_spec = "blue")

    def add_noise_to_data(self, sd):

        from scipy.stats import norm
        
        # norm.rvs: The scale (scale) keyword specifies the standard deviation.
        Ntot = self.data.Nl * self.data.Npix
        aux__ld = norm.rvs(size=Ntot, scale=sd)
        N__ld = self.data.repackPixelDimensions(aux__ld)

        # Add noise
        newModel = self.copy()
        newModel.data._spec__ld += N__ld

        return newModel

    
    def mc_uncertainties(self, sd, Nruns = 10,
                         outfile = None, append = True, overwrite = False,
                         debug = False):
        '''
        Uncertainties from Monte Carlo realizations.
        '''

        # File to save to
        outfile = test_file(outfile, default='/tmp/lix.hdf5', append=(not overwrite), delete=overwrite, debug=debug)

        # Read old file if we are going to append it
        elines = []
        if (append) & (os.path.exists(outfile)):
            elines = read_lines_params_hdf5_dataset(outfile)
            outfile = test_file(outfile, default='/tmp/lix.hdf5', append=False, delete=True, debug=debug)
            
        # Open hdf5 file
        f = h5py.File(outfile, "w")

        # Save old runs in file
        ilow = 0
        if (append):
            if (len(elines) > 0):
                for key, value in elines.items():
                    ds = f.create_dataset(key, data = value, compression = 'gzip', compression_opts = 4)
                    ilow = max(ilow, int(key) + 1)
                    
        for irun in range(ilow, ilow+Nruns+1):

            # Add noise & refit
            newModel = self.add_noise_to_data(sd)
            newModel.fit_emis_lines_gauss_l()

            newModel.save_summary_to_hdf5_dataset(f, '%05i' % irun)

            # Save
            if debug:
                plt.figure(2)
                plt.clf()
                self.data.plot(color_spec = "blue")
                newModel.data.plot(color_spec = "green")
                self.plot_gaussians(color_spec = "cyan")
                newModel.plot_gaussians(color_spec = "yellow")

        f.close()
        
                
    def simple_uncertainties(self, sd, addnoise = False, 
                             outfile = None, overwrite = False,
                             debug = False):
        '''
        Uncertainties from simple `by hand' measurements.
        '''
    
        # Add noise (or not)
        if addnoise:
            newModel = self.add_noise_to_data(sd)
        else:
            newModel = self.copy()

        # File to save to
        outfile = test_file(outfile, default='/tmp/lix.hdf5', delete=overwrite, debug=debug)

        # Open hdf5 file
        f = h5py.File(outfile, "w")
            
        # Refit with new baseline
        for base in [-sd, sd]:
            newModel.fit_emis_lines_gauss_l(F0 = base)

            # Save
            newModel.save_summary_to_hdf5_dataset(f, 'std=%7.4f' % base)
    
            if debug:
                plt.figure(2)
                plt.clf()
                self.data.plot(color_spec = "blue")
                newModel.data.plot(color_spec = "green")
                self.plot_gaussians(color_spec = "cyan")
                newModel.plot_gaussians(color_spec = "yellow")
                print 'Press enter for next plot'
                raw_input()

        f.close()


    def save_summary_to_hdf5_dataset(self, f_h5py, name):
        '''
        f_h5py must be an open h5py file.
        '''
        elines, fmt, footer = self.summary_elines()
        ds = f_h5py.create_dataset(name, data = elines, compression = 'gzip', compression_opts = 4)
        

    def fit_emis_lines_gauss_l(self, lines_file = None, baseline = 'resid', F0 = 0., refit_all = False):

        # Create dictionary for all lines
        self.El_gauss_l = {}

        # Read line table
        self.lines_params = read_lines_params(lines_file)
        #self.lines_params = self.lines_params.rows([9, 10, 11])

        # Define if we want to calc the baseline or not
        if (baseline == 'resid'):
            F0_status = 'fixed'
        elif (baseline == 'cont'):
            F0_status = 'fixed'
        else:
            F0_status = 'limited'

        # Create lines with first guesses
        for line_params in self.lines_params:

            ll_blue_cont = (line_params[2], line_params[3])
            ll_red_cont  = (line_params[4], line_params[5]) 
            cont, cerror = self.measure_cont(ll_blue_cont, ll_red_cont, baseline)
            if (baseline == 'cont'): F0 = cont

            aux = LineModel(data = self.data, fit_type = "gauss_l",
                            l_centre = line_params[1], 
                            ll_blue_cont = ll_blue_cont,
                            ll_red_cont  = ll_red_cont,
                            F0_status = F0_status, F0 = F0,
                            basespec = self.base
                            )

            self.El_gauss_l[line_params[0]] = aux
            self.El_gauss_l[line_params[0]].cont = cont
            self.El_gauss_l[line_params[0]].cerror = cerror

        # Refit blended lines:
        # [NII], Ha
        # [SII]
        # [SIII]6312, [OI]6300
        self.blended_groups = [ ['[NII]6548', 'Halpha', '[NII]6584'],
                                ['[SII]6716', '[SII]6731'],
                                ['[SIII]6312', '[OI]6300'] ]
        
        for blended in self.blended_groups:
            # Changed below to be compatible with python 2.6 @ alphacrucis.
            # Try to get back to more elegant notation asap.
            #refit = {k: self.El_gauss_l[k] for k in blended}
            refit = dict((k, self.El_gauss_l[k]) for k in blended)
            El_gauss_sum_l = LinesModel(self.data, refit, F0_status = F0_status, basespec = self.base)

        # Refit everything --- takes a long time!
        if refit_all:
            self.El_gauss_sum_l = LinesModel(self.data, self.El_gauss_l)

            
    def measure_cont(self, ll_blue_cont, ll_red_cont, baseline = 'resid'):
        
        cont = -999.
        cerror = -999.
            
        flag_cont_blue = (self.cont.lrest >= ll_blue_cont[0]) & (self.cont.lrest <= ll_blue_cont[1])
        flag_cont_red  = (self.cont.lrest >= ll_red_cont[0])  & (self.cont.lrest <= ll_red_cont[1])
        flag_cont = flag_cont_blue | flag_cont_red

        if (sum(flag_cont) > 1):
            spec_cont = self.cont._spec__ld[flag_cont]
            spec_cont_err = self.data._spec__ld[flag_cont]
            
            cont = np.median(spec_cont)
            cerror = np.std(spec_cont_err)

        if np.isnan(cont): cont = -999.
        if np.isnan(cerror): cerror = -999.

        if (baseline == 'cont'):
            ff = (self.cont.lrest >= ll_blue_cont[0]) & (self.cont.lrest <= ll_red_cont[1])
            self.base._spec__ld[ff] = cont
            
        return cont, cerror
    
    def plot_gaussians(self, color_spec = 'black', linestyle = '-'):
        params = np.array([ line_model.params for line_name, line_model in self.El_gauss_l.items() ]).flatten()
        G = gaussian_sum_l(self.data.lrest, params)
        G += self.base._spec__ld
        plt.plot(self.data.lrest, G, color = color_spec, linestyle = linestyle)

        
    def calc_flux_integrated_all(self, spec = None, large_window = False, debug = False):

        if spec == 'fres':
            s0d = self.data
        elif spec == 'fobs':
            s0d = self.fobs
        elif spec == 'fsyn':
            s0d = self.fsyn
        
        if debug:
            s0d.plot(color_spec = "red")

        for line_name, line_model in self.El_gauss_l.items():
            params = deepcopy(line_model.params)
            intF, intC  = self._calc_flux_integrated(s0d, line_name, params, large_window = large_window, debug = debug)
            self.El_gauss_l[line_name].intF = intF
            self.El_gauss_l[line_name].intC = intC

            
        for ib, blended in enumerate(self.blended_groups):
            
            params = np.array([self.El_gauss_l[line_name].params for line_name in blended]).flatten()
            intF, intC  = self._calc_flux_integrated(s0d, 'blended%s' % ib, params, large_window = large_window, debug = debug)

            lcen = np.array([self.El_gauss_l[line_name].params[0] for line_name in blended]).flatten()
            ind = np.argsort(lcen)
            lines_sorted = np.array(blended)[ind]
            Nlines = len(lines_sorted)
            
            int_blended = 0.
            for i, line_name in enumerate(lines_sorted):
                # Define flux as measured by gaussian to all blended lines, except the central or red-most
                self.El_gauss_l[line_name].intF = self.El_gauss_l[line_name].params[1]
                self.El_gauss_l[line_name].intC = intC
                s0d.intF[line_name] = self.El_gauss_l[line_name].intF
                if (i != 1):
                    int_blended += self.El_gauss_l[line_name].intF

            # Save flux for central or red-most line
            self.El_gauss_l[lines_sorted[1]].intF = intF - int_blended
            s0d.intF[lines_sorted[1]] = self.El_gauss_l[lines_sorted[1]].intF

            if debug:
                print blended, intF

            
        if debug:
            for line_name, line_model in self.El_gauss_l.items():
                print line_name, 'int: ', line_model.intF, line_model.intC, line_model.intF/line_model.intC       
                print      '    gau:', line_model.params[1], line_model.cont, line_model.params[1] / line_model.cont

            
    def _calc_flux_integrated(self, s0d, line_name, params, cont_l = 10., large_window = False, debug = False):

        # Get gaussians
        l = s0d.lrest
        dl = l[1] - l[0]
        G = gaussian_sum_l(l, params)
        EWpars = {}

        # Now select the central window from the gaussians
        l_centre = params[0]
        f_line = (G > 5.e-3) | (abs(l - l_centre) < dl)

        if f_line.sum() == 0:
            ll_window = (l_centre-1., l_centre+1.)
        else:
            ind_f_line = np.where(f_line)[0]
            ll_window = (l[ind_f_line[0]], l[ind_f_line[-1]])

        ll_blue_cont = (ll_window[0] - cont_l, ll_window[0])
        ll_red_cont  = (ll_window[1], ll_window[1] + cont_l) 
        
        EWpars[line_name] = l_centre, ll_window, ll_blue_cont, ll_red_cont
            
        s0d.measureEW(EWpars = EWpars, large_window = large_window, debug = debug)

        return s0d.intF[line_name], s0d.intC[line_name]

    
    def summary_elines(self):
        '''
        Save emission line info to an easy-to-use array.
        '''

        # Old & wrong way commented out.
        # The trick below saves things in the same order as the input line list.
        #El_l = np.array([ line_model.params[0] for line_name, line_model in self.El_gauss_l.iteritems() ])

        line_names = self.lines_params['col1']
        line_models = np.array([ self.El_gauss_l[line_name] for line_name in line_names ])

        El_l  = np.array([ line_model.params[0] for line_model in line_models ])
        El_F  = np.array([ line_model.params[1] for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        El_v0 = np.array([ line_model.params[2] for line_model in line_models ])
        El_vd = np.array([ line_model.params[3] for line_model in line_models ])
        El_Cl = np.array([ line_model.params[4] for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        
        El_F_e  = np.array([ line_model.perror[1] for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        El_v0_e = np.array([ line_model.perror[2] for line_model in line_models ])
        El_vd_e = np.array([ line_model.perror[3] for line_model in line_models ])
        El_Cl_e = np.array([ line_model.perror[4] for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        
        El_chi2 = np.array([ line_model.m.fnorm for line_model in line_models ])
        
        El_C   = np.array([ line_model.cont   for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        El_C_e = np.array([ line_model.cerror for line_model in line_models ]) * self.cont.fnorm * self.cont.fobs_norm
        
        El_W   = safe_div(El_F, El_C)
        El_W_e = safe_div(El_F_e, El_C) + El_C_e * safe_div(El_W, El_C)
        
        El_SN = safe_div(El_F, El_F_e)

        
        # Clean nan's and inf's
        m = (lambda x: replace_nan_inf_by_minus999(x))
        Els   = zip(m(El_l), m(El_F), m(El_F_e), m(El_W), m(El_W_e), m(El_vd), m(El_vd_e), m(El_v0), m(El_v0_e), m(El_SN), m(El_C), m(El_C_e), m(El_chi2), m(El_Cl), m(El_Cl_e))
        names   = ["lambda",  "El_F",  "El_F_e",  "El_W",  "El_W_e",  "El_vd",  "El_vd_e",  "El_v0",  "El_v0_e",  "El_SN",  "El_C",  "El_C_e",   "chisqr",  "El_Cl",  "El_Cl_e"]
        formats = ['float64' for i in xrange(len(names))]
        elines = np.array(Els, dtype={'names': names, 'formats': formats})

        fmt = "%8.3f " + ' '.join(['%12.4e' for i in xrange(len(names)-1)])
        footer = '# ' + names[0] + ''.join(['%13s' % name for name in names[1:]]) + '\n'
        
        return elines, fmt, footer
    
        
class LineModel(object):
    '''
    Modeling one line as a function --- only gaussian implemented so far
    '''

    def __init__(self, data, fit_type, 
                 l_centre, ll_blue_cont, ll_red_cont,
                 v0_min = -200., v0_max = 200., 
                 vd_min = 0.,    vd_max = 500.,
                 v0 = 0.,   v0_status  = 'limited',
                 vd = 100., vd_status  = 'limited',
                 F  = 1.,    F_status  = 'limited',
                 F0 = 0.,    F0_status = 'fixed',
                 basespec = None
                 ):

        # Spec instance to fit
        self.data     = data  
        #self.data.normalize_spec('lrest', 5590., 5680.)

        if (basespec is not None):
            self.data = data - basespec
            
        # Type of fit: gaussian, voigt, etc
        self.fit_type = fit_type

        # Line parameters: centre, blue and red continua
        self.l_centre     = l_centre      
        self.ll_blue_cont = ll_blue_cont       
        self.ll_red_cont  = ll_red_cont  

        # Calc local continuum baseline with ll_blue_cont and ll_red_cont
        self.calc_baseline()

        # Limits for v0 and vd
        self.v0_min = v0_min
        self.v0_max = v0_max
        self.vd_min = vd_min
        self.vd_max = vd_max

        # First guesses or fixed v0, vd, F, F0 (baseline)
        self.v0 = v0
        self.vd = vd
        self.F  = F
        self.F0 = F0

        # Status = limited (free), fixed, tied (constrained by other lines)
        # TO DO properly; this is only being used for the F0 baseline
        self.v0_status = v0_status
        self.vd_status = vd_status
        self.F_status  = F_status
        self.F0_status = F0_status

        # Fit gaussian
        if (fit_type == "gauss_l"):
            self.fit_gauss_l()
        
    def calc_baseline(self):
        pass

    def fit_gauss_l(self):
        from mpfit import mpfit

        import copy

        # Transform v --> l
        lref = 7000.
        self.v0_min = (lref / c_light) * self.v0_min
        self.v0_max = (lref / c_light) * self.v0_max
        self.vd_min = (lref / c_light) * self.vd_min
        self.vd_max = (lref / c_light) * self.vd_max
        self.v0     = (lref / c_light) * self.v0
        self.vd     = (lref / c_light) * self.vd

        # Get all parameters first guesses into one array
        par_init = [self.l_centre, self.F, self.v0, self.vd, self.F0]

        # Populate the configurations for each parameter
        par_info = [{'value': 0., 'fixed': 0, 'limited': [0, 0], 'limits' : [0., 0.], 'tied' : ''}
 												for i in range(len(par_init))]

        par_info[0]['fixed'  ] = 1
        par_info[1]['limited'] = [1, 0]
        par_info[1]['limits' ] = [0, 0]
        par_info[2]['limited'] = [1, 1]
        par_info[2]['limits' ] = [self.v0_min, self.v0_max]
        par_info[3]['limited'] = [1, 1]
        par_info[3]['limits' ] = [self.vd_min, self.vd_max]
        par_info[4]['fixed'  ] = 1

        # Calc baseline
        if (self.F0_status != 'fixed'):
            par_init[4] = self.F
            par_info[4]['fixed'  ] = 0
            par_info[4]['limited'] = [1, 1]
            par_info[4]['limits' ] = [-1, 5]

        data_fit = { 'x' : self.data.lrest, 
                     'y' : self.data._spec__ld, 
                     'err' : self.data._erro__ld }

        self.m = mpfit(self.mpfit_gaussian_l, par_init, parinfo = par_info, functkw = data_fit, quiet = 1)

        if (self.m.perror is None):
            self.m.perror = np.zeros_like(self.m.params) -999.

        self.params = self.m.params
        self.perror = self.m.perror

        #G = gaussian_sum_l(self.data.lrest, self.params)
        #plt.plot(self.data.lrest, G)
        #print self.params[0], self.params[2], self.params[3], self.params[4]

        
    def fit_gauss_v(self):
        pass


    def mpfit_gaussian_l(self, p, fjac = None, x = None, y = None, err = None):

        # Fix error == 0
        if (y != None) & (err != None):
            err = np.where(err == 0., 0.1*y, err)

        # If fjac==None then partial derivatives should not be
        # computed.  It will always be None if MPFIT is called with default
        # flag.
        model = gaussian_l(x, p)

        # Non-negative status value means MPFIT should continue, negative means
        # stop the calculation.
        status = 0

        return [status, (y-model)/err]


class LinesModel(object):
    '''
    Modeling several lines
    '''

    def __init__(self, data, dict_LineModel, 
                 F0_status = 'fixed',
                 basespec = None):

        self.data = data
        self.lines = dict_LineModel
        if (basespec is not None):
            self.data = data - basespec

        self.F0_status = F0_status

        # Fit gaussians
        self.fit_gauss_sum_l()


    def fit_gauss_sum_l(self):
        from mpfit import mpfit
        import copy

        # Get all parameters first guesses into one array
        par_init = np.array([ line_model.params for line_name, line_model in self.lines.iteritems() ]).flatten()

        # Populate the configurations for each parameter
        par_info = [{'value': 0., 'fixed': 0, 'limited': [0, 0], 'limits' : [0., 0.], 'tied' : ''}
 												for i in range(len(par_init))]

        i_NII6548 = None
        i_NII6584 = None
        n = 5

        for i, line_name in enumerate(self.lines):

            line_model = self.lines[line_name]

            # Line center
            par_info[0+n*i]['fixed'  ] = 1

            # Flux
            par_info[1+n*i]['limited'] = [1, 0]
            par_info[1+n*i]['limits' ] = [0, 0]

            # v0
            par_info[2+n*i]['limited'] = [1, 1]
            par_info[2+n*i]['limits' ] = [line_model.v0_min, line_model.v0_max]

            # vd
            par_info[3+n*i]['limited'] = [1, 1]
            par_info[3+n*i]['limits' ] = [line_model.vd_min, line_model.vd_max]

            # Baseline
            par_info[4+n*i]['fixed'  ] = 1
            if (self.F0_status != 'fixed'):
                if (i == 0):
                    par_info[4+n*i]['fixed'  ] = 0
                    par_info[4+n*i]['limited'] = [1, 1]
                    par_info[4+n*i]['limits' ] = [-1, 5]
                    par_init[4+n*i] =  0.
                else:
                    par_info[4+n*i]['tied'] = 'p[4]'
            
            # Save lines to be tied
            if (line_name == '[NII]6548'): i_NII6548 = i
            if (line_name == '[NII]6584'): i_NII6584 = i

                
        # Get ties done
        if (i_NII6548 != None) & (i_NII6584 != None):
            # Flux
            #par_info[1+n*i_NII6548]['tied'] = 'p[%s] / 3.' % (1+n*i_NII6584)
            # v0
            par_info[2+n*i_NII6548]['tied'] = 'p[%s]' % (2+n*i_NII6584)
            # vd
            par_info[3+n*i_NII6548]['tied'] = 'p[%s]' % (3+n*i_NII6584)
            
        # Treat baseline here
        data_fit = { 'x' : self.data.lrest, 
                     'y' : self.data._spec__ld,
                     'err' : self.data._erro__ld }

        # Plot
        #plt.clf()
        #G = gaussian_sum_l(self.data.lrest, par_init)
        #plt.plot(self.data.lrest, self.data.spec__l, color = 'k', linestyle = 'steps-mid')
        #plt.plot(self.data.lrest, G, color = 'purple')
        #plt.xlim(6400, 6800)
        #print par_init
        
        #gaussian_sum_l(self.data.lrest, par_init)
        self.m = mpfit(self.mpfit_gaussian_sum_l, par_init, parinfo = par_info, functkw = data_fit, quiet = 1)

        # Plot
        #G = gaussian_sum_l(self.data.lrest, self.m.params)
        #plt.plot(self.data.lrest, G, color = 'red')
        #print self.m.params
        
        if (self.m.perror is None):
            self.m.perror = np.zeros_like(self.m.params) -999.
        
        params__e = self.m.params.reshape(-1, 5)
        perror__e = self.m.perror.reshape(-1, 5)
        
        # Save new parameters to each LineModel
        for i, line_name in enumerate(self.lines):
            self.lines[line_name].params = params__e[i]
            self.lines[line_name].perror = perror__e[i]
            self.lines[line_name].m = self.m

        
    def mpfit_gaussian_sum_l(self, p, fjac = None, x = None, y = None, err = None):
        # If fjac==None then partial derivatives should not be
        # computed.  It will always be None if MPFIT is called with default
        # flag.
        model = gaussian_sum_l(x, p)
        # Non-negative status value means MPFIT should continue, negative means
        # stop the calculation.
        status = 0
        return [status, (y-model)/err]

    
        
class Spec(object):
    '''
    Parent class for all Spec*D classes
    '''
        
    def __init__(self, spec, lobs = None, lrest = None,
                 redshift = 0.,
                 fobs_norm = 1.,
                 fnorm_spatial = None,
                 erro = None,
                 mask = None,
                 flag = None,
                 flagType = None,
                 flagType_value = None,
                 flagType_id = None,
                 add_flag_to_spatial_mask = True,
                 name = None,
                 debug = False):

        self.debug = debug
        self.name = name

        if (lobs == None) and (lrest == None):
            print "!!! WARNING !!!> You need to inform at least one of the wavelengths arrays: lrest or lobs."
            sys.exit(1)

        if (lobs  != None): self.lobs  = lobs
        if (lrest != None): self.lrest = lrest
        self.redshift = redshift

        # Transform lobs in lrest or vice-versa if redshift is given
        if (lobs != None) & (lrest == None):
            _ll = WavelengthRange()
            self.lrest = _ll.lobsToRestFrame(self.lobs, self.redshift)

        if (lobs == None) & (lrest != None):
            _ll = WavelengthRange()
            self.lobs = _ll.lrestToObsFrame(self.lrest, self.redshift)

        # Save spec
        if (spec != None):
            spec_prob = np.isnan(spec)
            self._spec__ld = np.where( spec_prob, -999., spec )

            # Get dimensions
            # Convention: __ld = lambda, dimension-dependent info (nothing for Spec0D, zone for Spec1D, yx for Spec2D)
            self.Nd = self._spec__ld.ndim

        # Calculate dimensions
        self.Nl = len(self.lrest)
        self.Ny = 1
        self.Nx = 1
        if (self.Nd >= 2): self.Ny = self._spec__ld.shape[1]
        if (self.Nd >= 3): self.Nx = self._spec__ld.shape[2]            
        self.Npix = self.Ny * self.Nx
        
        # Creat error spectra if not given
        if (erro == None):
            "@@> Creating error spectra..."
            self._erro__ld = np.where( spec_prob, -999., spec*0.1 )
        else:
            self._erro__ld = np.where( np.isnan(erro), -999., erro)

        # Save spatial mask
        self._mask__d = np.ones_like(self._spec__ld.sum(axis = 0), dtype = 'bool')
        if (mask != None): self._mask__d = (mask > 0)

        # Flux normalization
        self.fobs_norm = fobs_norm
        self._fnorm__d = np.ones_like(self._mask__d, dtype = "float")
        if (fnorm_spatial != None): self._fnorm__d = fnorm_spatial
        
        # Creating flag types (flagType__ld) and summed flag (flag__ld).
        # Each flag type has a value (e.g., 11) and an array of True/False (flagged/not flagged by that condition),
        # so that flag__ld = value_flagType__ld * array_flagType__ld
        self._flagType__ld = {}
        self._flag__ld = flag
        if (flag != None): self._flag__ld = flag.copy()

        if (flagType == None) & (flag == None):
            # Leave flagType empty & create default total flag (all elements = 0)
            if (debug): print "@@> Creating empty flag..."
            self.add_flagType(flagType, update_spatial_mask = add_flag_to_spatial_mask)

        if (flagType != None) & (flag == None):
            # Create flagType for flagType & create total flag from flagType
            self.add_flagType(flagType, flagType_id = flagType_id, flagType_value = flagType_value, update_spatial_mask = add_flag_to_spatial_mask)

        if (flagType == None) & (flag != None):
            # Create flagType from total flag & leave total flag as given
            # TO DO: separate flag into sums, etc
            self.add_flagType(flag, update_spatial_mask = add_flag_to_spatial_mask, update_flag = False)

        if (flagType != None) & (flag != None):
            # Create flagType for flagType but do NOT update total flag
            self.add_flagType(flagType, flagType_id = flagType_id, flagType_value = flagType_value, update_spatial_mask = add_flag_to_spatial_mask)
            print "!!! WARNING !!!> You have parsed both a summed flag (flag) and a flag type (flagType)."
            print "                 I substituted your total flag by your flagType sum, you should check if that is what you really want."

            
    def add_flagType(self, flagType, flagType_id = None, flagType_value = None, update_flag = True, update_spatial_mask = False):

        if (flagType != None):

            # Define default flag value
            if (flagType_value == None): flagType_value = 91

            # Define default flag id from value
            if (flagType_id == None): flagType_id = 'flag%s' % flagType_value

            # See if the given value is not already being used
            if (self._flagType__ld):
                # Get values for each flag.
                # This zip() complicated thing is a trick to get elements from a list inside a dictionary.
                values = np.array( zip(*self._flagType__ld.values())[0] )
                if ( (flagType_value == values).sum() > 0 ) & (not (flagType_id in self._flagType__ld)):
                    new_value = values.max() + 1
                    # Add flag to flag already found
                    if (self.debug): print "@@> Flag value %s already in use, using %s instead." % (flagType_value, new_value)
                    flagType_value = new_value


            # Add flag to existing one, if there is already one of the same ID, or create a new one
            if (flagType_id in self._flagType__ld):
                flagNew = (self._flagType__ld[flagType_id][1]) | (flagType > 0)
                #print flagNew.sum(), flagType.sum(), (self._flagType__ld[flagType_id][1]).sum()
                if (self.debug): print "@@> Adding to old flag %s with value %s." % (flagType_id, flagType_value)
                if (flagType_value != self._flagType__ld[flagType_id][0]):
                    print "!!! WARNING !!!> Your flag %s had value %s, now being replaced by %s." % (flagType_id, self._flagType__ld[flagType_id][0], flagType_value)
            else:
                flagNew = (flagType > 0)
                if (self.debug): print "@@> Adding new flag %s with value %s." % (flagType_id, flagType_value)


            # Add flag to flagType
            self._flagType__ld[flagType_id] = [flagType_value, flagNew]


            # Update mask
            if (update_spatial_mask):
                if (self.debug): print "@@> Updating spatial mask with flag %s (%s)." % (flagType_id, flagType_value)
                self._update_spatial_mask(flagNew)

        # Update summed flag
        if (update_flag):
            if (self.debug): print "@@> Creating new summed flag."
            self._update_flag(add_or_replace = 'replace')
            


    def _update_flag(self, add_or_replace = 'add'):

        # Create default flag (= 0 everywhere) when creating anew or replacing
        if (self._flag__ld == None):
            self._flag__ld = np.zeros_like(self._spec__ld, dtype = 'int64')

        if (add_or_replace == 'replace'):
            if (self.debug): print "@@> Replacing flag__ld..."
            self._flag__ld[:] = 0

        # If there are flags in flagTypes, sum them up to create total flag
        if (self._flagType__ld):
            for value, f__ld in self._flagType__ld.values():
                self._flag__ld += value * f__ld


    def _update_spatial_mask(self, flag__ld):
        # Create mask in lambda
        # My definition of mask is ~ to the flags I used to use in SM, so that
        # mask = 1 --> pixel is OK, mask = 0 --> pixel should be masked out.

        # This should work, but 1 time out of 10 or 30 it just spits out buggy numbers in the sum, e.g.:
        # -36310267709161472 -72057044298891137
        #mask_extra__d = flag__ld.sum(axis = 0) < self.Nl
        # So I am taking the long way home and doing the loop myself. This is solid and adds 0.1 sec for
        # a 46 x 73 x 78 array.

        #lix1 = flag__ld.sum(axis = 0)
        #lix2 = lix1 < self.Nl

        mask_extra__d = flag__ld.sum(axis = 0) < self.Nl

        '''
        print flag__ld.sum(axis = 0)[50:60,20:30]
        print flag__ld.sum(axis = 0)[50, 20]

        print flag__ld.sum(axis = 0)[50, 20]

        plt.figure(10)
        plt.clf()
        plt.subplot(221)
        plt.imshow(mask_extra__d)
        plt.colorbar()
        plt.subplot(222)
        plt.imshow(self._mask__d)
        plt.colorbar()
        plt.subplot(223)
        plt.plot(self.lrest, self._spec__ld[..., 50, 20])
        '''
        
        if (self.Nd > 1):
            self._mask__d[(~self._mask__d) | (~mask_extra__d)] = False
        else:
            self._mask__d = (self._mask__d) & (mask_extra__d)


        '''
        # Alternative calc for bug:
        j_sum = np.zeros_like(self._mask__d, dtype = "float64")
        for flag__l1 in flag__ld: j_sum += flag__l1
        mask_extra__d = j_sum < self.Nl
        '''
        
        
    def count_flags(self, llow = None, lupp = None):
        # Count flags (%) in a given wavelength range.

        if (llow == None): llow = self.lrest[0]
        if (lupp == None): lupp = self.lrest[-1]

        mask__l = (self.lrest >= llow) & (self.lrest <= lupp)
        flag__ld = self._flag__ld[mask__l]
        Nl = flag__ld.shape[0]

        percFlagged__d = (flag__ld > 0).sum(axis = 0) * 100. / float(Nl)
        return percFlagged__d
        
        
    def mask_lambda(self, type_ids, type_exclude = None):
        '''
        Return mask for given flag type, where:
        mask = 1 --> pixel is OK, mask = 0 --> pixel should be masked out.
        i.e., mask = "inverse" of flag.

        Note that this also masks out where spec is bad (= nan or -999).

        Usage:
        mask__ld = s2d.mask_lambda( ["califa_flag", "sky_lines", "my_flag"] )

        To add up all flags:
        mask__ld = s2d.mask_lambda( "all" )

        Or to add all but not some:
        mask__ld = s2d.mask_lambda( "all", type_exclude = ["big_errors", "small_errors"] )
        '''

        # Create empty lambda mask
        mask__ld = np.ones_like(self._spec__ld, dtype = 'bool')

        # Mask out bad spec
        mask__ld[ (np.isnan(self._spec__ld)) | (self._spec__ld < -990.) ] = False
        
        # Create mask in lambda from chosen flags
        if (self._flagType__ld):

            # Option to add up all flags
            if (type_ids == "all"):
                type_ids = self._flagType__ld.keys()

            # Flags not to be added
            if (type_exclude != None):
                for i in type_exclude[:]:
                    if i in type_ids:
                        type_ids.remove(i)

            # Summing flags up
            for type_id in type_ids:
                if (type_id in self._flagType__ld):
                    value, f__ld = self._flagType__ld[type_id]
                    if (self.debug): print "@@> Adding %s (%s) to mask__ld." % (type_id, value)
                    mask__ld[(f__ld)] = False


        return mask__ld


    def flag_lambda(self, ll, llow, lupp, flag_value, flagType_id = None, add_flag_to_spatial_mask = False):
        '''
        Add flag to a wavelength window, e.g., to mask sky lines.
        '''

        if (ll == 'lobs'):
            ll = self.lobs
        elif (ll == 'lrest'):
            ll = self.lrest

        # Correcting dimensions of wavelength vector
        # This gives the worng broadcasting, so, no, do not do this!
        #if (self.Nd == 2):
        #    ll = ll[:, np.newaxis]
        #elif (self.Nd == 3):
        #    ll = ll[:, np.newaxis, np.newaxis]

        ll_to_flag = (ll >= llow) & (ll <= lupp)
        flagType = np.zeros_like(self._spec__ld, dtype = 'bool')
        flagType[ll_to_flag] = True
         
        self.add_flagType(flagType, flagType_id = flagType_id, flagType_value = flag_value, update_spatial_mask = add_flag_to_spatial_mask)


    def flag_bigerrors(self, threshold, flag_value, flagType_id = None, add_flag_to_spatial_mask = False):
        '''
        Add flag for big errors
        '''

        flux_flag = np.abs( self._erro__ld / (self._spec__ld + (self._spec__ld == 0)) ) > threshold
        self.add_flagType(flux_flag, flagType_id = flagType_id, flagType_value = flag_value, update_spatial_mask = add_flag_to_spatial_mask)


    def flag_smallerrors(self, threshold, flag_value, flagType_id = None, add_flag_to_spatial_mask = False):
        '''
        Add flag for small errors
        '''

        flux_flag = np.abs( self._erro__ld / (self._spec__ld + (self._spec__ld == 0)) ) < threshold
        self.add_flagType(flux_flag, flagType_id = flagType_id, flagType_value = flag_value, update_spatial_mask = add_flag_to_spatial_mask)
        
    def error_replace(self, flagType_id, replace = 'median'):

        if (replace == 'median'):
            flag_replace = self._flagType__ld[flagType_id][1]
            mask__ld = self.mask_lambda( "all" ) & (~np.isnan(self._erro__ld))

            # Mask errors with nan's
            erro_masked__ld = np.where(mask__ld, self._erro__ld, np.nan )

            # Calc median and replace
            aux__ld = np.where(flag_replace, scipy.stats.nanmedian(erro_masked__ld, axis=0), self._erro__ld)

            # Replace nan's left: they will be left only when the whole pixel is flagged
            aux__ld = np.where(np.isnan(aux__ld), self._erro__ld, aux__ld)

            # Substitute values in error spec
            self._erro__ld[flag_replace] = aux__ld[flag_replace]

            
            ## This is exatly the same as above. It is more contorted but I have control
            ## over it --- good for debugging, but it as tad slow (2.8 sec instead of 2.4)
            #
            ## Calc median error in pixel
            #mask__lp = self.collapsePixelDimensions(mask__ld)
            #erro__lp = self.collapsePixelDimensions(self._erro__ld)
            #errmed__p = np.zeros([self.Npix]) * np.nan
            #
            #for i in range(self.Npix):
            #    erro__l = erro__lp[mask__lp[:,i], i]
            #    if len(erro__l) > 0:
            #        errmed__p[i] = np.median(erro__l)
            #
            #errmed__d = np.resize( errmed__p, (self.Ny, self.Nx) )
            #
            ## Substitute flagged errors by median in pixel
            #aux__ld = np.where(flag_replace, errmed__d, self._erro__ld)
            #aux__ld = np.where(np.isnan(aux__ld), self._erro__ld, aux__ld)
            #self._erro__ld[flag_replace] = aux__ld[flag_replace]

            
            ## This would be much more elegant, but it takes 10x longer!
            ## e.g.: http://lists.astropy.scipy.org/pipermail/astropy/2012-March/001904.html
            #erro_masked__ld = np.ma.masked_where(~mask__ld, (self._erro__ld * mask__ld) )
            #aux__ld = np.where(flag_replace, np.ma.median(erro_masked__ld, axis = 0), self._erro__ld)
            #aux__ld = np.where(np.isnan(aux__ld), np.median(self._erro__ld, axis=0), aux__ld)
            #self._erro__ld[flag_replace] = aux__ld[flag_replace]

            
    def collapsePixelDimensions(self, var__ld, Nl = None):
        '''
        Transform 3D arrays with dimensions __lyx into dimensions __lp (p = pixel).
        If given a 1D or 2D array, just return itself.
        '''
        if (Nl == None): Nl = self.Nl

        if (self.Nd != 2):
            var__lp = np.ma.resize( var__ld, (Nl, self.Npix) )
        else:
            var__lp = var__ld
            
        return var__lp

    
    def repackPixelDimensions(self, var__lp, Nl = None):
        '''
        Does the opposite of collapsePixelDimensions()
        '''
        if (Nl == None): Nl = self.Nl

        if (self.Nd == 3):
            var__ld = np.ma.resize( var__lp, (Nl, self.Ny, self.Nx) )
        elif (self.Nd == 1):
            var__ld = np.ma.resize( var__lp, (Nl) )
        else:
            var__ld = var__lp
        
        return var__ld

            
    def denormalize_spec(self, norm = 1.):
        '''
        Denormalize spec!
        '''

        self._spec__ld *= self._fnorm__d * self.fobs_norm / float(norm)
        self._erro__ld *= self._fnorm__d * self.fobs_norm / float(norm)
        self._fnorm__d /= self._fnorm__d
        self.fobs_norm = float(norm)
    
        #print self._spec__ld is self.spec__lyx
        #print self._erro__ld is self.erro__lyx
        #print self._fnorm__d is self.fnorm__yx
        
    def normalize_spec(self, ll, llow, lupp, normalize_by = None):
        '''
        Normalize each spec in a wavelength region
        '''

        if (ll == 'lobs'):
            _ll = WavelengthRange()
            llow = _ll.lobsToRestFrame(llow, self.redshift)
            lupp = _ll.lobsToRestFrame(lupp, self.redshift)

        if (normalize_by == None):
            _S, _N, SN, _rms_formal = self.calcSN(llow, lupp, calc_noise = False)
        else:
            _S = normalize_by

        _S = np.abs(_S)
        good_S = (_S > -990)

        if (self.Nd > 1):
            self._fnorm__d[good_S] = self._fnorm__d[good_S] * _S[good_S]
            self._spec__ld[:,good_S] = self._spec__ld[:,good_S] / _S[good_S]
            self._erro__ld[:,good_S] = self._erro__ld[:,good_S] / _S[good_S]

        if (self.Nd == 1):
            if (good_S):
                self._fnorm__d *= _S
                self._spec__ld /= _S
                self._erro__ld /= _S
            else:
                print "@@> Spec not normalized --- no good flux in S/N region (%s--%s AA)." %(llow, lupp)

        #plt.plot(self.spec__lyx[:,20:40,37])

        
    def __sub__(self, other):

        if ( (self.lrest - other.lrest).sum() != 0 ) & ( (self.lobs - other.lobs).sum() != 0 ):
            print "!!! WARNING !!!> You can only sum/subtract specs with the same wavelength range."
            sys.exit(1)

        else:

            #spec = (self.fobs_norm * self._fnorm__d * self._spec__ld) - (other.fobs_norm * other._fnorm__d * other._spec__ld)
            #erro = (self.fobs_norm * self._fnorm__d * self._erro__ld) + (other.fobs_norm * other._fnorm__d * other._erro__ld)

            fnorm_other2self = (other.fobs_norm * other._fnorm__d) / (self.fobs_norm * self._fnorm__d)
            
            spec = (self._spec__ld) - (other._spec__ld * fnorm_other2self)
            erro = (self._erro__ld) + (other._erro__ld * fnorm_other2self)

            flag = np.maximum(self._flag__ld, other._flag__ld)
            mask = (self._mask__d & other._mask__d)

        return self.__class__(spec, lobs = copy(self.lobs), lrest = copy(self.lrest),
                              redshift = copy(self.redshift), 
                              fobs_norm = copy(self.fobs_norm), fnorm_spatial = copy(self._fnorm__d),
                              flag = flag, erro = erro, mask = mask)

    def __add__(self, other):

        if ( (self.lrest - other.lrest).sum() != 0 ) & ( (self.lobs - other.lobs).sum() != 0 ):
            print "!!! WARNING !!!> You can only sum/subtract specs with the same wavelength range."
            sys.exit(1)

        else:

            #spec = (self.fobs_norm * self._fnorm__d * self._spec__ld) + (other.fobs_norm * other._fnorm__d * other._spec__ld)
            #erro = (self.fobs_norm * self._fnorm__d * self._erro__ld) + (other.fobs_norm * other._fnorm__d * other._erro__ld)

            spec = (self._spec__ld) + (other._spec__ld)
            erro = (self._erro__ld) + (other._erro__ld)

            flag = np.maximum(self._flag__ld, other._flag__ld)
            mask = (self._mask__d & other._mask__d)

        return self.__class__(spec, lobs = copy(self.lobs), lrest = copy(self.lrest),
                              redshift = copy(self.redshift),
                              fobs_norm = 1.,
                              flag = flag, erro = erro, mask = mask)
    
    def __div__(self, other):

        if ( (self.lrest - other.lrest).sum() != 0 ):
            print "!!! WARNING !!!> You can only sum/subtract specs with the same wavelength range."
            sys.exit(1)

        else:

            #spec = (self.fobs_norm * self._fnorm__d * self._spec__ld) / (other.fobs_norm * other._fnorm__d * other._spec__ld)
            #erro = (self.fobs_norm * self._fnorm__d * self._erro__ld) / (other.fobs_norm * other._fnorm__d * other._erro__ld)

            spec = (self._spec__ld) / mask_minus999( (other._spec__ld), thereshold = 0, fill = -999 )
            erro = (self._erro__ld) / mask_minus999( (other._erro__ld), thereshold = 0, fill = -999 )

            flag = np.maximum(self._flag__ld, other._flag__ld)
            mask = (self._mask__d & other._mask__d)

        return self.__class__(spec, lobs = copy(self.lobs), lrest = copy(self.lrest),
                              redshift = copy(self.redshift),
                              fobs_norm = 1.,
                              flag = flag, erro = erro, mask = mask)

    def __pow__(self, other):

        spec = self._spec__ld**other
        flag = self._flag__ld
        erro = self._erro__ld
        mask = self._mask__d

        return self.__class__(spec, lobs = copy(self.lobs), lrest = copy(self.lrest),
                              redshift = copy(self.redshift),
                              fobs_norm = 1.,
                              flag = flag, erro = erro, mask = mask)

    def resample(self, lresam, lorig = 'lrest', debug = False):
        if (lorig == 'lrest'): lor = self.lrest
        if (lorig == 'lobs' ): lor = self.lobs

        if (debug): print self._fnorm__d, self.fnorm, self.fobs_norm
            
        # Defined __r = resampled __l
        _ll = WavelengthRange()
        ResamM__rl = stutil.ReSamplingMatrixNonUniform( lor, lresam )
        dlorig  = lor[1]  - lor[0]
        dlresam = lresam[1] - lresam[0]
        R_dl = float(dlorig) / float(dlresam)
        #print ResamM__rl, lor, lresam, R_dl, dlorig, dlresam

        # Resampling spectra -- bad pixels are used in resampling!
        #--old--spec__rz = np.tensordot( ResamM__rl, self.spec__lz * self.mask__lz, (1,0) )
        spec__rd = np.tensordot( ResamM__rl, self._spec__ld * self._fnorm__d, (1,0) )
        #plt.clf()
        #plt.plot(self.lrest, self._spec__ld, '-x', color="blue")
        #plt.plot(lresam, spec__rd, '-o', color="orange")

        # Rebinning errors
        erro2__rd = np.tensordot( ResamM__rl, (self._erro__ld * self._fnorm__d)**2, (1,0) )
        llow = np.max( [np.min(lor), np.min(lresam)] )
        lupp = np.min( [np.max(lor), np.max(lresam)] )
        m__ld = (lor > llow) & (lor < lupp)
        m__rd = (lresam > llow) & (lresam < lupp)

        #e_norm = np.nansum(self._erro__ld[m__ld]**2 * dlorig, axis = 0) / np.nansum(erro2__rd[m__rd] * dlresam, axis = 0)

        erro__ld = np.ma.array( self._erro__ld, mask=( self._erro__ld < -990. ) )
        e_norm = np.ma.sum(erro__ld[m__ld]**2 * dlorig, axis = 0) / np.nansum(erro2__rd[m__rd] * dlresam, axis = 0)

        erro__rd = np.sqrt(e_norm * erro2__rd)
        #plt.clf()
        #plt.plot(lor, self._erro__ld, '-x', color="blue")
        #plt.plot(lresam, erro__rd, '-o', color="orange")

        if (debug): print self._fnorm__d, self.fnorm, self.fobs_norm

        # Create a spec1D
        if (lorig == 'lrest'):
            spec = self.__class__(spec__rd, lrest = lresam, erro = erro__rd, redshift = self.redshift, fobs_norm = self.fobs_norm)
        else:
            spec = self.__class__(spec__rd,  lobs = lresam, erro = erro__rd, redshift = self.redshift, fobs_norm = self.fobs_norm)


        # Add flags to spec0D
        if (self._flagType__ld):
            for id, (value, f__ld) in self._flagType__ld.items():
                update_spatial_mask = False
                if (id == "califa_flag"): update_spatial_mask = True
                f__rd = np.tensordot( ResamM__rl, f__ld, (1,0) )
                spec.add_flagType((f__rd > 0.3), flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)

        return spec

    
    def calcSN(self, llow, lupp, spatial_mask = True, flags_mask = True, debug = False, calc_noise = True):
        '''
        Calc S/N pixel by pixel, i.e.:
        - calc S/N for spec0D
        - calc S/N by region for spec1D
        - calc S/N pixel by pixel (S/N image) for spec2D
        '''

        _ima__ld = self._spec__ld.copy()
        _rms__ld = self._erro__ld.copy()

        # Masking can probably be made faster
        # Apply flags
        if (flags_mask):
            mask__ld = self.mask_lambda( "all", type_exclude = ["small_errors"] )
            _ima__ld[~mask__ld] = -999.
            _rms__ld[~mask__ld] = -999.
        
        # Apply spatial mask
        if (spatial_mask):
           _ima__ld = np.where(self._mask__d, _ima__ld, -999.)
           _rms__ld = np.where(self._mask__d, _rms__ld, -999.)

        # Mask in wavelength
        mask__l = (self.lrest >= llow) & (self.lrest <= lupp)
        _ima__ld = _ima__ld[mask__l]
        _rms__ld = _rms__ld[mask__l]
        _l = self.lrest[mask__l]
        
        # Create masked arrays --- mask -999
        _ima__ld = np.ma.masked_array( _ima__ld, mask = (_ima__ld < -990.) )
        _rms__ld = np.ma.masked_array( _rms__ld, mask = (_rms__ld < -990.) )

        # Calc S
        _S = np.ma.median(_ima__ld, axis = 0)


        if (calc_noise):

            # Calc detrended noise --- carefully using np.ma methods to treat masked arrays
            Nl = _ima__ld.shape[0]
            _ima__lp = self.collapsePixelDimensions(_ima__ld, Nl = Nl)
            
            # Note that ma.polyfits works with 2D arrays, but it was incredibly buggy when I tried (nan's everywhere),
            # thus the inelegant for-loop below
            a__p = np.zeros([self.Npix])
            b__p = np.zeros([self.Npix])
            for i in range(self.Npix):
                if ( Nl - _ima__lp.mask[:,i].sum() ) > 1 :
                    a__p[i], b__p[i] = np.ma.polyfit(_l, _ima__lp[:,i], 1)
            
            line__lp = a__p[np.newaxis, :] * _l[:, np.newaxis] + b__p[np.newaxis, :]
            _ima_detrend__ld = self.repackPixelDimensions(_ima__lp - line__lp, Nl = Nl)

            # Calc N
            _N = np.ma.std(_ima_detrend__ld, axis = 0)
            _rms_formal = np.ma.median(_rms__ld, axis = 0)

        else:
            _N = _S
            _rms_formal = _S
            
            
        # Calc S/N
        SN = np.ma.where( (_N > 0), _S / _N, -999.)
        SN = np.ma.where( _S == 0., 0., SN)
        SN[SN < -990.] = np.ma.masked

        if (debug):

            if (self.Nd == 2):
                print _rms__ld[:,0],  _rms__ld.mask[:,0]
                plt.clf()
                plt.plot(_S, 'o')
                plt.plot(_N, '.')
                plt.plot(SN, 'x')
                plt.plot(_rms_formal, '.')
                plt.plot(_N/_rms_formal, 'x', color="blue")

            if (self.Nd == 3):
                print _N[50,28]
                print _S[50,28]
                print SN[50,28]
                print _rms_formal[50,28], (_N / _rms_formal)[50,28]
                print (_N / _rms_formal)[34,34]
                print np.mean(_N / _rms_formal), np.median(_N / _rms_formal)
                plt.clf()
                plt.subplot(231)
                plt.imshow(_S, interpolation = "nearest", origin='lower')
                plt.title("F")
                plt.colorbar()
                plt.subplot(232)
                plt.imshow(_N, interpolation = "nearest", origin='lower')
                plt.title("rms")
                plt.colorbar()
                plt.subplot(233)
                plt.imshow(SN, interpolation = "nearest", origin='lower', vmin = 5, vmax = 50)
                plt.title("S/N")
                plt.colorbar()
                plt.subplot(234)
                plt.imshow(_rms_formal, interpolation = "nearest", origin='lower', vmin = 0, vmax = 0.010)
                plt.title("rms formal")
                plt.colorbar()
                plt.subplot(235)
                plt.imshow(_N / _rms_formal, interpolation = "nearest", origin='lower')
                #plt.imshow(_rms_formal/_N, interpolation = "nearest", vmin = 5, vmax = 50, origin='lower')
                plt.title("rms / rms formal")
                plt.colorbar()

                plt.subplot(236)
                _N2 = np.ma.std(_ima__ld, axis = 0)
                plt.imshow(_N / _N2, interpolation = "nearest", origin='lower')
                plt.title("rms detrended / rms non-detrended")
                plt.colorbar()

        # Fill up masked values with -999.
        _S = np.ma.asarray(_S).filled(-999.)
        _N = np.ma.asarray(_N).filled(-999.)
        SN = np.ma.asarray(SN).filled(-999.)
        _rms_formal = np.ma.asarray(_rms_formal).filled(-999.)            
                            
        return _S, _N, SN, _rms_formal

    
    def select_lambda(self, llow, lupp, update_spatial_mask_califa_flag = False):

        spec__ld = self._spec__ld.copy() * self._fnorm__d
        erro__ld = self._erro__ld.copy() * self._fnorm__d

        # Mask in wavelength
        mask__l = (self.lrest >= llow) & (self.lrest <= lupp)
        spec__ld = spec__ld[mask__l]
        erro__ld = erro__ld[mask__l]
        _l = self.lrest[mask__l]

        # Create a new specXD
        spec = self.__class__(spec__ld, lrest = _l, erro = erro__ld, mask = self._mask__d,
                              redshift = self.redshift, fobs_norm = self.fobs_norm)

        # Add flags to specXD
        if (self._flagType__ld):
            for id, (value, f__lz) in self._flagType__ld.items():
                # If we are using this routine as a faster way to calc S/N, the spatial mask should be left alone!
                update_spatial_mask = False
                if (id == "califa_flag"): update_spatial_mask = update_spatial_mask_califa_flag
                spec.add_flagType(f__lz[mask__l], flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)

        return spec

    

    def plot(self, normalize = False, normalize_by = None, 
             sort = None, sort_label = None,
             shade_error = False, mark_flagged = True,
             color_spec = "black", color_flagged = "red",
             offset = 0., lmin = None, lmax = None,
             lplot = 'lrest', linestyle = '-',
             **kwargs):
        '''
        Works for Spec0D and Spec1D, but not Spec2D yet
        '''
        
        if (normalize) & (normalize_by == None):
            self.normalize_spec('lrest', 5590., 5680.)

        if (normalize_by != None):
            self.normalize_spec('lrest', 5590., 5680., normalize_by = normalize_by)

        # Choose wavelength to plot
        if (lplot == 'lrest'):
            ll = self.lrest
        else:
            ll = self.lobs
            
        # Plot spec
        spec = self._spec__ld + offset
        plt.plot(ll, spec, color = color_spec, linestyle = linestyle, **kwargs)
        #ymin = spec.min()
        #ymax = spec.max()
        #plt.ylim(ymin, ymax)


        # Mark flagged data
        if (mark_flagged):
            flagged = np.ma.masked_where(self._flag__ld == 0, spec, **kwargs)
            plt.plot(ll, flagged, color = color_flagged)

        # Adjust lambda limits
        if (lmin == None): lmin = np.min(ll) - 20.
        if (lmax == None): lmax = np.max(ll) + 20.
        plt.xlim( lmin, lmax )

        # Plot errors
        if (shade_error):
            plt.fill_between(ll, self._spec__ld - self._erro__ld, self._spec__ld + self._erro__ld, facecolor='blue', alpha=0.5, **kwargs)

        # Plot sort
        if (sort != None) & (sort_label != None):
            isort = np.argsort( sort )
            for ispec, i in enumerate(isort):
                plt.annotate('%s = %.2f' % (sort_label, sort[i]) , xy=(ll[-1], spec[-1,ispec]), xytext=(0,0), 
                             textcoords='offset points', ha='center', va='bottom')


    def correctMWlaw(self, EBV, optionMWlaw, AV = False):
        '''
        Correct spec by MW extinction law
        '''

        # Calc q = A_lambda / A_V for each reddening law
        if (EBV > 0):
            if (optionMWlaw == 'CCM'):
                R_V = 3.1
                q_norm__ld = CCM_RedLaw(self.lobs, R_V)
            else:
                q_norm__ld = np.ones_like(self.lobs)

        if (AV):
            A_V = EBV
            EBV = A_V / R_V
        else:
            A_V = R_V * EBV

        # Fix q_norm__ld dimensions to be able to multiply by fobs
        if (self.Nd == 2):
            q_norm__ld = q_norm__ld[:, np.newaxis]
        elif (self.Nd == 3):
            q_norm__ld = q_norm__ld[:, np.newaxis, np.newaxis]

        f = (self._spec__ld > -990)
        #print f[:,].shape, self._spec__ld.shape, q_norm__ld.shape
        self._spec__ld[f] = (10**( 0.4 * A_V * q_norm__ld ) * self._spec__ld)[f]
        #f = self._spec__ld > -990
        #self.spec__lyx[f] = aux[f]
        
    
    def Kcorrect_Flux_1plusZ(self, Factor1plusZ = 1):
        '''
        K-correct fluxes by the cosmological factor.

          f = 0: No correction

        If using the luminosity distance DL:
          f = -1: F_nu
          f =  1: F_lambda
          
        If using the comoving transverse distance DM:
          f =  1: F_nu
          f =  3: F_lambda
        '''

        aux = self._spec__ld * (1 + self.redshift)**(Factor1plusZ)
        f = self._spec__ld > -990
        self._spec__ld[f] = aux[f]

        aux = self._erro__ld * (1 + self.redshift)**(Factor1plusZ)
        f = self._erro__ld > -990
        self._erro__ld[f] = aux[f]

        
    def total_flux(self, baseline = 0):
        '''
        Sum up flux in all spectra
        '''

        return np.sum( abs(self._spec__ld - baseline), axis = 0 )

    
        
class Spec0D(Spec):
    '''
    Spec0D: F_lambda(lambda)
    '''

    def __init__(self, spec = None, *args, **kwargs):
        if (spec != None):
            self._populate0d(spec, *args, **kwargs)

            
    def _populate0d(self, *args, **kwargs):
        super(Spec0D, self).__init__(*args, **kwargs)

        if (self.Nd == 1):
            self.spec__l = self._spec__ld
            self.flag__l = self._flag__ld
            self.flagType__l = self._flagType__ld
            self.erro__l = self._erro__ld
            self.mask    = self._mask__d
            self.fnorm   = self._fnorm__d
        else:
            print "!!! WARNING !!!> Your spec dimensions are wrong: expected 1 (__l), but got %s." % self.Nd
            sys.exit(1)

            
    def fromStarlightInputFile(self, cxtFile, specUnits = 1.e-16, redshift = 0.):
        t = atpy.Table(cxtFile, type='starlight_input')

        # Save spectra
        self._populate0d( t['flux'], lrest = t['lambda'], erro = t['error'], flag = t['flag'], 
                          fobs_norm = specUnits, redshift = redshift)

        
    def measureEW(self, lines_file = None, EWpars = None, ext_l = 20., large_window = False, debug = False):

        # Renaming things
        l = self.lrest
        spec = self.spec__l
        dl = np.zeros_like(l)
        dl[1:-1] = ( (l[2:] - l[1:-1]) + (l[1:-1] - l[0:-2]) )/2.
        dl[0]  = ( dl[1]  + (l[1] - l[0])   )/2.
        dl[-1] = ( dl[-2] + (l[-1] - l[-2]) )/2.
        
        # Init dictionaries
        try:
            self.EWpars
        except:
            self.EWpars = {}

        try:
            self.intF
        except:
            self.intF = {}
            
        try:
            self.intC
        except:
            self.intC = {}
            
        # Read lines file if user has not set the input EW parameters
        if (EWpars is None):
            EWpars = {}
            lines_params = read_lines_params(lines_file)
        
            for line_params in lines_params:

                line_name = line_params[0] 
                l_centre = line_params[1]
                ll_window = (l_centre - ext_l/2., l_centre + ext_l/2.)
                ll_blue_cont = (line_params[2], line_params[3])
                ll_red_cont  = (line_params[4], line_params[5]) 

                # Make central window larger; useful for absorption lines
                if large_window:
                    ll_window = (ll_blue_cont[1], ll_red_cont[0])

                EWpars[line_name] = l_centre, ll_window, ll_blue_cont, ll_red_cont

        # Plot stuff
        if debug:
            plt.plot(l, spec, color = 'black')

            
        # Calc integrated flux & continuum 
        for line_name in EWpars:

            l_centre     = EWpars[line_name][0]
            ll_window    = EWpars[line_name][1]
            ll_blue_cont = EWpars[line_name][2]
            ll_red_cont  = EWpars[line_name][3]

            # Get flux spectrum in the central line window
            f_line = (l >= ll_window[0]) & (l <= ll_window[1])
            L = f_line * spec

            # Get median continuum on the blue and red sides
            f_cont_red = (l > ll_red_cont[0]) & (l <= ll_red_cont[1])
            if (sum(f_cont_red) > 0):
                cont_red = np.median(spec[f_cont_red])
                Cr = f_cont_red * cont_red
            else:
                cont_red = -999.
                Cr = cont_red + np.zeros_like(l)
                
            f_cont_blue = (l >= ll_blue_cont[0]) & (l < ll_blue_cont[1])        
            if (sum(f_cont_blue) > 0):
                cont_blue = np.median(spec[f_cont_blue])
                Cb = f_cont_blue * cont_blue
            else:
                cont_blue = -999.
                Cb = cont_blue + np.zeros_like(l)

            # Connect the blue and red continua
            if (cont_red > -999.) & (cont_blue > -999):
                y1 = cont_blue
                y2 = cont_red
                x1 = np.median(l[f_cont_blue])
                x2 = np.median(l[f_cont_red])
                a = (y2 - y1) / (x2 - x1)
                b = y1 - a * x1
                C = a * l + b
                if (sum(f_line) > 0):
                    C[~f_line] = 0.
            else:
                C = -999. + np.zeros_like(l)
             
            # Calc flux & continuum
            if (cont_red > -999.) & (cont_blue > -999):
                intF = sum(dl * (L - C))
                intC = (cont_red + cont_blue) / 2.
            else:
                intF = -999.
                intC = -999.

            if np.isnan(intF): intF = -999.
            if np.isnan(intC): intC = -999.

            self.intF[line_name] = intF
            self.intC[line_name] = intC
            self.EWpars[line_name] = l_centre, ll_window, ll_blue_cont, ll_red_cont


            if debug:
                print l_centre, intF, intC
                plt.plot(l[f_line], L[f_line], color = 'orange', linestyle = 'steps-mid')
                #plt.plot( [x1, x2], [y1, y2], '.-', color='red' )
                plt.plot(l, Cb, color = 'blue', linestyle = 'steps-mid')
                plt.plot(l, Cr, color = 'red', linestyle = 'steps-mid')
                plt.plot(l, C,  color = 'yellow', linestyle = 'steps-mid')

                
    def extendSpecUniform(self, spec, lor, lre):
        '''
        Extend or cut spectrum at the ends, assuming lorig and lresam are
        uniformily sampled.
        '''

        spec__r = np.zeros_like(lre)

        ff__r = (lre >= lor[0]) & (lre <= lor[-1])
        ff__o = (lor >= lre[0]) & (lor <= lre[-1])
        spec__r[ff__r] = spec[ff__o]

        ff = (lre < lor[0])
        if (sum(ff) > 0):
            spec__r[ff] = spec[0]

        ff = (lre > lor[-1])
        if (sum(ff) > 0):
            spec__r[ff] = spec[-1]

        return spec__r

    
    def interpFlaggedSpec(self, flag = None):
        '''
        Replace points in flagged spec by interpolated values.
        '''
        spec = self.spec__l.copy()

        if (flag is not None):
            if (sum(flag) > 0):
                if (sum(~flag) > 1):
                    spec[flag] = np.interp(self.lrest[flag], self.lrest[~flag], self.spec__l[~flag])
                else:
                    spec = np.zeros_like(spec)

        return spec

    
    def boxFilter_lambda(self, ext_l, debug = False, flag = False, lrest_unif = True):
        
        # Remove flagged fluxes by interpolating spectrum
        if flag:
            ff = (self.flag__l == 1)
        else:
            ff = None
        spec = self.interpFlaggedSpec(ff)
        
        # Extend spectrum at the endings
        lor  = self.lrest
        _dl  = 6. * int(ext_l)
        lre = np.arange( (lor[0] - _dl), (lor[-1] + _dl + 1), (lor[1] - lor[0]) )
        if lrest_unif:
            spec__r = self.extendSpecUniform(spec, lor, lre)
        else:
            matrix = stutil.ReSamplingMatrixNonUniform(lor, lre, extrap = True)
            spec__r = np.dot(matrix, spec)

        dl = (lre[1] - lre[0])
        l = np.arange( min(-2*dl, -2*ext_l), max(2*dl+1, 2*ext_l + 1), dl )
        box__l = np.zeros_like(l)
        fbox__l = np.abs(l) < np.abs(0.5 * ext_l)
        box__l[fbox__l] = 1.
        scon__r = np.convolve(spec__r,  box__l, 'same') / ext_l

        if (debug):
            plt.clf()
            plt.plot(self.lrest, self.spec__l, color='red')
            plt.plot(lre, spec__r, color='blue')
            plt.plot(lre, scon__r, color='black')

            plt.figure(2)
            plt.clf()
            plt.plot(l, box__l)
            print ext_l

            
        # Resample spec into old lambda range
        if lrest_unif:
            scon__l = self.extendSpecUniform(scon__r, lre, lor)
        else:
            matrix = stutil.ReSamplingMatrixNonUniform(lre, lor)
            scon__l = np.dot(matrix, scon__r)

        fobs_norm = np.median(self._fnorm__d)
        _fnorm__d = self._fnorm__d / fobs_norm
        
        return self.__class__(scon__l, lrest = copy(self.lrest), 
                              redshift = copy(self.redshift), 
                              fobs_norm = fobs_norm, fnorm_spatial = _fnorm__d)

    
    def gaussianFilter_lambda(self, fwhm_l, FWHM = True, debug = False, flag = False, lrest_unif = True):
        '''
        Return a gaussian smoothed spectrum by sig_l [angstroms].

        Note: assumes homogenous lambda!
        '''

        # Remove flagged fluxes by interpolating spectrum
        if flag:
            ff = (self.flag__l == 1)
        else:
            ff = None
        spec = self.interpFlaggedSpec(ff)
        #plt.plot(self.lrest, spec, color = 'yellow')
            
        # Calculate sigma 
        if (FWHM):
            sig_l = fwhm_l / (2 * np.sqrt(2 * np.log(2)))
        else:
            sig_l = fwhm_l
            fwhm_l = sig_l * (2 * np.sqrt(2 * np.log(2)))

            
        # Extend spectrum at the endings
        lor  = self.lrest
        _dl = 6. * int(fwhm_l)
        lre = np.arange( (lor[0] - _dl), (lor[-1] + _dl + 1), (lor[1] - lor[0]) )
        if lrest_unif:
            spec__r = self.extendSpecUniform(spec, lor, lre)
        else:
            matrix = stutil.ReSamplingMatrixNonUniform(lor, lre, extrap = True)
            spec__r = np.dot(matrix, spec)
        
        dl = (lre[1] - lre[0])
        l = np.arange( min(-2*dl, -5*sig_l), max(2*dl+1, 5*sig_l + 1), dl )
        amp = 1. / (sig_l * np.sqrt(2. * np.pi))
        gauss = dl * amp * np.exp( -0.5 * (l / sig_l)**2 )
        scon__r = np.convolve(spec__r,  gauss, 'same')

        
        if (debug):
            plt.clf()
            plt.plot(self.lrest, self.spec__l, color='red')
            plt.plot(lre, spec__r, color='blue')
            plt.plot(lre, scon__r, color='black')

            plt.figure(2)
            plt.clf()
            plt.plot(l, gauss)
            print sig_l

            
        # Resample spec into old lambda range
        if lrest_unif:
            scon__l = self.extendSpecUniform(scon__r, lre, lor)
        else:
            matrix = stutil.ReSamplingMatrixNonUniform(lre, lor)
            scon__l = np.dot(matrix, scon__r)

            
        #fobs_norm = np.median(self._fnorm__d)
        #_fnorm__d = self._fnorm__d / fobs_norm
        fobs_norm = self.fobs_norm
        _fnorm__d = self._fnorm__d
       

        return self.__class__(scon__l, lrest = copy(self.lrest), 
                              redshift = copy(self.redshift), 
                              fobs_norm = fobs_norm, fnorm_spatial = _fnorm__d)
    
    
    def gaussianFilter_velocity(self, fwhm_v, FWHM = True, debug = False):
        '''
        WARNING: More tests needed --- it seems the rebin makes the lines shift a little to the red
        
        Return a gaussian smoothed spectrum by sig_v [km/s].
        '''

        dv = 50.
        
        # Resample spec into d ln lambda
        lor  = self.lrest
        lre = np.exp( np.arange( np.log(lor[0] - 100), np.log(lor[-1] + 101), dv/c_light ) )        
        matrix = stutil.ReSamplingMatrixNonUniform(lor, lre, extrap = True)
        spec__r = np.dot(matrix, self.spec__l)

        # Convolve
        if (FWHM):
            sig_v = fwhm_v / (2 * np.sqrt(2 * np.log(2)))
        else:
            sig_v = fwhm_v
            fwhm_v = sig_v * (2 * np.sqrt(2 * np.log(2)))

            
        v = np.arange( min(-2*dv, -6*sig_v), max(2*dv+1, 6*sig_v + 1), dv )
        amp = 1. / (sig_v * np.sqrt(2. * np.pi))
        gauss = dv * amp * np.exp( -0.5 * (v / sig_v)**2 )
        scon__r = np.convolve(spec__r,  gauss, 'same')

        
        # Resample spec into lambda again
        matrix = stutil.ReSamplingMatrixNonUniform(lre, lor)
        scon__l = np.dot(matrix, scon__r)

        
        if (debug):
            #lre  = np.linspace( lor[0], lor[-1]+.5, 2*len(lor) )
            #print lor[338:], lre[586:]
            plt.clf()
            plt.plot( lor, self.spec__l, marker='x' )
            plt.plot( lre, spec__r, marker='.' )
            plt.plot( lor, scon__l, marker='+' )

            matrix = stutil.ReSamplingMatrixNonUniform(lre, lor)
            spec__l = np.dot(matrix, spec__r)
            plt.plot( lor, spec__l, marker='+' )
            print np.trapz(self.spec__l, lor), np.trapz(spec__r, lre), np.trapz(spec__l, lor)

            
        return self.__class__(scon__l, lrest = lor, 
                              redshift = copy(self.redshift), 
                              fobs_norm = copy(self.fobs_norm))

    

    def toSpec1D(self, redshift = None):

        if (redshift == None):
            redshift = self.redshift
            
        # Create a spec1D
        s1d = Spec1D(self.spec__l[:,np.newaxis], lrest = self.lrest, lobs = self.lobs, redshift = redshift,
                     erro = self.erro__l[:,np.newaxis], fobs_norm = 1., fnorm_spatial = [self.fobs_norm * self.fnorm])

        # Add flags to spec0D
        if (self.flagType__l):
            for id, (value, f__l) in self.flagType__l.items():
                update_spatial_mask = False
                if (id == "califa_flag"): update_spatial_mask = True
                s1d.add_flagType(f__l[:,np.newaxis], flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)
    
        return s1d

        
class Spec1D(Spec):
    '''
    Spec1D: F_lambda(lambda, z)
    '''

    def __init__(self, *args, **kwargs):
        Spec.__init__(self, *args, **kwargs)
     
        if (self.Nd == 2):
            self.spec__lz = self._spec__ld
            self.flag__lz = self._flag__ld
            self.flagType__lz = self._flagType__ld
            self.erro__lz = self._erro__ld
            self.mask__z  = self._mask__d
            self.fnorm__z = self._fnorm__d
        else:
            print "!!! WARNING !!!> Your spec dimensions are wrong: expected 2 (__lz), but got %s." % self.Nd
            sys.exit(1)


    def addZone(self, s0d):

        self.spec__lz = np.concatenate((self.spec__lz, s0d.spec__l[:, np.newaxis]), axis = 1)
        self.erro__lz = np.concatenate((self.erro__lz, s0d.erro__l[:, np.newaxis]), axis = 1)
        self.flag__lz = np.concatenate((self.flag__lz, s0d.flag__l[:, np.newaxis]), axis = 1)
        self.fnorm__z = np.concatenate((self.fnorm__z, [s0d.fnorm]), axis = 0)
        self.mask__z  = np.concatenate((self.mask__z , [s0d.mask]),  axis = 0)

        # Fix parent arrays
        self._spec__ld = self.spec__lz
        self._erro__ld = self.erro__lz
        self._flag__ld = self.flag__lz
        self._fnorm__d = self.fnorm__z
        self._mask__d  = self.mask__z
        self.Ny = self._spec__ld.shape[1]
        self.Npix = self.Ny * self.Nx

        
    def toSpec0D(self, Nz = 0):

        # Create a spec0D
        s0d = Spec0D(self.spec__lz[:,Nz], lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = self.erro__lz[:,Nz], fobs_norm = self.fobs_norm)

        # Add flags to spec0D
        if (self.flagType__lz):
            for id, (value, f__lz) in self.flagType__lz.items():
                update_spatial_mask = False
                if (id == "califa_flag"): update_spatial_mask = True
                s0d.add_flagType(f__lz[:,Nz], flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)
    
        return s0d

    def stack(self, flag = None, fix_npix = False, debug = False):

        if (flag == None): flag = np.ones( [self.Ny], bool )

        if fix_npix:
            # Calc number of good pixels for each lambda (to be used as a weight to sum spec and errors)
            NpixTotal = len(flag)
            NpixGood__l = (self.spec__lz[:, flag] > 0).sum(axis = 1)
            fracGood__l = np.float_( NpixGood__l ) / NpixTotal
        else:
            fracGood__l = 1.

        #spec__l = np.sum(self.spec__lz[:, flag], axis = 1)
        spec__l = np.nansum(self.spec__lz[:, flag], axis = 1) / (fracGood__l + (fracGood__l == 0))
        erro__l = np.sqrt(np.sum(self.erro__lz[:, flag]**2, axis = 1))
        
        # Create a spec0D
        s0d = Spec0D(spec__l, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = erro__l, fobs_norm = self.fobs_norm)

        # Add flags to spec0D - TO DO

        if debug:
            plt.plot(self.lobs, fracGood__l, color="red")
        
        return s0d

    
    def stack_sqr(self):

        spec__l = np.sum(self.spec__lz**2, axis = 1)
        erro__l = np.sum(self.erro__lz**2, axis = 1)
        
        # Create a spec0D
        s0d = Spec0D(spec__l, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = erro__l, fobs_norm = self.fobs_norm)

        # Add flags to spec0D - TO DO
    
        return s0d
    
    def median(self):

        self.percentile(50)
        '''
        spec__l = np.median(self.spec__lz, axis = 1)
        erro__l = np.median(self.erro__lz, axis = 1)
        
        # Create a spec0D
        s0d = Spec0D(spec__l, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = erro__l, fobs_norm = self.fobs_norm)

        # Add flags to spec0D - TO DO
    
        return s0d
        '''

    def percentile(self, p):

        spec__l = np.percentile(self.spec__lz, p, axis = 1)
        erro__l = np.percentile(self.erro__lz, p, axis = 1)
        
        # Create a spec0D
        s0d = Spec0D(spec__l, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = erro__l, fobs_norm = self.fobs_norm)

        # Add flags to spec0D - TO DO
    
        return s0d

    
    def calibrate(self, calib__l):

        spec__lz = self.spec__lz * calib__l[:, np.newaxis]
        
        # Create a new spec1D
        s1d = self.__class__(spec__lz, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift,
                     erro = self.spec__lz, fobs_norm = self.fobs_norm)

        return s1d

        
    def plot_zone(self, Nz = 0, **kwargs):

        s0d = self.toSpec0D(Nz = Nz)
        s0d.plot(**kwargs)

        
    def plot_all(self, make_offset = True, offset_tuning = 2.,
                 sort = None, sort_label = None,
                 normalize = True, normalize_by = None, 
                 shade_error = False, mark_flagged = False,
                 color_spec = "black", color_flagged = "red",
                 lmin = None, lmax = None, lplot='lrest'):

        if (make_offset):
            offset = np.arange(self.Npix) * offset_tuning
        else:
            offset = 0.

        s1d = self
        
        if (sort != None):
           isort = np.argsort( sort ) 
           spec = self.spec__lz[:, isort]
           erro = self.erro__lz[:, isort]
           flag = self.flag__lz[:, isort]
           s1d = Spec1D(spec, lrest = self.lrest, erro = erro, flag = flag) 
            
        s1d.plot(normalize = normalize, normalize_by = normalize_by,
             shade_error = shade_error, mark_flagged = mark_flagged,
             color_spec = color_spec, color_flagged = color_flagged,
             offset = offset, lmin = lmin, lmax = lmax,
             sort = sort, sort_label = sort_label, lplot = lplot)
        

class Spec2D(Spec):
    '''
    Spec2D: F_lambda(lambda, y, x)
    '''

    def __init__(self, spec = None, *args, **kwargs):

        if (spec != None):
            self._populate2d(spec, *args, **kwargs)
            
        '''
        else:
            super(Spec2D, self).__init__(spec, *args, **kwargs)
        '''
        
    def _populate2d(self, *args, **kwargs):
        super(Spec2D, self).__init__(*args, **kwargs)
        #Spec.__init__(self, *args, **kwargs)

        if (self.Nd == 3):
            self.spec__lyx = self._spec__ld
            self.flag__lyx = self._flag__ld
            self.flagType__lyx = self._flagType__ld
            self.erro__lyx = self._erro__ld
            self.mask__yx  = self._mask__d
            self.fnorm__yx = self._fnorm__d
        else:
            print "!!! WARNING !!!> Your spec dimensions are wrong: expected 3 (__lyz), but got %s." % self.Nd
            sys.exit(1)

                
    def readCalifaFitsFile(self, fitsFile, headerOnly = False):

        # Read fits file
        self.fitsFile = fitsFile
        dataHDU = astropy.io.fits.open(fitsFile, memmap = True)
        self.fitsHeader = dataHDU[0].header

        if (not headerOnly):
            spec__lyx = dataHDU[0].data
            erro__lyx = dataHDU[1].data
            flag__lyx = dataHDU[3].data

        dataHDU.close()

        if (not headerOnly):
            return spec__lyx, erro__lyx, flag__lyx

    
    def lobsFromFitsHeader(self):
        
        # Define array for observed wavelengths
        pix_ref = self.fitsHeader['CRPIX3']
        lref = self.fitsHeader['CRVAL3']
        dl   = self.fitsHeader['CDELT3']
        Nl   = self.fitsHeader['NAXIS3']
        _ll = WavelengthRange()
        lobs = _ll.fromFits(pix_ref = pix_ref, lref = lref, dl = dl, Nl = Nl)

        return lobs

    
    def redshiftFromFitsHeader(self):
        # Get redshift
        syst_vel_key_v500 = 'HIERARCH V500 MED_VEL'
        syst_vel_key = 'MED_VEL'

        if syst_vel_key_v500 in self.fitsHeader:
            vel = self.fitsHeader[syst_vel_key_v500]
        elif syst_vel_key in self.fitsHeader:
            vel = self.fitsHeader[syst_vel_key]
            print '!!> Using redshift from %s header keyword instead of %s.' % (syst_vel_key, syst_vel_key_v500)
        else:
            vel = 0.
            print '!!! WARNING !!!> No redshift found on fits file (%s); using z = 0.' % self.fitsFile

        a = cdist.distance()
        redshift = a.redshift_from_velocity(vel)

        return redshift

    
    def nameFromFitsHeader(self, namekey = 'OBJECT'):
        # Get object name
        name = None
        if namekey in self.fitsHeader:
            name = re.sub('.*_', '', self.fitsHeader[namekey])

        return name

    
    def comb2v500Fix(self, comb2v500FixFile, spec__lyx, erro__lyx, flag__lyx):
        # Fixing COMBO data to match V500

        # Test if fix file exists. Create it otherwise.
        if not os.path.exists(comb2v500FixFile):
            from califautils import mapCOMBtoV500
            mapCOMBtoV500.run_main(dir = os.path.basename(comb2v500FixFile))

        if not os.path.exists(comb2v500FixFile):
            print 'Could not create or find file %s to match COMB data to V500. Exiting.' % comb2v500FixFile
            sys.exit(1)

        tc = atpy.Table(comb2v500FixFile, type="ascii")
        ydiff  = tc['ydiff'][0]
        xdiff  = tc['xdiff'][0]
        ydiff2 = tc['ydiff2'][0]
        xdiff2 = tc['xdiff2'][0]

        mask__yx = np.ones_like(spec__lyx[0])

        spec__lyx, erro__lyx, flag__lyx, mask__yx = CalifaMatchCombData(ydiff, xdiff, ydiff2, xdiff2, spec__lyx, erro__lyx, flag__lyx, _mask__yx)

        return spec__lyx, erro__lyx, flag__lyx, mask__yx

    
    def califaFits2spec2d(self, fitsFile, specUnits = 1.e-16, califa_flag = 11,
                           maskFile = None, comb2v500Fix = False, comb2v500FixFile = None,
                           shiftToRestframe = True):

        # Getting info from fits file        
        # Bad pixels are originally flagged with == 1. We use the flag == 11 for those.
        spec__lyx, erro__lyx, flag__lyx = self.readCalifaFitsFile(fitsFile)
        lobs = self.lobsFromFitsHeader()
        redshift = self.redshiftFromFitsHeader()
        name = self.nameFromFitsHeader('OBJECT')

        # No shifting to restframe
        if not shiftToRestframe:
            redshift = 0.
            print '!!! WARNING !!!> No restframe shift will be applied due to parameter shiftToRestframe = %s.' % shiftToRestframe
            
        # Define spatial mask
        # Here we use: mask = 1 --> pixel is OK, mask = 0 --> pixel should be masked out.
        if (maskFile == None):
            mask__yx = np.ones_like(spec__lyx[0])
        else:
            # Open Ruben's spatial mask. Ruben's def: every pixel above 0 should be masked.
            maskHDU = astropy.io.fits.open(maskFile)
            mask__yx = (maskHDU[0].data <= 0)
            maskHDU.close()

        # Fixing COMBO data to match V500
        if comb2v500Fix:
            spec__lyx, erro__lyx, flag__lyx, _mask__yx = self.comb2v500Fix(comb2v500FixFile, spec__lyx, erro__lyx, flag__lyx)
            # Save original mask from being fiddled with
            if (maskFile == None):
                mask__yx = _mask__yx

        # Save spectra
        self._populate2d( spec__lyx, lobs = lobs, erro = erro__lyx, fobs_norm = specUnits,
                        flagType = flag__lyx, flagType_id = 'califa_flag', flagType_value = califa_flag,
                        mask = mask__yx, redshift = redshift, name = name )
        
        
    def toImageBoxFilter(self, llow, lupp, spatial_mask = True, debug = False):

        _ima__lyx = self.spec__lyx.copy()
        _ima__lyx[(self.flag__lyx > 0)] = 0.
        _ima__lyx = _ima__lyx[(self.lrest >= llow) & (self.lrest <= lupp), :, :]
        
        # Apply spatial mask
        if (spatial_mask):
            _ima__lyx = np.where(self.mask__yx, _ima__lyx, -999.)
            
        _ima__yx = np.ma.sum( np.ma.array( _ima__lyx, mask=( _ima__lyx < -990.) ), axis =0 )
                    
        if (debug):
            import random
            plt.figure(random.randint(1, 1000))
            plt.clf()
            plt.imshow(_ima__yx)
            plt.colorbar()
            
        return Image(_ima__yx)


        
    def toSpec1D(self, segCube__zyx = None, segMap__yx = None, beta_error = None, beta_array = None,
                 llow_SN = 5590., lupp_SN = 5680., force_sum_spec0d = False, debug = False):

        if (segCube__zyx != None) and (segMap__yx != None):
            print "!!! WARNING !!!> You need to give either a seg cube or map, not both."
            sys.exit(1)

        if (segCube__zyx == None) and (segMap__yx == None):
            print "!!! WARNING !!!> You need to give either a seg cube or map."
            sys.exit(1)

        if (segMap__yx != None):
            segM = segMap(segMap__yx)
            segCube__zyx = segM.toSegCube().segCube__zyx


        # Create empty arrays for spec, error & flags
        Nzones = len(segCube__zyx)
        specZones__lz = np.zeros( [self.Nl, Nzones] ) -999.
        erroZones__lz = np.zeros( [self.Nl, Nzones] ) -999.
        flagTypeZones__lz = {}
        if (self.flagType__lyx):
            for id, (value, f__lyx) in self.flagType__lyx.items():
                flagTypeZones__lz[id] = [value, np.zeros([self.Nl, Nzones], dtype = 'bool') ]


        # Separate zones with single spaxels from the rest
        Npix__z = ( segCube__zyx * self.mask__yx ).sum( axis = (1,2) )
        singleSpax__z = (Npix__z == 1)
        multSpax__z   = (Npix__z >  1)

        
        # Simply reshape the single spaxels from 2d to 1d (note we are not summing errors in quadrature, since this calculation is only valid for single spaxels anyway)
        segmask__zyx = segCube__zyx * self.mask__yx
        specZones__lz = np.tensordot(self.spec__lyx * self.fnorm__yx, segmask__zyx, axes=([1,2],[1,2]))
        erroZones__lz = np.tensordot(self.erro__lyx * self.fnorm__yx, segmask__zyx, axes=([1,2],[1,2]))


        # Creating flags: note that this is correct even for summed spaxels
        NpixTotal__z = segmask__zyx.sum(axis=(1,2))

        # Sum flags: if a flag is in > 50% of the spaxels for a given lambda, it is propagated
        if (self.flagType__lyx):
            for id, (value, f__lyx) in self.flagType__lyx.items():
                if debug:
                    print 'Added flag ', id, value
                NpixFlagged__lz = np.tensordot(np.float_(f__lyx), np.float_(segmask__zyx), axes=([1,2],[1,2]))
                fracFlagged__lz = np.float_( NpixFlagged__lz ) / NpixTotal__z
                f__lz = (fracFlagged__lz > 0.5)
                flagTypeZones__lz[id][1] = f__lz

        # TO DO: Test when it is faster to do (1) one by one and when it is (2) better to do numpyt sums.
        # There must be a number of multSpax__z where it is best to do (1) rather than (2)
                
                        
        # Sum up spec, erro & flags for each zone, one by one
        #for _iz in range(0, Nzones):
        if force_sum_spec0d:
            for _iz in np.arange(len(multSpax__z))[multSpax__z]:
                #print _iz
                maskZone__yx = segCube__zyx[_iz, :, :]
                beta = 1.
                if (beta_array != None): beta = beta_array[_iz]
                specZone = self.toSpec0D(maskZone__yx = maskZone__yx, beta_error = beta_error, beta = beta, debug = debug)
                specZones__lz[:, _iz] = specZone.spec__l
                erroZones__lz[:, _iz] = specZone.erro__l
                if (specZone.flagType__l):
                    for id, (value, f__l) in specZone.flagType__l.items():
                        flagTypeZones__lz[id][1][:, _iz] = f__l

        # Sum zones with multiple spaxels using np tricks 
        else:
            
            # Select zones w that have more than one spaxel to be summed up
            segmask__wyx = segmask__zyx[multSpax__z]
            
            # Pixels not to be added: everything is considered good, except for pixels flagged by CALIFA calibration
            maskFlag__lyx = self.mask_lambda( ["califa_flag"] )
            
            # Calc number of good pixels for each lambda (to be used as a weight to sum spec and errors)
            NpixGood__lw = np.tensordot(np.float_(maskFlag__lyx), segmask__wyx, axes=([1,2],[1,2]))
            fracGood__lw = np.float_( NpixGood__lw ) / Npix__z[multSpax__z]
            
            # Sum spec
            _aux_good__lw = np.tensordot(self.spec__lyx * self.fnorm__yx * np.float_(maskFlag__lyx), segmask__wyx, axes=([1,2],[1,2])) / (fracGood__lw + (fracGood__lw == 0))
            _aux_bad__lw  = np.tensordot(self.spec__lyx * self.fnorm__yx, segmask__wyx, axes=([1,2],[1,2]))
            spec__lw = np.where( fracGood__lw > 0, _aux_good__lw, _aux_bad__lw)
            
            # Save to spec array
            specZones__lz[:, multSpax__z] = spec__lw
            
            # Sum error in quadrature
            np.seterr(invalid='raise') 
            _aux_good__lw = np.sqrt( np.tensordot( (self.erro__lyx * self.fnorm__yx)**2 * np.float_(maskFlag__lyx), segmask__wyx, axes=([1,2],[1,2])) ) / (fracGood__lw + (fracGood__lw == 0))
            _aux_bad__lw  = np.sqrt( np.tensordot( (self.erro__lyx * self.fnorm__yx)**2, segmask__wyx, axes=([1,2],[1,2])) )
            erro__lw = np.where( fracGood__lw > 0, _aux_good__lw, _aux_bad__lw)

            # Save to error array
            erroZones__lz[:, multSpax__z] = erro__lw


        if self.debug:
            plt.figure(1)
            plt.clf()
            plt.plot(self.lrest, spec__lw, 'b', label = 'new sum')
            plt.plot(self.lrest, specZone.spec__l, 'r', label = 'sum spec0d')
            plt.legend()
        
            plt.figure(2)
            plt.clf()
            plt.plot(self.lrest, erro__lw, 'b', label = 'new sum')
            plt.plot(self.lrest, specZone.erro__l, 'r', label = 'sum spec0d')
            plt.legend()
        
            plt.figure(3)
            plt.clf()
            plt.plot(self.lrest, specZone.flagType__l['sky_lines'][1], 'b', label = 'new sum')
            plt.plot(self.lrest, flagTypeZones__lz['sky_lines'][1][:, 0], 'r', label = 'sum spec0d')
            plt.legend()

            plt.figure(4)
            plt.clf()
            plt.plot(self.lrest, specZone.flagType__l['small_errors'][1], 'b', label = 'new sum')
            plt.plot(self.lrest, flagTypeZones__lz['small_errors'][1][:, 0], 'r', label = 'sum spec0d')
            plt.legend()

            plt.figure(5)
            plt.clf()
            plt.plot(self.lrest, specZone.flagType__l['big_errors'][1], 'b', label = 'new sum')
            plt.plot(self.lrest, flagTypeZones__lz['big_errors'][1][:, 0], 'r', label = 'sum spec0d')
            plt.legend()

            plt.figure(6)
            plt.clf()
            plt.plot(self.lrest, specZone.flagType__l['califa_flag'][1], 'b', label = 'new sum')
            plt.plot(self.lrest, flagTypeZones__lz['califa_flag'][1][:, 0], 'r', label = 'sum spec0d')
            plt.legend()

            
                    
        # Create a spec1D
        s1d = Spec1D(specZones__lz, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift, erro = erroZones__lz, fobs_norm = self.fobs_norm)

        # Add flags to spec1D
        if (flagTypeZones__lz):
            for id, (value, f__lz) in flagTypeZones__lz.items():
                update_spatial_mask = False
                if (id == "califa_flag"): update_spatial_mask = True
                s1d.add_flagType(f__lz, flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)

        # Function to correct correlated errors
        if (beta_array != None):
            if (debug): print "@@> Using beta given as parameter                             (Npix = %s, beta = %s)." % (NpixTotal__z, beta_array)

        if (beta_array == None) & (beta_error == 'califa_newbeta'):
            beta_array = califa_newbeta(s1d, llow_SN, lupp_SN)
            if (debug): print "@@> Using beta for correlated errors for CALIFA / new beta    (Npix = %s, beta = %s)." % (NpixTotal__z, beta_array)
                
        if (beta_array == None) & (beta_error == 'califa_voronoi_IAA'):
            beta_array = califa_voronoi_IAA_beta_error(NpixTotal__z)
            if (debug): print "@@> Using beta for correlated errors for CALIFA / Voronoi IAA (Npix = %s, beta = %s)." % (NpixTotal__z, beta_array)

        # Correct error by correlated error function
        if (beta_array != None):
            s1d.erro__lz[multSpax__z] *= beta_array[multSpax__z]
                
        return s1d


    def toSpec0D(self, maskZone__yx = None, beta_error = None, beta = 1.,
                 llow_SN = 5590., lupp_SN = 5680., debug = False):
        '''
        Sum up specs for a given zone.
        
        Note: I have tested if it would be best to do all zones together (directly to Spec1D), but it quickly gets out of hand,
        probably because numpy creates huge arrays in memory. For example:

            a__lz = np.nansum( self.spec__lyx[:, np.newaxis, :, :] * maskFlag__lyx[:, np.newaxis, :, :] * maskEff__zyx[np.newaxis, :, :, :], axis = (1, 2) )

        This takes 1.2 s for 5 zones, but 73.8 s for 10 zones!
        '''

        # Create zone mask, if none given
        if (maskZone__yx == None): maskZone__yx = np.ones_like( self.mask__yx, dtype = 'bool' )

        # Effective mask: combine zone mask and global spatial mask
        maskEff__yx = maskZone__yx * self.mask__yx

        # Pixels not to be added: everything is considered good, except for pixels flagged by CALIFA calibration
        maskFlag__lyx = self.mask_lambda( ["califa_flag"] )
        #maskFlag__lyx = self.mask_lambda( "all", type_exclude = ["small_errors"] )

        # Calc total number of pixels in zone
        NpixTotal = maskEff__yx.sum()
        
        if (NpixTotal <= 0):

            spec__l = np.zeros(self.Nl)
            erro__l = np.ones(self.Nl)

        elif (NpixTotal == 1):

            spec__l = (self.spec__lyx * self.fnorm__yx)[:, maskEff__yx][:, 0]
            erro__l = (self.erro__lyx * self.fnorm__yx)[:, maskEff__yx][:, 0]

        else:
            
            # Calc number of good pixels for each lambda (to be used as a weight to sum spec and errors)
            NpixGood__l = (maskEff__yx * maskFlag__lyx).sum(axis = (1,2))
            fracGood__l = np.float_( NpixGood__l ) / NpixTotal
            
            # Sum spec
            #spec__l = np.nansum( (self.spec__lyx * maskFlag__lyx * maskEff__yx), axis = (1, 2) ) / (fracGood__l + 1e-30)
            #1 / (z + (z == 0))
            _aux_good__l = np.nansum( (self.spec__lyx * self.fnorm__yx * maskFlag__lyx * maskEff__yx), axis = (1, 2) ) / (fracGood__l + (fracGood__l == 0))
            _aux_bad__l  = np.nansum( (self.spec__lyx * self.fnorm__yx * maskEff__yx), axis = (1, 2) )
            spec__l = np.where( fracGood__l > 0, _aux_good__l, _aux_bad__l)
    
            # Sum error in quadrature
            np.seterr(invalid='raise') 
            _aux_good__l = np.sqrt(abs(np.nansum( ((self.erro__lyx * self.fnorm__yx)**2 * maskFlag__lyx * maskEff__yx), axis = (1, 2) ))) / (fracGood__l + (fracGood__l == 0))
            _aux_bad__l  = np.sqrt(abs(np.nansum( ((self.erro__lyx * self.fnorm__yx)**2 * maskEff__yx), axis = (1, 2) )))
            erro__l = np.where( fracGood__l > 0, _aux_good__l, _aux_bad__l)
            
            #print self.lrest[197:201]
            #s = np.nansum( (self.spec__lyx * maskFlag__lyx * maskEff__yx), axis = (1, 2) )
            #n = np.nansum( (self.erro__lyx**2 * maskFlag__lyx * maskEff__yx), axis = (1, 2) )**0.5
            #print (s)[197:201]
            #print (n)[197:201]
            #print (s/n)[197:201]
            #s = np.nansum( (self.spec__lyx * maskFlag__lyx * maskEff__yx), axis = (1, 2) ) / (fracGood__l + (fracGood__l == 0))
            #n = np.nansum( (self.erro__lyx**2 * maskFlag__lyx * maskEff__yx), axis = (1, 2) )**0.5 / (fracGood__l + (fracGood__l == 0))
            #print (s)[197:201]
            #print (n)[197:201]
            #print (s/n)[197:201]


        # Create a spec0D
        s0d = Spec0D(spec__l, lrest = self.lrest, lobs = self.lobs, redshift = self.redshift, erro = erro__l, fobs_norm = self.fobs_norm)

        
        # Function to correct correlated errors
        if (beta != 1.):
            if (debug): print "@@> Using beta given as parameter                             (Npix = %s, beta = %s)." % (NpixTotal, beta)

        if (beta == 1.) & (beta_error == 'califa_voronoi_IAA'):
            beta = califa_voronoi_IAA_beta_error(NpixTotal)
            if (debug): print "@@> Using beta for correlated errors for CALIFA / Voronoi IAA (Npix = %s, beta = %s)." % (NpixTotal, beta)
                    
        if (beta == 1.) & (beta_error == 'califa_newbeta'):
            beta = califa_newbeta(s0d, llow_SN, lupp_SN)
            if (debug): print "@@> Using beta for correlated errors for CALIFA / new beta    (Npix = %s, beta = %s)." % (NpixTotal, beta)

        # Correct error by correlated error function
        s0d.erro__l *= beta

        
        # Checking all betas
        #print beta / califa_newbeta(s0d, llow_SN, lupp_SN)
        #print "@@> Using beta given as parameter                             (Npix = %s, beta = %s)." % (NpixTotal, beta)
        #beta = califa_newbeta(s0d, llow_SN, lupp_SN)
        #print "@@> Using beta for correlated errors for CALIFA / new beta    (Npix = %s, beta = %s)." % (NpixTotal, beta)
        #beta = califa_voronoi_IAA_beta_error(NpixTotal)
        #print "@@> Using beta for correlated errors for CALIFA / Voronoi IAA (Npix = %s, beta = %s)." % (NpixTotal, beta)
        #print s0d.erro__l is s0d._erro__ld
        #S, N, SN, N_formal = s0d.calcSN(llow_SN, lupp_SN)
        #print N, N_formal, N / N_formal

        
        # Creating flags
        if (NpixTotal > 0):
            
            # Sum flags: if a flag is in > 50% of the spaxels for a given lambda, it is propagated
            if (self.flagType__lyx):
                for id, (value, f__lyx) in self.flagType__lyx.items():
                    NpixFlagged__l = np.sum( (f__lyx * maskEff__yx), axis = (1, 2) )
                    fracFlagged__l = np.float_( NpixFlagged__l ) / NpixTotal
                    f__l =  (fracFlagged__l > 0.5)
            
                    # Add flag to spec0D
                    update_spatial_mask = False
                    if (id == "califa_flag"): update_spatial_mask = True
                    s0d.add_flagType(f__l, flagType_id = id, flagType_value = value, update_flag = True, update_spatial_mask = update_spatial_mask)

                    
        return s0d


    def zoneSN(self, llow, lupp, maskZone = None):

        specZone = self.toSpec0D(maskZone)
        SN = specZone.calcSN(llow, lupp)
        
        return SN

    
    def correctMWlaw_old(self, EBV, optionMWlaw):
        '''
        TODO: Transform this into parent's method (Spec)
        '''

        # Calc q = A_lambda / A_V for each reddening law
        if (EBV > 0):
            if (optionMWlaw == 'CCM'):
                R_V = 3.1
                q_norm = CCM_RedLaw(self.lobs, R_V)
            else:
                q_norm = np.ones_like(self.lobs)

        A_V = R_V * EBV

        # Fix q_norm dimensions to be able to multiply by fobs
        q_norm = q_norm[:, np.newaxis, np.newaxis]
        #if (self.spec__lyx.ndim == 2):
        #    q_norm = q_norm[:, np.newaxis]
        #elif (self.fobs.ndim == 3):
        #    q_norm = q_norm[:, np.newaxis, np.newaxis]

        aux = self.spec__lyx * 10**( 0.4 * A_V * q_norm )
        f = self.spec__lyx > -990
        self.spec__lyx[f] = aux[f]
        
    def CCM_RedLaw_old(self, l, R_V):
        '''
        TODO: Transform this into parent's method (Spec)
        '''
    
        x = 1.e4 / l
    
        # Optical / NIR: 1.1 <= x <= 3.3; 3030 --> 9091 AA
        # CCM89 eq 3a, 3b
    
        y = x - 1.82
    
        a = 1. + 0.17699 * y - 0.50447 * y**2 - 0.02427 * y**3 + 0.72085 * y**4 + 0.01979 * y**5 - 0.77530 * y**6 + 0.32999 * y**7
        b = 1.41338 * y + 2.28305 * y**2 + 1.07233 * y**3 - 5.38434 * y**4 - 0.62251 * y**5 + 5.30260 * y**6 -2.09002 * y**7
    
        q = a + (b / R_V)
    
        return q

    def correct_Flux_1plusZ_old(self, Factor1plusZ = 3):
        '''
        TODO: Transform this into parent's method (Spec)
        '''
        
        # f = 0: No correction
        # f = 1: F_nu
        # f = 3: F_lambda

        aux = self.spec__lyx * (1 + self.redshift)**(Factor1plusZ)
        f = self.spec__lyx > -990
        self.spec__lyx[f] = aux[f]

        aux = self.erro__lyx * (1 + self.redshift)**(Factor1plusZ)
        f = self.erro__lyx > -990
        self.erro__lyx[f] = aux[f]

        
    def plot(self, NyNx = (0, 0), maskZone__yx = None, beta_error = None):

        if (maskZone__yx == None):
            maskZone__yx = np.zeros_like( self.mask__yx, dtype = 'bool' )
            maskZone__yx[NyNx] = 1
        
        s0d = self.toSpec0D(maskZone__yx = maskZone__yx)
        s0d.plot()

        
    
class segCube(object):
    '''
    Some methods to go from segmentation cubes to zone masks (probably lossless) or segmentation maps (probably lossy) 
    '''

    def __init__(self, pixelDens, layer0 = None, Nz = None):
        self.segCube__zyx = ( np.float_(pixelDens) >= 0.5 )

        # Layer 0 should be sum of all other layers, so it does not count
        self.Nz = Nz
        if (self.Nz == None): self.Nz = self.segCube__zyx.shape[0] - 1
        
        if (layer0 == 'remove'):  self.remove_layer0()
        if (layer0 == 'replace'): self.replace_layer0()
        if (layer0 == 'add'):     self.add_layer0()
        if (layer0 == 'zeroout'): self.zeroout_layer0()
           
    def remove_layer0(self):
        seg0 = self.segCube__zyx
        self.segCube__zyx = seg0[1:, :, :].copy()
        self.Nz = self.Nz - 1 
        
    def replace_layer0(self):
        seg0 = self.segCube__zyx[1:, :, :].sum(axis = 0) > 0
        self.segCube__zyx[0, :, :] = seg0
            
    def add_layer0(self):
        seg0 = self.segCube__zyx.sum(axis = 0) > 0
        seg__yxz = np.transpose(self.segCube__zyx, (1,2,0))
        seg__yxz = np.dstack( [seg0, seg__yxz] )
        self.segCube__zyx = np.transpose(seg__yxz, (2,0,1))
        self.Nz = self.Nz + 1 

    def zeroout_layer0(self):
        self.segCube__zyx[0, :, :] = 0

    def zeroOutDupePlanes(self):
        '''
        Find duplicate planes and zeros them out.
        Useful to transform zones to yx map.
        '''

        # Sort cube
        segArea__z = self.segCube__zyx.sum(axis = (1,2))
        ind__z = np.argsort(segArea__z)
        scube__zyx = self.segCube__zyx[ind__z]
        segArea__z = segArea__z[ind__z]
        
        # Find duplicate areas
        dupe__z = np.zeros_like(segArea__z, dtype = 'bool')
        dupe__z[:-1] = (segArea__z[:-1] == segArea__z[1:])
        
        # Find planes j that are equal to plane j+1
        ind_dupe = np.where( dupe__z )[0]
        ind_zeroout = []
        for ind in ind_dupe:
            mask__yx = abs( scube__zyx[ind] - scube__zyx[ind+1] )
            if (mask__yx.sum() == 0):
                ind_zeroout.append(ind)

        # Zero out duplicate planes
        ind_zeroout__z = ind__z[ind_zeroout]
        self.segCube__zyx[ind_zeroout__z] = 0

        # Calc layer 0 again
        self.replace_layer0()

        
    def toSegMap(self, smallerArea = True):
        '''
        Lossy transformation from Segmentation Cube to Segmentation Map.
        smallerArea on  = priority to zones of smaller area and greater zone number
        smallerArea off = priority to zones of smaller zone number
        '''
        
        segMap__yx = np.zeros_like(self.segCube__zyx[0])
        scube__zyx = self.segCube__zyx.copy()
        ind__z = np.arange(scube__zyx.shape[0])
        Nz = self.segCube__zyx.shape[0] - 1
        
        # Sort cube
        if (smallerArea):
            segArea__z = self.segCube__zyx.sum(axis = (1,2))
            ind__z = np.lexsort((-ind__z, segArea__z))
            scube__zyx = self.segCube__zyx[ind__z]
            segArea__z = segArea__z[ind__z]

        # Create segmentation map 
        for i_map, map in enumerate(scube__zyx):
            _aux = map * ind__z[i_map]
            segMap__yx = np.where( (segMap__yx == 0), segMap__yx + _aux, segMap__yx)

        return segMap(segMap__yx, Nz = Nz)

    
    def transformZoneToYX(self, var__z):
        # Lossy transformation to create image
        smap  = self.toSegMap()
        scube = smap.toSegCube()

        # Careful not to sum up the super-region number 0
        var__yx = np.tensordot(scube.segCube__zyx[1:], var__z[1:], (0,0))  
        var__yx = np.ma.masked_array(var__yx, mask = ~scube.segCube__zyx[0])
 
        return var__yx

    
    def calcAreaZones(self, image = None, mask = None, debug = False, SN_clip = 0.):
        '''
        Calc area & other distances in pixels
        '''

        # Zero out all arrays 
        d = 1
        self.area__z         = np.zeros(self.Nz + 1) - 999.
        self.xcen__z         = np.zeros(self.Nz + 1) - 999.
        self.ycen__z         = np.zeros(self.Nz + 1) - 999.
        self.dcen_imaMax__z  = np.zeros(self.Nz + 1) - 999.
        self.dcen_imaCen__z  = np.zeros(self.Nz + 1) - 999.
        self.xmax__z         = np.zeros(self.Nz + 1) - 999.
        self.ymax__z         = np.zeros(self.Nz + 1) - 999.
        self.dmax_imaMax__z  = np.zeros(self.Nz + 1) - 999.
        self.dmax_imaCen__z  = np.zeros(self.Nz + 1) - 999.
        self.dtmin_imaMax__z = np.zeros(self.Nz + 1) - 999.
        self.dtmax_imaMax__z = np.zeros(self.Nz + 1) - 999.
        self.dtmin_imaCen__z = np.zeros(self.Nz + 1) - 999.
        self.dtmax_imaCen__z = np.zeros(self.Nz + 1) - 999.

        if (image == None):
            im1  = np.ones_like( self.segCube__zyx[0], 'float' )
            ima = Image(im1)
            ima_ycen, ima_xcen = ima.imgCentroid(SN_lim = SN_clip)
            
        if (image != None):
            # Find image's centroid and maximum emission
            ima = image
            ima_ymax, ima_xmax = ima.imgMax()
            ima_ycen, ima_xcen = ima.imgCentroid(SN_lim = SN_clip)

        # Apply masks
        scube__zyx = self.segCube__zyx
        if (image != None): scube__zyx = scube__zyx * (~ima.data__yx.mask)                
        if (mask  != None): scube__zyx = scube__zyx * mask

        # Calc areas 
        self.area__z = np.sum(scube__zyx, axis=(1,2))

        
        # Calc areas and distances for each zone
        for i, slice__yx in enumerate(scube__zyx):

            # Do not calc stuff if area = 0
            if (self.area__z[i] > 0):
                    
                # Calc centroids
                ind_slice__yx = np.where(slice__yx == 1)
                self.xcen__z[i] = np.mean(ind_slice__yx[1])
                self.ycen__z[i] = np.mean(ind_slice__yx[0])

                # Calc distance from zone centroid to image centroid
                d = np.sqrt( (self.xcen__z[-1] - ima_xcen)**2 + (self.ycen__z[-1] - ima_ycen)**2 )
                self.dcen_imaCen__z[i] = d
    
                # Calc minimum & maximum distance from region to image centroid
                d__yx = np.ma.array( ima.distPoint(ima_ycen, ima_xcen), mask = ~slice__yx )
                d_min = d__yx.min()
                d_max = d__yx.max()
                self.dtmin_imaCen__z[i] = d_min
                self.dtmax_imaCen__z[i] = d_max

                
                # Calc image-dependent distances
                if (image != None):

                    # Calc x,y of maximum emission
                    ima_zone = Image(image.data__yx * slice__yx)
                    _ymax, _xmax = ima_zone.imgMax()
                    self.xmax__z[i] = _xmax
                    self.ymax__z[i] = _ymax

                    # Calc distance from zone centroid to image maximum emission
                    d = np.sqrt( (self.xcen__z[i] - ima_xmax)**2 + (self.ycen__z[i] - ima_ymax)**2 )
                    self.dcen_imaMax__z[i] = d

                    # Calc distance from zone centroid to image centroid
                    d = np.sqrt( (self.xcen__z[i] - ima_xcen)**2 + (self.ycen__z[i] - ima_ycen)**2 )
                    self.dcen_imaCen__z[i] = d
    
                    # Calc distance from zone maximum emission to image maximum emission
                    d = np.sqrt( (self.xmax__z[i] - ima_xmax)**2 + (self.ymax__z[i] - ima_ymax)**2 )
                    self.dmax_imaMax__z[i] = d
    
                    # Calc distance from zone maximum emission to image centroid
                    d = np.sqrt( (self.xmax__z[i] - ima_xcen)**2 + (self.ymax__z[i] - ima_ycen)**2 )
                    self.dmax_imaCen__z[i] = d
                    
                    # Calc minimum & maximum distance from region to image maximum emission
                    d__yx = np.ma.array( ima.distPoint(ima_ymax, ima_xmax), mask = ~slice__yx )
                    d_min = d__yx.min()
                    d_max = d__yx.max()
                    self.dtmin_imaMax__z[i] = d_min
                    self.dtmax_imaMax__z[i] = d_max
                    
                
        if (debug):
            print "SN_clip", SN_clip

            plt.clf()
            #d = self.transformZoneToYX( self.area__z )
            #d = self.transformZoneToYX( self.dcen_imaMax__z )
            #d = self.transformZoneToYX( self.dcen_imaCen__z )
            #d = self.transformZoneToYX( self.dmax_imaMax__z )
            #d = self.transformZoneToYX( self.dmax_imaCen__z )
            #plt.imshow(self.toSegMap().segMap__yx)
            plt.imshow(d, interpolation="nearest")
            #plt.imshow(image)
            plt.colorbar()
            self.drawContours(drawCircles = True)

            '''
            ax = plt.subplot(111)
            i = 10
            r__z = (self.area__z / np.pi)**0.5
            plt.imshow(scube__zyx[i])
            plt.colorbar()
            plt.plot( ima_xcen, ima_ycen, 'o', color = 'red')
            for x, y, r, rmin, rmax in zip(self.xcen__z[i:i+1], self.ycen__z[i:i+1], r__z[i:i+1], self.dtmin_imaCen__z[i:i+1], self.dtmax_imaCen__z[i:i+1]):
                circle = mpatches.Circle((ima_xcen, ima_ycen), rmin, fc="none", ec="green")
                ax.add_patch(circle)
                circle = mpatches.Circle((ima_xcen, ima_ycen), rmax, fc="none", ec="green")
                ax.add_patch(circle)
                circle = mpatches.Circle((x, y), r, fc="none", ec="green")
                ax.add_patch(circle)
            '''

            
    def drawContours(self, drawCircles = False, colors = 'k'):
        '''
        Draw contour plots for segmented regions.

        Maybe this would look better with matplotlib.patches.PathPatch?
        But I cannot transform my numpy "slice" array into a Path object. More info:
        http://matplotlib.org/api/artist_api.html#matplotlib.patches.PathPatch
        http://matplotlib.org/users/path_tutorial.html
        '''

        xlow = -0.5
        xupp = -0.5 + self.segCube__zyx.shape[2]
        ylow = -0.5
        yupp = -0.5 + self.segCube__zyx.shape[1]

        for slice in self.segCube__zyx[1:]:
            plt.contour(slice, [0.5], colors=colors, linewidths=1, origin='lower', extent=(xlow,xupp,ylow,yupp))

        if (drawCircles):
            self.drawCircles()

            
    def drawCircles(self):

        if (len(self.area__z) == 0):
            print "!!! WARNING !!!> You have neither run calcAreaZones or given input areas."
            sys.exit(1)

        xlow = -0.5
        xupp = -0.5 + self.segCube__zyx.shape[2]
        ylow = -0.5
        yupp = -0.5 + self.segCube__zyx.shape[1]

        # Draw centroids
        plt.plot(self.xcen__z[1:], self.ycen__z[1:], '.', color='green')

        # Draw maxima
        if ( len(self.xmax__z) > 0 ):
            plt.plot(self.xmax__z[1:], self.ymax__z[1:], '.', color='red')

        # Draw circles
        #ax = plt.subplot(111)
        ax = plt.gca()
        r__z = (self.area__z / np.pi)**0.5
        for x, y, r in zip(self.xcen__z[1:], self.ycen__z[1:], r__z[1:]):
            circle = mpatches.Circle((x, y), r, fc="none", ec="green")
            ax.add_patch(circle)


            
class segMap(object):
    '''
    Some methods to go from segmentation maps to segmentation cubes (lossless) or zone masks (probably lossless)
    '''
    
    def __init__(self, zoneMap = None, *args, **kwargs):

        if (zoneMap != None):
            self._populateSegMap(zoneMap, *args, **kwargs)

            
    def _populateSegMap(self, zoneMap, Nz = None):

        self.segMap__yx = np.int_(zoneMap)

        self.Nz = Nz
        if (self.Nz == None): self.Nz = self.segMap__yx.max()

            
    def fromFitsFile(self, fitsFile):

        # Read fits file
        self.fitsFile = fitsFile
        dataHDU = astropy.io.fits.open(fitsFile, memmap = True)
        seg__yx = dataHDU[0].data       
        self.fitsHeader = dataHDU[0].header
        dataHDU.close()

        self._populateSegMap(seg__yx)

        
    def __sub__(self, other):
        '''
        Given a self segMap, subtract all zones which are contaminated by other segMap
        '''

        # Start differential segmentation cube
        mask__yx = (self.segMap__yx > 0)

        # Remove self zones "contaminated" by other zones
        for i in range(self.Nz+1):
            if (i > 0):
                zone_i = np.where( (other.segMap__yx == i), self.segMap__yx, -999)
                zone_remove = np.unique(zone_i)
                for remove in zone_remove:
                    mask__yx = mask__yx & (self.segMap__yx != remove)

        diff = self.__class__(mask__yx * self.segMap__yx)
        
        return diff

    
    def toSegCube(self, cumulative = False, renumber = False):
        '''
        Lossless transformation from Segmentation Map to Segmentation Cube. 
        '''

        i_zones = np.unique(self.segMap__yx[self.segMap__yx > 0])
        
        if renumber:
            Nz = np.sum(i_zones > 0)
            i_zones_new = np.arange(1, Nz+1)
        else:
            Nz = self.Nz
            i_zones_new = i_zones

        seg__zyx = np.zeros( (Nz+1, self.segMap__yx.shape[0], self.segMap__yx.shape[1]), dtype = 'bool')
        
        for iz_new, iz_old in zip(i_zones_new, i_zones):
            if (cumulative):
                seg__zyx[iz_new] = (self.segMap__yx <= iz_old) & (self.segMap__yx > 0)
            else:
                seg__zyx[iz_new] = (self.segMap__yx == iz_old)                

        return segCube(seg__zyx, layer0 = 'replace')
    
        
    def drawContours(self, **kwargs):

        scube = self.toSegCube()
        scube.drawContours(**kwargs)

        
    def calcAreaZones(self, *args, **kwargs):

        scube = self.toSegCube()
        scube.calcAreaZones(*args, **kwargs)

        self.area__z         = scube.area__z         
        self.xcen__z         = scube.xcen__z         
        self.ycen__z         = scube.ycen__z         
        self.dcen_imaMax__z  = scube.dcen_imaMax__z  
        self.dcen_imaCen__z  = scube.dcen_imaCen__z  
        self.xmax__z         = scube.xmax__z         
        self.ymax__z         = scube.ymax__z         
        self.dmax_imaMax__z  = scube.dmax_imaMax__z  
        self.dmax_imaCen__z  = scube.dmax_imaCen__z  
        self.dtmin_imaMax__z = scube.dtmin_imaMax__z 
        self.dtmax_imaMax__z = scube.dtmax_imaMax__z 
        self.dtmin_imaCen__z = scube.dtmin_imaCen__z 
        self.dtmax_imaCen__z = scube.dtmax_imaCen__z 


class Image(object):
    '''
    Very simple image-related methods
    '''

    def __init__(self, ima__yx = None, *args, **kwargs):

        if (ima__yx != None):
            self._populateImg(ima__yx, *args, **kwargs)

            
    def _populateImg(self, ima__yx, rms = None):
        self.mask__yx = np.zeros_like(ima__yx, 'bool')
        self.mask__yx = (ima__yx < -990.)
        self.data__yx = np.ma.masked_array(ima__yx, mask = self.mask__yx)
        self.rms__yx  = self.data__yx * 0.1
        
        self.Ny = self.data__yx.shape[0]
        self.Nx = self.data__yx.shape[1]            

        if (rms != None):
            self.rms__yx = np.ma.masked_array(rms, mask = self.mask__yx)
            self.mask__yx[rms < -990.] = 1

        SN = np.array(self.data__yx / self.rms__yx)
        self.SN__yx = np.ma.masked_array(SN, mask = self.mask__yx)
        
        # Get pixel centre coordinates
        self.x = np.arange(0, self.data__yx.shape[1])
        self.y = np.arange(0, self.data__yx.shape[0])

        # Get pixel border coordinates
        self.x1 = self.x - 0.5
        self.x2 = self.x + 0.5
        self.y1 = self.y - 0.5
        self.y2 = self.y + 0.5

        
    def fromFitsFile(self, fitsFile):

        # Read fits file
        self.fitsFile = fitsFile
        dataHDU = astropy.io.fits.open(fitsFile, memmap = True)
        ima__yx = dataHDU[0].data       
        self.fitsHeader = dataHDU[0].header
        dataHDU.close()

        self._populateImg(ima__yx)

        
    def plot(self, log=False, **kwargs):

        data = self.data__yx

        if log:
            data = mask_minus999( safe_log10(self.data__yx) )
         
        plt.imshow(data, origin='lower', interpolation='nearest', **kwargs)
        plt.colorbar()

        
    def clipSN(self, SN_lim):
        self.mask__yx[self.SN__yx < SN_lim] = 1

    def imageZonesSN(self, SegCube = None, SegMap = None, debug = False, beta_error = None):

        scube = Check_SegCube_SegMap(SegCube = SegCube, SegMap = SegMap)
        SN__z, rms__z = self.zonesSN(SegCube = scube.segCube__zyx, debug = debug, beta_error = beta_error)
        SN__yx  = scube.transformZoneToYX(SN__z)
        rms__yx = scube.transformZoneToYX(rms__z)
        
        if (debug):
            #pass
            #plt.figure("Image")
            plt.clf()
            #plt.imshow(self.data__yx, origin='lower', interpolation='nearest')
            scube = segCube(SegCube)
            scube.drawContours()
            plt.imshow(SN__yx, origin='lower', interpolation='nearest')
            plt.colorbar()

        return SN__z, rms__z, SN__yx, rms__yx

    
    def zonesSN(self, SegCube = None, SegMap = None, debug = False, beta_error = None):

        scube = Check_SegCube_SegMap(SegCube = SegCube, SegMap = SegMap)
        
        SN__z  = []
        rms__z = []
        
        for slice__yx in scube.segCube__zyx:
            Npix = ( (slice__yx) & (self.data__yx > 0) ).sum()
            _f = self.data__yx * slice__yx
            _e = self.rms__yx * slice__yx
            _A = slice__yx.sum()
            _SN, _N = self.zoneSN(_f, _e, Npix = Npix, beta_error = beta_error )
            SN__z.append( _SN )
            rms__z.append( _N )


        SN__z  = np.array(SN__z)
        rms__z = np.array(rms__z)
        
        if (debug):
            pass
            #plt.figure("Image")
            #plt.clf()
            #plt.imshow(self.data__yx, origin='lower', interpolation='nearest')
            #scube = segCube(SegCube)
            #scube.drawContours()
            #plt.clf()
            #plt.imshow(_e, origin='lower', interpolation='nearest')
            #plt.colorbar()

        return SN__z, rms__z


    def zoneSN(self, flux, rms, Npix = None, beta_error = None):

        beta = 1.
        if (beta_error == 'califa_voronoi_IAA'):
            beta = califa_voronoi_IAA_beta_error(Npix)
            
        _S = np.ma.sum(flux)
        _N = beta * np.sqrt( np.ma.sum(rms**2.) ) 
            
        if (_N != 0.):
            SN = _S / _N
        else:
            SN = 0.

        return SN, _N
    

    def SNMax(self):
        '''
        Find pixel with S/N maximum
        '''
        iy_max, ix_max = np.unravel_index( np.argmax(self.SN__yx), self.SN__yx.shape )
        return iy_max, ix_max
    
    def imgMax(self):
        '''
        Find pixel with image maximum
        '''
        iy_max, ix_max = np.unravel_index( np.argmax(self.data__yx), self.data__yx.shape )
        return iy_max, ix_max

    def imgMin(self):
        '''
        Find pixel with image minimum, excluding masks
        '''
        iy_max, ix_max = np.unravel_index( np.argmin(self.data__yx), self.data__yx.shape )
        return iy_max, ix_max

    def imgCentroid(self, SN_lim = 0):
        '''
        Find image centroid (takes mask into account)
        '''

        maskSN__yx = (self.SN__yx >= SN_lim)

        ind_ima__yx = np.ma.where( (self.data__yx * maskSN__yx) > 0. )
        xcen = np.mean(ind_ima__yx[1])
        ycen = np.mean(ind_ima__yx[0])
        
        return ycen, xcen

    def distPoint(self, ypoi, xpoi):
        '''
        Find distance from each pixel centre to given coordinates
        '''
        distPoint__yx = np.zeros_like(self.data__yx)
        distPoint__yx = distPoint__yx + np.sqrt( (self.x[np.newaxis, :] - xpoi)**2 + (self.y[:, np.newaxis] - ypoi)**2 )
        return distPoint__yx


    def distMaxPoint(self, ypoi, xpoi):
        '''
        Finds maximum distance from each pixel border to given coordinates
        '''
        d1 = np.sqrt( (self.x1[np.newaxis, :] - xpoi)**2 + (self.y1[:, np.newaxis] - ypoi)**2 )
        d2 = np.sqrt( (self.x1[np.newaxis, :] - xpoi)**2 + (self.y2[:, np.newaxis] - ypoi)**2 )
        d3 = np.sqrt( (self.x2[np.newaxis, :] - xpoi)**2 + (self.y1[:, np.newaxis] - ypoi)**2 )
        d4 = np.sqrt( (self.x2[np.newaxis, :] - xpoi)**2 + (self.y2[:, np.newaxis] - ypoi)**2 )
        d12 = np.maximum(d1, d2)
        d34 = np.maximum(d3, d4)
        distMaxPoint__yx = np.maximum(d12, d34)
        return distMaxPoint__yx


    def distMinPoint(self, ypoi, xpoi):
        '''
        Finds minimum distance from each pixel border to given coordinates
        '''
        d1 = np.sqrt( (self.x1[np.newaxis, :] - xpoi)**2 + (self.y1[:, np.newaxis] - ypoi)**2 )
        d2 = np.sqrt( (self.x1[np.newaxis, :] - xpoi)**2 + (self.y2[:, np.newaxis] - ypoi)**2 )
        d3 = np.sqrt( (self.x2[np.newaxis, :] - xpoi)**2 + (self.y1[:, np.newaxis] - ypoi)**2 )
        d4 = np.sqrt( (self.x2[np.newaxis, :] - xpoi)**2 + (self.y2[:, np.newaxis] - ypoi)**2 )
        d12 = np.minimum(d1, d2)
        d34 = np.minimum(d3, d4)
        distMaxPoint__yx = np.minimum(d12, d34)
        return distMaxPoint__yx

    
    def findHLR_pix(self, ycen = None, xcen = None, SN_lim = 0, debug = False):
        '''
        Find the half light radius using of an image at 5650.
        Based on Andre's pycasso Q3DataCube.findHLR_pix 
        
        Returns
        -------
        HLR : float
            The half light radius, in pixels.
        '''

        maskSN__yx = (self.SN__yx >= SN_lim)

        # Get centres
        if (ycen == None) | (xcen == None):
            ycen, xcen = self.imgMax()

        # Calc r for the image
        r__yx = np.sqrt( (self.y[:, np.newaxis] - ycen)**2 + (self.x[np.newaxis, :] - xcen)**2 )

        # Create r vector 
        dr = 1
        r_bins = np.arange(0., np.max(r__yx) + dr, dr)
        Nr = len(r_bins)

        # numpy.digitize returns: xbin[i-1] <= x < xbin[i]
        i_r_in_rbins = np.digitize(r__yx.flat, r_bins).reshape(r__yx.shape)

        smap = segMap( i_r_in_rbins )
        scube = smap.toSegCube()
        scube.zeroout_layer0()

        tensorXYtoR__ryx = scube.segCube__zyx
        cumLumin__r = np.ma.sum(self.data__yx * maskSN__yx * tensorXYtoR__ryx, axis=(1,2)).cumsum()

        # Use the inverse cumulative luminosity. That is, given a luminosity,
        # the function return the radius. This works because the cumulative
        # sum is a monotonically increasing function.
        # FIXME: Will this work if the image is not contiguous? Are there any?
        scube2 = smap.toSegCube(cumulative = True)
        scube2.calcAreaZones()
        scube2.area__z[0] = 0
        r_eff = np.sqrt(scube2.area__z / np.pi)
        intInverseLC = scipy.interpolate.interp1d(cumLumin__r, r_eff)
        HLR_pix = intInverseLC(cumLumin__r.max()/2)

        
        if (debug):
            #plt.clf()
            #plt.plot(intInverseLC.y, intInverseLC.x)
            #plt.plot(r_eff, cumLumin__r)
            #plt.imshow( np.ma.array(self.data__yx, mask = 1-maskSN__yx), interpolation="nearest", origin='lower')
            #plt.colorbar()
            #ax = plt.subplot(111)
            #circle = mpatches.Circle((xcen, ycen), HLR_pix, fc="none", ec="black")
            #ax.add_patch(circle)
            #hlr_rgb = 7.72818655609
            #circle = mpatches.Circle((xcen, ycen), hlr_rgb, fc="none", ec="black")
            #ax.add_patch(circle)
            
            plt.clf()
            plt.plot(r_bins[1:], r_bins[1:]/r_eff[1:])
            
            print cumLumin__r
            print r_bins
            print r_bins-1
            print r_eff
            print HLR_pix, cumLumin__r.max()
        
        return float(HLR_pix)
        

    def intersectCircle(self, ycen, xcen, r):
        '''
        Finds intersections between pixel borders and a circle of radius r and centred in (xcen, ycen)
        '''

        self.line1xint1__yx = np.zeros_like(self.data__yx) + np.nan
        self.line1xint2__yx = np.zeros_like(self.data__yx) + np.nan
        self.line2yint1__yx = np.zeros_like(self.data__yx) + np.nan
        self.line2yint2__yx = np.zeros_like(self.data__yx) + np.nan
        self.line3xint1__yx = np.zeros_like(self.data__yx) + np.nan
        self.line3xint2__yx = np.zeros_like(self.data__yx) + np.nan
        self.line4yint1__yx = np.zeros_like(self.data__yx) + np.nan
        self.line4yint2__yx = np.zeros_like(self.data__yx) + np.nan

        # Line 1: y = y1
        D = r**2 - (self.y1[:, np.newaxis] - ycen)**2
        xint1 = np.where((D >= 0), xcen + np.sqrt(abs(D)), np.nan)
        self.line1xint1__yx[:,] = np.where( (xint1 >= self.x1[np.newaxis, :]) & (xint1 <= self.x2[np.newaxis, :]), xint1, np.nan)
        xint2 = np.where((D >  0), xcen - np.sqrt(abs(D)), np.nan)
        self.line1xint2__yx[:,] = np.where( (xint2 >= self.x1[np.newaxis, :]) & (xint2 <= self.x2[np.newaxis, :]), xint2, np.nan)

        # Line 2: x = x2
        D = r**2 - (self.x2[np.newaxis, :] - xcen)**2
        yint1 = np.where((D >= 0), ycen + np.sqrt(abs(D)), np.nan)
        self.line2yint1__yx[:,] = np.where( (yint1 >= self.y1[:, np.newaxis]) & (yint1 <= self.y2[:, np.newaxis]), yint1, np.nan)
        yint2 = np.where((D >  0), ycen - np.sqrt(abs(D)), np.nan)
        self.line2yint2__yx[:,] = np.where( (yint2 >= self.y1[:, np.newaxis]) & (yint2 <= self.y2[:, np.newaxis]), yint2, np.nan)

        # Line 3: y = y2
        D = r**2 - (self.y2[:, np.newaxis] - ycen)**2
        xint1 = np.where((D >= 0), xcen + np.sqrt(abs(D)), np.nan)
        self.line3xint1__yx[:,] = np.where( (xint1 >= self.x1[np.newaxis, :]) & (xint1 <= self.x2[np.newaxis, :]), xint1, np.nan)
        xint2 = np.where((D >  0), xcen - np.sqrt(abs(D)), np.nan)
        self.line3xint2__yx[:,] = np.where( (xint2 >= self.x1[np.newaxis, :]) & (xint2 <= self.x2[np.newaxis, :]), xint2, np.nan)

        # Line 4: x = x1
        D = r**2 - (self.x1[np.newaxis, :] - xcen)**2
        yint1 = np.where((D >= 0), ycen + np.sqrt(abs(D)), np.nan)
        self.line4yint1__yx[:,] = np.where( (yint1 >= self.y1[:, np.newaxis]) & (yint1 <= self.y2[:, np.newaxis]), yint1, np.nan)
        yint2 = np.where((D >  0), ycen - np.sqrt(abs(D)), np.nan)
        self.line4yint2__yx[:,] = np.where( (yint2 >= self.y1[:, np.newaxis]) & (yint2 <= self.y2[:, np.newaxis]), yint2, np.nan)

        # Return flags:
        #  0: pixel completely outside
        #  1: pixel completely inside
        # -1: pixel intersected by circle
        # -2: central pixel is greater than circle
        distMin__yx  = self.distMinPoint(ycen, xcen)
        flag = np.where( (distMin__yx <= r), 1, 0 )
        flag = np.where( np.isnan(self.line1xint1__yx), flag, -1)
        flag = np.where( np.isnan(self.line1xint2__yx), flag, -1)
        flag = np.where( np.isnan(self.line2yint1__yx), flag, -1)
        flag = np.where( np.isnan(self.line2yint2__yx), flag, -1)
        flag = np.where( np.isnan(self.line3xint1__yx), flag, -1)
        flag = np.where( np.isnan(self.line3xint2__yx), flag, -1)
        flag = np.where( np.isnan(self.line4yint1__yx), flag, -1)
        flag = np.where( np.isnan(self.line4yint2__yx), flag, -1)

        self.flag_line1 = np.where( (~np.isnan(self.line1xint1__yx)) | (~np.isnan(self.line1xint2__yx)), 1, 0)
        self.flag_line2 = np.where( (~np.isnan(self.line2yint1__yx)) | (~np.isnan(self.line2yint2__yx)), 1, 0)
        self.flag_line3 = np.where( (~np.isnan(self.line3xint1__yx)) | (~np.isnan(self.line3xint2__yx)), 1, 0)
        self.flag_line4 = np.where( (~np.isnan(self.line4yint1__yx)) | (~np.isnan(self.line4yint2__yx)), 1, 0)

        # Fix central pixel
        flag = np.where( ((r < .5) & (xcen == self.x[np.newaxis, :]) & (ycen == self.y[:, np.newaxis])), -2, flag )

        return flag


    def areaInsideCircle(self, ycen, xcen, r):
        '''
        Calculates area of each pixel that is inside a circle of radius r and centred in (xcen, ycen)
        '''

        flagInters = self.intersectCircle(ycen, xcen, r)
        area = np.float_(flagInters)

        # Calc fraction of pixel inside circle for the borders

        # Case 1: interceptions are only in vertical lines (line2, line4)
        _f1 = np.where( (area < 0) &
                        ( ( ( self.flag_line2 | self.flag_line4 ) & (~self.flag_line1 & ~self.flag_line3) & ( abs(self.y[:, np.newaxis] - ycen) > .5) ) |
                          ( self.flag_line1 & self.flag_line2 & self.flag_line4  ) |
                          ( self.flag_line3 & self.flag_line2 & self.flag_line4  ) )
            , 1, 0)
        aux = self.FuncIntegral_SqrtR2MinusU2(self.x2[np.newaxis, :], xcen, r) - self.FuncIntegral_SqrtR2MinusU2(self.x1[np.newaxis, :], xcen, r)
        dx = self.x2[np.newaxis, :] - self.x1[np.newaxis, :]
        aN = aux - (dx * (self.y1[:, np.newaxis] - ycen))  # Case 1 North: above ycen
        aS = aux - (dx * (ycen - self.y2[:, np.newaxis]))  # Case 1 South: below ycen
        a1 = np.where( (self.y[:, np.newaxis] >= ycen), aN, aS )
        area = np.where(_f1, a1, area)
        #print area[37,37], area[31,37], aS[31,37], aux[:,37]
        #print aux[:,37], dx[:,37], area[35,37]


        # Case 2: interceptions are only in horizontal lines (line1, line3)
        _f2 = np.where( (area < 0) &
                        ( ( ( self.flag_line1 | self.flag_line3 ) & (~self.flag_line2 & ~self.flag_line4) & ( abs(self.x[np.newaxis, :] - xcen) > .5) ) |
                          ( self.flag_line1 & self.flag_line2 & self.flag_line3  ) |
                          ( self.flag_line3 & self.flag_line4 & self.flag_line1  ) )
            , 1, 0)
        aux = self.FuncIntegral_SqrtR2MinusU2(self.y2[:, np.newaxis], ycen, r) - self.FuncIntegral_SqrtR2MinusU2(self.y1[:, np.newaxis], ycen, r)
        dy = self.y2[:, np.newaxis] - self.y1[:, np.newaxis]
        aE = aux - (dy * (self.x1[np.newaxis, :] - xcen))  # Case 2 East: right of xcen
        aW = aux - (dy * (xcen - self.x2[np.newaxis, :]))  # Case 2 West: left  of xcen
        a2 = np.where( (self.x[np.newaxis, :] >= xcen), aE, aW )
        area = np.where(_f2, a2, area)
        #print area[34,40], area[34,34], aE[34,40], aW[34,34], aux[34,:]
        #print self.line2yint1__yx[34,36], self.line2yint1__yx[34,36]
        

        # Getting x_interception for Cases 3, 4, 5: intercept one horizontal and one vertical axis
        l1  = np.where( np.isnan(self.line1xint1__yx), 1e30, self.line1xint1__yx )
        l2  = np.where( np.isnan(self.line1xint2__yx), 1e30, self.line1xint2__yx )
        l3  = np.where( np.isnan(self.line3xint1__yx), 1e30, self.line3xint1__yx )
        l4  = np.where( np.isnan(self.line3xint2__yx), 1e30, self.line3xint2__yx )
        m12 = np.minimum( l1, l2 )
        m34 = np.minimum( l3, l4 )
        xintlow = np.minimum( m12, m34 )

        l1  = np.where( np.isnan(self.line1xint1__yx), -1e30, self.line1xint1__yx )
        l2  = np.where( np.isnan(self.line1xint2__yx), -1e30, self.line1xint2__yx )
        l3  = np.where( np.isnan(self.line3xint1__yx), -1e30, self.line3xint1__yx )
        l4  = np.where( np.isnan(self.line3xint2__yx), -1e30, self.line3xint2__yx )
        m12 = np.maximum( l1, l2 )
        m34 = np.maximum( l3, l4 )
        mm  = np.maximum( m12, m34 )
        xintupp= np.maximum( m12, m34 )
        #print xintlow[35,34], xintupp[35,34]


        # Case 3: intercepts lines 1 & 2 for pixels above center
        #                 or lines 3 & 4 for pixels below center
        #                 or lines 1 & 4 for pixels above center
        #                 or lines 2 & 3 for pixels below center
        # This means we need to integrate just below the circle.
        _f3a = np.where( (self.y[:, np.newaxis] >= ycen) & (self.flag_line1) & (self.flag_line2), 1, 0)
        _f3b = np.where( (self.y[:, np.newaxis]  < ycen) & (self.flag_line3) & (self.flag_line4), 1, 0)
        _f3c = np.where( (self.y[:, np.newaxis] >= ycen) & (self.flag_line1) & (self.flag_line4), 1, 0)
        _f3d = np.where( (self.y[:, np.newaxis]  < ycen) & (self.flag_line2) & (self.flag_line3), 1, 0)
        _f3  = np.where( (area < 0) & (_f3a | _f3b | _f3c | _f3d), 1, 0)

        # Case 3 East: right of xcen
        aux = self.FuncIntegral_SqrtR2MinusU2(self.x2[np.newaxis, :], xcen, r) - self.FuncIntegral_SqrtR2MinusU2(xintlow, xcen, r)
        dx = self.x2[np.newaxis, :] - xintlow
        aNE = aux - (dx * (self.y1[:, np.newaxis] - ycen))  # Case 1 North: above ycen
        aSE = aux - (dx * (ycen - self.y2[:, np.newaxis]))  # Case 1 South: below ycen
        a3 = np.where( (self.x[np.newaxis, :]  < xcen) & (self.y[:, np.newaxis] >= ycen), aNE, -1 )
        a3 = np.where( (self.x[np.newaxis, :]  < xcen) & (self.y[:, np.newaxis]  < ycen), aSE, a3 )

        # Case 3 West: left of xcen
        aux = self.FuncIntegral_SqrtR2MinusU2(xintupp, xcen, r) - self.FuncIntegral_SqrtR2MinusU2(self.x1[np.newaxis, :], xcen, r)
        dx = xintupp - self.x1[np.newaxis, :]
        aNW = aux - (dx * (self.y1[:, np.newaxis] - ycen))  # Case 1 North: above ycen
        aSW = aux - (dx * (ycen - self.y2[:, np.newaxis]))  # Case 1 South: below ycen
        a3 = np.where( (self.x[np.newaxis, :] >= xcen) & (self.y[:, np.newaxis] >= ycen), aNW, a3 )
        a3 = np.where( (self.x[np.newaxis, :] >= xcen) & (self.y[:, np.newaxis]  < ycen), aSW, a3 )

        area = np.where(_f3, a3, area)
        #print area[36,39], aN[36,39], xmin[36,39], xmax[36,39]
        #print area[36,35], aN[36,35], xmin[36,35], xmax[36,35]
        #print area[35,35], aN[35,35], xmin[35,35], xmax[35,35]
        #print area[34,38], area[35,37]


        # Case 4: all other cases where we need more than one integral (curved part & rectangle)
        _f4 = np.where( (area < 0), 1, 0)

        # Case 4 East: right of xcen
        aux = self.FuncIntegral_SqrtR2MinusU2(xintlow, xcen, r) - self.FuncIntegral_SqrtR2MinusU2(self.x1[np.newaxis, :], xcen, r)
        dx = xintlow - self.x1[np.newaxis, :]
        aNE = aux - (dx * (self.y1[:, np.newaxis] - ycen))  # Case 4 North-East: above ycen
        aSE = aux - (dx * (ycen - self.y2[:, np.newaxis]))  # Case 4 South-East: below ycen
        aR  = (self.x2[np.newaxis, :] - xintlow) * (self.y2[:, np.newaxis] - self.y1[:, np.newaxis]) # Area of rectangle
        a4 = np.where( (self.x[np.newaxis, :] < xcen) & (self.y[:, np.newaxis] > ycen), aNE + aR, 0. )
        a4 = np.where( (self.x[np.newaxis, :] < xcen) & (self.y[:, np.newaxis] < ycen), aSE + aR, a4 )

        # Case 4 West: left of xcen
        aux = self.FuncIntegral_SqrtR2MinusU2(self.x2[np.newaxis, :], xcen, r) - self.FuncIntegral_SqrtR2MinusU2(xintupp, xcen, r)
        dx = self.x2[np.newaxis, :] - xintupp
        aNW = aux - (dx * (self.y1[:, np.newaxis] - ycen))  # Case 4 North-West: above ycen
        aSW = aux - (dx * (ycen - self.y2[:, np.newaxis]))  # Case 4 South-West: below ycen
        aR  = (xintupp - self.x1[np.newaxis, :]) * (self.y2[:, np.newaxis] - self.y1[:, np.newaxis]) # Area of rectangle
        a4 = np.where( (self.x[np.newaxis, :] > xcen) & (self.y[:, np.newaxis] > ycen), aNW + aR, a4 )
        a4 = np.where( (self.x[np.newaxis, :] > xcen) & (self.y[:, np.newaxis] < ycen), aSW + aR, a4 )

        # Case 4 centered: area == 0
        a4 = np.where( (self.x[np.newaxis, :] == xcen) & (self.y[:, np.newaxis] == ycen), 0., a4 )
        area = np.where(_f4, a4, area)

        #print xint[36,36], xint[36,36], aux[36,36], self.x1[36], area[36,36], aR[36,36]
        #print xint[36,38], xint[36,38], aux[36,38], self.x2[36], area[36,38], aR[36,38]
        #print aNW[36,37], aR[36,37], area[36,37], self.x2[36]
        #print self.line2yint1__yx[36,37], self.line2yint2__yx[36,37]


        # Cases 5, 6: fix special cases in central pixel & around
        _f5 = np.where( (abs(xcen - self.x[np.newaxis, :]) <= (1e-10)) & (abs(ycen - self.y[:, np.newaxis]) <= (1e-10)), 1, 0 )
        _f6 = np.where( (_f5 == 0), 1, 0 )
        #print area[35,37]

        # Case 5a: central pixel is centred in circle & circle is smaller than central pixel
        _f5a = np.where( (_f5) & (r <= .5) & (abs(xcen - self.x[np.newaxis, :]) < (1e-10)) & (abs(ycen - self.y[:, np.newaxis]) < (1e-10)), 1, 0 )
        a5a = np.pi * r**2
        if (np.sum(_f5a) > 0): area = np.where(_f5a, a5a, 0.)
                                  
        # Case 5b: central pixel is centred in circle & circle is greater than central pixel but does not encompasses it all
        _f5b = np.where( (_f5) & (r > .5) & (r < np.sqrt(2.)/2.) & (abs(xcen - self.x[np.newaxis, :]) < (1e-10)) & (abs(ycen - self.y[:, np.newaxis]) < (1e-10)), 1, 0 )
        aux = self.FuncIntegral_SqrtR2MinusU2(self.x2[np.newaxis, :], xcen, r) - self.FuncIntegral_SqrtR2MinusU2(xintupp, xcen, r)
        dx = self.x2[np.newaxis, :] - xintupp
        aNW = aux - (dx * (self.y[:, np.newaxis] - ycen))
        aR  = (xintupp - self.x[np.newaxis, :]) * (self.y2[:, np.newaxis] - self.y[:, np.newaxis]) # Area of rectangle
        a5b = 4. * (aNW + aR)
        area = np.where(_f5b, a5b, area)
        #print _f5a[34,37]
        #print xintupp[34,37], self.x2[37], aux[:,37]

        # Treat neiboughring pixels in case 5b
        _f5b_neibN = np.where( (_f5 != 1) &
                        ( ( (~np.isnan(self.line1xint1__yx)) & (~np.isnan(self.line1xint2__yx)) ) ) )
        _f5b_neib = np.where( (_f5 != 1) &
                        ( ( (~np.isnan(self.line1xint1__yx)) & (~np.isnan(self.line1xint2__yx)) ) |
                          ( (~np.isnan(self.line2yint1__yx)) & (~np.isnan(self.line2yint2__yx)) ) |
                          ( (~np.isnan(self.line3xint1__yx)) & (~np.isnan(self.line3xint2__yx)) ) |
                          ( (~np.isnan(self.line4yint1__yx)) & (~np.isnan(self.line4yint2__yx)) ) )
            , 1, 0)
        if (np.sum(_f5b_neib) > 0):
            aux = self.FuncIntegral_SqrtR2MinusU2(xintupp, xcen, r) - self.FuncIntegral_SqrtR2MinusU2(xintlow, xcen, r)
            dx = xintupp - xintlow
            aN = aux - (dx * (self.y1[:, np.newaxis] - ycen))
            a5n = np.nan
            if (len(_f5b_neibN) > 0): a5n = aN[_f5b_neibN]
            area = np.where(_f5b_neib, a5n, area)
            #print xintlow[35,37], xintupp[35,37], aux[35,37], (dx * (self.y1[:, np.newaxis] - ycen))[35,37], 4*area[35,37] + area[34,37], xcen
            #print a5n.shape

            
        # Case 5c: central pixel is centred in circle & circle is greater than central pixel & encompasses it
        _f5c = np.where( (_f5) & (r >= np.sqrt(2.)/2.) & (abs(xcen - self.x[np.newaxis, :]) < (1e-10)) & (abs(ycen - self.y[:, np.newaxis]) < (1e-10)), 1, 0 )
        area = np.where(_f5c, 1., area)

        # Treat neiboughring pixels in case 5c
        _f5b_neibN = np.where( (_f5 != 1) &
                        ( ( (~np.isnan(self.line1xint1__yx)) & (~np.isnan(self.line1xint2__yx)) ) ) )
        _f5b_neib = np.where( (_f5 != 1) &
                        ( ( (~np.isnan(self.line1xint1__yx)) & (~np.isnan(self.line1xint2__yx)) ) |
                          ( (~np.isnan(self.line2yint1__yx)) & (~np.isnan(self.line2yint2__yx)) ) |
                          ( (~np.isnan(self.line3xint1__yx)) & (~np.isnan(self.line3xint2__yx)) ) |
                          ( (~np.isnan(self.line4yint1__yx)) & (~np.isnan(self.line4yint2__yx)) ) )
            , 1, 0)
        if (np.sum(_f5b_neib) > 0):
            aux = self.FuncIntegral_SqrtR2MinusU2(xintupp, xcen, r) - self.FuncIntegral_SqrtR2MinusU2(xintlow, xcen, r)
            dx = xintupp - xintlow
            aN = aux - (dx * (self.y1[:, np.newaxis] - ycen))
            a5n = np.nan
            if (len(_f5b_neibN) > 0): a5n = aN[_f5b_neibN]
            area = np.where(_f5b_neib, a5n, area)
            #print xintlow[35,37], xintupp[35,37], aux[35,37], (dx * (self.y1[:, np.newaxis] - ycen))[35,37], 4*area[35,37] + area[34,37], xcen
            #print a5n.shape

 


        # Case 6: central pixel is not centred in circle
        # Looks like this case is ok somewhow
        dist__yx = self.distPoint(ycen, xcen)
        _f6N = np.where( (_f6) & (r <= 1. + 1e-10) & (dist__yx <= 1. + 1e-10) , 1, 0 )


        # Fix nan's, if any
        area = np.where( np.isnan(area), 0., area)

        #print area[30:39,32:42]

        #return _f3
        return area

    
    def FuncIntegral_SqrtR2MinusU2(self, u, ucen, r):
        aux = ( (u - ucen) / abs(r) )
        arg_arcsin = np.where( abs(aux) <= (1. + 1e-10), aux, np.nan )
        # Fixing precision problem
        arg_arcsin = np.where( (abs(abs(aux) - 1.) <= 1e-10) & (aux < 0.), -1., arg_arcsin )
        arg_arcsin = np.where( (abs(abs(aux) - 1.) <= 1e-10) & (aux > 0.),  1., arg_arcsin )
        int = 0.5 * ( (u - ucen) * np.sqrt(abs(r**2 - (u - ucen)**2) + 1e-30) + r**2 * np.arcsin(arg_arcsin) )
        #if (aux.shape[0] > 1):
        #    print aux[34,37], ((abs(aux[34,37]) - 1.) <= 1e-10), arg_arcsin[34,37]#, int[34,37]
        #else:
        #    print aux[:,37], ((abs(aux[:,37]) - 1.) <= 1e-10), arg_arcsin[:,37]#, int[:,37]
        return int
    
'''

#    def toImageGaussFilter(self, fcen = None, ):

'''


# *************************************************************************************** #
# Extinction laws

def CCM_RedLaw(l, R_V):
    '''
    Given wavelenghts, return CCM extinction law
    '''
    
    x = 1.e4 / l
    
    # Optical / NIR: 1.1 <= x <= 3.3; 3030 --> 9091 AA
    # CCM89 eq 3a, 3b
    
    y = x - 1.82
    
    a = 1. + 0.17699 * y - 0.50447 * y**2 - 0.02427 * y**3 + 0.72085 * y**4 + 0.01979 * y**5 - 0.77530 * y**6 + 0.32999 * y**7
    b = 1.41338 * y + 2.28305 * y**2 + 1.07233 * y**3 - 5.38434 * y**4 - 0.62251 * y**5 + 5.30260 * y**6 -2.09002 * y**7
    
    q = a + (b / R_V)
    
    return q

# *************************************************************************************** #
# Functions

def safe_log10(x):
    log10_x = np.where( (x > 0), np.log10(abs( x + (x == 0))), -999. )
    return log10_x
    
def safe_div(a, b):
    aob = np.where( (b != 0), a / ( b + (b == 0)), -999. )
    return aob

def read_lines_params_hdf5_dataset(filename):
    f_h5py = h5py.File(filename, "r")
    elines = f_h5py.get('/')
    return elines

def lines_params_dataset_stats(ds, h5py_close = True):
    '''
    __m = measurement
    __e = emission line
    '''

    rms = {}
    rms['lambda'] = np.array([ ds.values()[0]['lambda'] ])
    
    keys = ['El_F', 'El_v0', 'El_vd', 'El_W']
    
    for key in keys:
        El_k__me =  np.array([m[key] for m in ds.values()])
        rms[key] = np.std( El_k__me, axis = 0 )

    if h5py_close:
        ds.file.close()
        
    return rms


def test_file(outfile, default='/tmp/lix', delete=False, append=False, debug=False):
    if outfile is None:
        print 'Saving to default file file %s.' % (outfile)
        outfile = '/tmp/lix.hdf5'
        
    outfile = os.path.abspath(outfile)
    
    if (os.path.exists(outfile)):
        if (delete):
            if debug: print 'Overwriting file %s.' % (outfile)
            os.remove(outfile)
        elif (not append):
            print 'File %s exists, giving up. Try again with the overwrite option.' % (outfile)
            sys.exit(1)

    return outfile


def read_lines_params(lines_file):

    if lines_file is None:
        lines_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "specHelpers_lines.dat")

    return atpy.Table(lines_file, type = "ascii")


def gaussian_l(l, p):
    l0rest, F, l0, ld, F0 = p[0], p[1], p[2], p[3], p[4]

    dl = l[1] - l[0]
    l0  = l0rest + l0
    if ld > 0:
        amp = F / (np.sqrt(2*np.pi) * ld)
        G = amp * np.exp(-0.5 * ((l - l0) / ld)**2)
    else:
        G = np.zeros_like(l)
        
    # Sum up baseline to gaussian not too far from the peak
    G += add_baseline_gaussian(l, G, F0)
 
    return G


def add_baseline_gaussian(l, G__l, F0, B__l = None, tol = 1e-5):
    '''
    Add a baseline around the peak of a gaussian,
    respecting where the old baseline B__l > 0!
    '''

    if (B__l is None):
        B__l = np.zeros_like(G__l)
        
    if (G__l.max() != 0):
        ff = (G__l / G__l.max()) > tol
        B__l[ff] = F0

    return B__l

def gaussian_sum_l(l, p):

    Nargs_gaussian_l = 5

    params__e = np.array(p).reshape(-1, Nargs_gaussian_l)
    if params__e.shape[1] != Nargs_gaussian_l:
        raise AssertionError("Argument list too short or incomplete.")

    # Add baseline to lines, but do not add baseline twice below blended lines!
    Gs = np.zeros_like(l)
    B = np.zeros_like(l)
    for params in params__e:
        aux = deepcopy(params)
        aux[-1] = 0.
        G = gaussian_l(l, aux)
        B = add_baseline_gaussian(l, G, params[-1], B)
        Gs += G

    Gs += B
    
    return Gs


def gaussian_v(l, p):
    l0rest, F, v0, vd = p[0], p[1], p[2], p[3]
    
    l0  = l0rest * (1 + v0 / c_light)
    amp = (F * c_light) / (np.sqrt(2*np.pi) * l0 * vd)
    v = c_light * (l - l0) / l0
    G = amp * np.exp(-0.5 * ((v - v0) / vd)**2)
    
    return G


def gaussian_sum_v(l, p):

    Nargs_gaussian_l = 4

    params__e = np.array(p).reshape(-1, Nargs_gaussian_l)
    if params__e.shape[1] != Nargs_gaussian_l:
        raise AssertionError("Argument list too short or incomplete.")

    gauss_tot = np.zeros_like(l)
    for params in params__e:
        gauss_tot += gaussian_v(l, params)

    return gauss_tot


def replace_nan_inf_by_minus999(x):
    
    y1 = replace_by_minus999(x,  'nan')
    y2 = replace_by_minus999(y1, 'inf')
    
    return y2

    
def replace_by_minus999(x, x_old, x_new = -999):

    y = x.copy()

    if x_old == 'nan':
        flag = np.isnan(x)
    elif x_old == 'inf':
        flag = np.isinf(x)
    else:
        flag = (x == x_old)

    y[flag] = x_new

    return y
    
            
def mask_minus999(var, thereshold = -990., fill = None):
    
    a = np.ma.masked_array(var, mask=(var <= thereshold))

    if fill == None:
        return a
    else:
        return a.filled(fill)


def califa_newbeta(spec_nD, llow_SN, lupp_SN):

    S, N, SN, N_formal = spec_nD.calcSN(llow_SN, lupp_SN)
    beta = N / N_formal

    return beta


def califa_voronoi_IAA_beta_error(Npix):
    
    beta = (15. * Npix / (15. + Npix - 1.))**0.5
    
    return beta


def Check_SegCube_SegMap(SegMap = None, SegCube = None):

    # If both a seg cube and map are given, or none, raise error
    if (SegMap == None) and (SegCube == None):
        print "!!! WARNING !!!> You need to input either a segmentation map or cube."
        sys.exit(1)

    if (SegMap != None) and (SegCube != None):
        print "!!! WARNING !!!> You need to input either a segmentation map or cube, not both."
        sys.exit(1)

    # Transform segmentation map into cube
    if (SegMap != None):
        segM = segMap(SegMap)
        SegCube = segM.toSegCube().segCube__zyx
    
    return segCube(SegCube)


            
def CalifaMatchCombData(ydiff, xdiff, ydiff2, xdiff2, spec__lyx, erro__lyx, flag__lyx, mask__yx):

    Nl = spec__lyx.shape[0]
    Ny = spec__lyx.shape[1]
    Nx = spec__lyx.shape[2]
    nNy = Ny + abs(ydiff)
    nNx = Nx + abs(xdiff)

    if (ydiff != 0):
    
        aux__lyx = np.ones([Nl, abs(ydiff), Nx])
        aux__yx  = np.zeros([abs(ydiff), Nx])
    
        # Add array at the beginning of y
        if (ydiff > 0):
            print "@@> Adding array at the beginning of y array for COMBO..." 
            spec__lyx = np.concatenate((aux__lyx*np.nan,   spec__lyx), axis=1)
            erro__lyx = np.concatenate((aux__lyx*np.nan,   erro__lyx), axis=1)
            flag__lyx = np.concatenate((np.int_(aux__lyx), flag__lyx), axis=1)
            mask__yx  = np.concatenate((aux__yx,           mask__yx ), axis=0) > 0
    
        # Add array at the end of y
        if (ydiff < 0):
            print "@@> Adding array at the end of y array for COMBO..." 
            spec__lyx = np.concatenate((spec__lyx, aux__lyx*np.nan  ), axis=1)
            erro__lyx = np.concatenate((erro__lyx, aux__lyx*np.nan  ), axis=1)
            flag__lyx = np.concatenate((flag__lyx, np.int_(aux__lyx)), axis=1)
            mask__yx  = np.concatenate((mask__yx,  aux__yx,         ), axis=0) > 0
    
    if (xdiff != 0):
    
        aux__lyx = np.ones([Nl, nNy, abs(xdiff)])
        aux__yx  = np.zeros([nNy, abs(xdiff)])
    
        # Add array at the beginning of x
        if (xdiff > 0):
            print "@@> Adding array at the beginning of x array for COMBO..." 
            spec__lyx = np.concatenate((aux__lyx*np.nan,   spec__lyx), axis=2)
            erro__lyx = np.concatenate((aux__lyx*np.nan,   erro__lyx), axis=2)
            flag__lyx = np.concatenate((np.int_(aux__lyx), flag__lyx), axis=2)
            mask__yx  = np.concatenate((aux__yx,           mask__yx ), axis=1) > 0
    
        # Add array at the end of x
        if (xdiff < 0):
            print "@@> Adding array at the end of x array for COMBO..." 
            spec__lyx = np.concatenate((spec__lyx, aux__lyx*np.nan  ), axis=2)
            erro__lyx = np.concatenate((erro__lyx, aux__lyx*np.nan  ), axis=2)
            flag__lyx = np.concatenate((flag__lyx, np.int_(aux__lyx)), axis=2)
            mask__yx  = np.concatenate((mask__yx,  aux__yx,         ), axis=1) > 0

    # Recursive trick to deal with the second offset pair
    if (xdiff2 != 0) | (ydiff2 != 0):
        spec__lyx, erro__lyx, flag__lyx, mask__yx = CalifaMatchCombData(ydiff2, xdiff2, 0, 0, spec__lyx, erro__lyx, flag__lyx, mask__yx)

    return spec__lyx, erro__lyx, flag__lyx, mask__yx


def CalifaMatchCombData_SegCube(ydiff, xdiff, ydiff2, xdiff2, segCube__zyx):

    Nz = segCube__zyx.shape[0]
    Ny = segCube__zyx.shape[1]
    Nx = segCube__zyx.shape[2]
    nNy = Ny + abs(ydiff)
    nNx = Nx + abs(xdiff)

    if (ydiff != 0):
    
        aux__zyx = np.zeros([Nz, abs(ydiff), Nx])
        #aux__yx  = np.zeros([abs(ydiff), Nx])
    
        # Add array at the beginning of y
        if (ydiff > 0):
            print "@@> Adding array at the beginning of y array for COMBO..." 
            segCube__zyx = np.concatenate((aux__zyx, segCube__zyx), axis=1)
    
        # Add array at the end of y
        if (ydiff < 0):
            print "@@> Adding array at the end of y array for COMBO..." 
            segCube__zyx = np.concatenate((segCube__zyx, aux__zyx), axis=1)
    
    if (xdiff != 0):
    
        aux__zyx = np.zeros([Nz, nNy, abs(xdiff)])
        #aux__yx  = np.zeros([nNy, abs(xdiff)])
    
        # Add array at the beginning of x
        if (xdiff > 0):
            print "@@> Adding array at the beginning of x array for COMBO..." 
            segCube__zyx = np.concatenate((aux__zyx, segCube__zyx), axis=2)

        # Add array at the end of x
        if (xdiff < 0):
            print "@@> Adding array at the end of x array for COMBO..." 
            segCube__zyx = np.concatenate((segCube__zyx, aux__zyx), axis=2)

    # Recursive trick to deal with the second offset pair
    if (xdiff2 != 0) | (ydiff2 != 0):
        segCube__zyx = CalifaMatchCombData_SegCube(ydiff2, xdiff2, 0, 0, segCube__zyx)

    return segCube__zyx


def old_unique_2d(flag, threshold = None, lambda_axis = 0):
    '''
    Deprecated! ... Usage:

    flagMasked__l = unique_2d( f1__lk, threshold = 20, lambda_axis = 0 )
    
    Function to help with adding flags when adding up pixels / spaxels.

    Ideas and code snippets taken from:
    http://stackoverflow.com/questions/4373631/sum-array-by-number-in-numpy
    http://stackoverflow.com/questions/8560440/removing-duplicate-columns-and-rows-from-a-numpy-2d-array

    Simple tests can be done with:

    f0 = np.array( ([0, 11, 12, 0],
            [0,  0,  0, 0],
            [0, 11, 12, 0],
            [0, 12, 12, 0],
            [0, 23,  0, 20])
         )

    ff = unique_2d( f0 , lambda_axis = 1, threshold = 20 )
    '''

    # Transpose vector if needed, we always assume the lambda axis = 0
    f1 = flag
        
    if (lambda_axis == 1):
        f1 = flag.T

    # Sort flag vectors for each lambda
    sort_indices = np.argsort(f1, axis = 1)
    static_indices = np.indices(f1.shape)
    f2 = f1[static_indices[0], sort_indices]

    # Compare each element in axis = 1 to the one before,
    # mark false if it is a duplicate
    unique = np.ones_like(f1, dtype = 'bool')
    unique[:, :-1] = (f2[:, 1:] != f2[:, :-1])

    # Mask sorted vector, removing duplicates
    f3 = f2 * unique
    #l1 = np.where((f3 > 0).any(axis = 0))[0][0]
    #print 'f3', threshold, l1

    # Sort masked vector to be able to reduce its dimensions
    sort_indices = np.argsort(f3, axis = 1)
    static_indices = np.indices(f3.shape)
    f4 = f3[static_indices[0], sort_indices]

    # Reduce dimension
    l1 = np.where((f4 > 0).any(axis = 0))[0][0]
    f5 = f4[:, l1:]
    #print 'f4', threshold, l1

    # Sum up flags
    f6 = f5.sum(axis = 1)

    # Clean summed flags
    if (threshold != None):
        f1 = f5
        g2 = np.zeros( [f1.shape[0], 4], 'int' )

        # Stupidly going through all combinations
        g0 = (f1 == 20)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 1 ] = 11
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 21)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 2 ] = 12
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 22)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 23)
        g1 = np.where(g0)
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 2 ] = 12
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 24)
        g1 = np.where(g0)
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 25)
        g1 = np.where(g0)
        g2[ g1[0], 2 ] = 12
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 32)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 2 ] = 12
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 33)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 36)
        g1 = np.where(g0)
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 2 ] = 12
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g0 = (f1 == 45)
        g1 = np.where(g0)
        g2[ g1[0], 0 ] =  9
        g2[ g1[0], 1 ] = 11
        g2[ g1[0], 2 ] = 12
        g2[ g1[0], 3 ] = 13
        f1 = np.where(g0, 0, f1)

        g3 = np.concatenate((g2, f1), axis=1)
        f6 = unique_2d(g3, lambda_axis = 0)


    return f6

