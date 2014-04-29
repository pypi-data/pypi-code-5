'''
Created on 07/Jan/2014

@author: Natalia Vale Asari
'''

import numpy as np
import scipy.integrate

# Physical constants & units
c_light = 299792.458  # km/s
Mpc_to_km = 3.08567758e19
s_to_Gyr = 3.15569e7 * 1.e9


class distance(object):
    '''
    Calculate cosmological distances and times according to Hogg 1999
    (H99, http://arXiv.org/abs/astro-ph/9905116).

    The default cosmology is omega_matter = 0.3, omega_lambda = 0.7, h = 0.7; 
    distance units are in Mpc, angles in radians, velocity in km/s, and time in Gyr.

    ----
    Usage / testing:
    import pystarlight.util.cosmo_distances as cdist

    # A plot (see below):
    cdist.plot_redshift_age(1)

    # A few sanity checks:
    cosmology = [0.3, 0.7, 0.7]
    a = cdist.distance(cosmology = cosmology)
    
    print a.z(1., 0.5)
    print a.z1, a.z0
    print a.redshift(1., 0.5)
    print a.z1, a.z0
    print a.redshift_from_velocity(4000)
    print a.z1, a.z0
    print a.z()
    print a.z1, a.z0
    print a.z(1., 0.5)
    print a.z1, a.z0
    print a.z()
    print a.z1, a.z0
    print a.redshift()
    print a.z1, a.z0
    
    a.z(1., 0.)
    print a.DH()
    print a.DC()
    print a.DM()
    print a.DA()
    print a.DL()
    print a.tH()
    print a.tL()
    print a.tA()
    print a.tU()
    '''

    def __init__(self, z1 = None, z0 = 0., cosmology = [0.3, 0.7, 0.7]):

        # Cosmology parameters
        self.cosmology = cosmology
        self.omega_M = cosmology[0]
        self.omega_L = cosmology[1]
        self.h       = cosmology[2]
        self.omega_K = 1. - self.omega_M - self.omega_L
        self.H0      = 100. * self.h  # km/s/Mpc

        # Default values for z0, z1
        self.z1 = z1
        self.z0 = z0
        
        # Give simpler names to distance & time functions
        self.z = self.redshift
        self.z_from_v = self.redshift_from_velocity
        self.DH = self.Hubble_distance
        self.DC = self.comoving_distance
        self.DM = self.comoving_transverse_distance
        self.DA = self.angular_diameter_distance
        self.DL = self.luminosity_distance

        self.tH = self.Hubble_time
        self.tL = self.lookback_time
        self.tA = self.age
        self.tU = self.age_universe

        
    def redshift(self, z1 = None, z0 = None):

        # Get default values for z0, z1
        if (z0 is None):
            z0 = self.z0

        if (z1 is None):
            z1 = self.z1

        # Check if everything is in place: z0 is usually 'here' (z0 = 0)
        if (z0 > z1):
            z0, z1 = z1, z0
        self.z1 = z1
        self.z0 = z0

        # H99, eq. 13
        z = -1. + ( (1. + z1) / (1. + z0) )
        
        return z


    def redshift_from_velocity(self, v, z0 = 0.):
        
        # H99, eq. 9
        z1 = -1. + np.sqrt( (1. + v / c_light) / (1. - v / c_light) )
        z = self.redshift(z1, z0)

        return z

    
    def Hubble_distance(self):

        # H99, eq. 4
        DH = c_light / self.H0

        return DH

    
    def comoving_distance(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 15
        int_invEz = scipy.integrate.quad( self._inv_Ez, 0., z, ([self.omega_M, self.omega_K, self.omega_L]) )[0]
        DC = self.DH() * int_invEz
        
        return DC

    
    def comoving_transverse_distance(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # We need Hubble and comoving distance
        DC = self.comoving_distance()
        DH = self.DH()

        # H99, eq. 15
        abs_ok = abs(self.omega_K)
        if (self.omega_K > 0.):
            DM = DH * np.sinh( np.sqrt(abs_ok) * DC / DH ) / np.sqrt(abs_ok)
        elif (self.omega_K < 0.):
            DM = DH * np.sin(  np.sqrt(abs_ok) * DC / DH ) / np.sqrt(abs_ok)
        else:
            DM = DC

        return DM
    

    def angular_diameter_distance(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 18; DA = [ Mpc / rad ]
        DM = self.comoving_transverse_distance()
        DA = DM / (1. + z)
        
        return DA

    
    def luminosity_distance(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 21
        DM = self.comoving_transverse_distance()
        DL = (1. + z) * DM

        return DL


    def Hubble_time(self):
        
        # H99, eq. 3
        tH = (1. / self.H0) * (Mpc_to_km / s_to_Gyr)

        return tH
    

    def lookback_time(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 30
        tH = self.Hubble_time()
        int_invEz_1pZ = scipy.integrate.quad( self._inv_Ez_1pZ, 1., 1./(1.+z), ([self.omega_M, self.omega_K, self.omega_L]) )[0]
        tL = tH * int_invEz_1pZ

        return tL

    
    def age(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 30
        tH = self.Hubble_time()
        int_invEz_1pZ = scipy.integrate.quad( self._inv_Ez_1pZ, 1./(1.+z), 0., ([self.omega_M, self.omega_K, self.omega_L]) )[0]
        tA = tH * int_invEz_1pZ
        
        return tA


    def age_universe(self, z1 = None, z0 = None):

        z = self.redshift(z1, z0)

        # H99, eq. 30
        tH = self.Hubble_time()
        int_invEz_1pZ = scipy.integrate.quad( self._inv_Ez_1pZ, 1., 0., ([self.omega_M, self.omega_K, self.omega_L]) )[0]
        tU = tH * int_invEz_1pZ
        
        return tU

    
    def _inv_Ez(self, _z, (om, ok, ol)):

        # H99, eq. 14
        inv_Ez = ( om * (1. + _z)**3. + ok * (1. + _z)**2. + ol )**(-0.5)
        
        return inv_Ez

    
    def _inv_Ez_1pZ(self, x, (om, ok, ol)):

        # H99, eq. 30
        # Integrating on x = 1/(1 + z')
        # z = 0   ==> x = 1
        # z = inf ==> x = 0
        inv_Ez_1pZ = - ( x / (om + ok * x + ol * x**3) )**(0.5)
            
        return inv_Ez_1pZ



'''
Some useful plots
'''

def plot_redshift_age(Nfig = 1):

    import matplotlib.pyplot as plt
    from matplotlib import rc

    rc('text', usetex=True)
    rc('font', family='serif')

    plt.figure(Nfig)
    plt.clf()

    cosmology = [0.3, 0.7, 0.7]
    a = distance(cosmology = cosmology)

    zs = np.linspace(0., 6., 100)
    tAs = [a.tA(z) for z in zs]
    tLs = [a.tL(z) for z in zs]

    plt.plot(zs, tAs, 'k-',  label = 'age')
    plt.plot(zs, tLs, 'k--', label = 'lookback time')

    plt.xlabel('redshift')
    plt.ylabel('t [Gyr]')

    plt.legend(loc='upper right', frameon=False)
    
    '''
    '''

