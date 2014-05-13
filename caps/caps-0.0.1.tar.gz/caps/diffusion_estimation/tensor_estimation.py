#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import division
import numpy
import os
import scipy.optimize
import nibabel
import itertools

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (List, Bool, File, Int, Str, Float, Directory)
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import (List, Bool, File, Int, Str,
                                      Float, Directory)

# Capsul import
from capsul.process import Process

# Caps import
from monomials import construct_matrix_of_monomials
from polynomials import construct_set_of_polynomials
from integrals import construct_matrix_of_integrals
from caps.diffusion_estimation.resources import get_sphere
from diffusion_multiprocessing import multi_processing


##############################################################
#               OLS Estimation Process definition
##############################################################

class LSTensorEstimation(Process):
    """ Ordinary least square tensor fiting

    Fits a diffusion tensor given diffusion-weighted signals and
    gradient info using a least square strategy [1]_.

    .. hidden-technical-block::
        :label: [+show/hide ols fit details]
        :starthidden: True

        .. include:: source/_static/technical_documentation/diffusion_estimation_ols.txt

    References
    ----------

    .. [1] Mori, S., 2007. Introduction to Diffusion Tensor Imaging.
           Elsevier.
    """

    def __init__(self):
        """ Initialize LSTensorEstimation class
        """
        # Inheritance
        super(LSTensorEstimation, self).__init__()

        # Inputs
        self.add_trait("dwi_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="an existing diffusion weighted image"))
        self.add_trait("bvals_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the the diffusion b-values"))
        self.add_trait("bvecs_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the the diffusion b-vectors"))
        self.add_trait("model_order", Int(
            2,
            optional=False,
            output=False,
            exists=True,
            desc="the estimated model order (even)"))
        self.add_trait("mask_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a mask image"))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor model will be "
                  "written")))
        self.add_trait("model_name", Str(
            "tensor",
            optional=True,
            output=False,
            desc=("the name of the output tensor model file")))
        self.add_trait("estimate_odf", Bool(
            False,
            optional=True,
            output=False,
            desc="estimate the odf"))

        # Outputs
        self.add_trait("tensor_file", File(
            output=True,
            desc="the result file containing the tensor model coefficients"))

        # Intern parameters
        # Replace diffusion signal smaller than this threshold in order to
        # avoid taking log(0) during the ols estimation
        self.min_signal = 1

    def _run_process(self):
        """ LSTensorEstimation execution code
        """
        # Load
        self.load_dataset()

        # Estimation
        if self.estimate_odf:
            raise Exception("OLS ODF estimation not yet implemented")
        else:
            dti_parameters_flat = self.ols_tensor_fit()

        # Save
        self.dti_parameters = dti_parameters_flat.reshape(
            self.shape[:-1] + (self.e, ))
        dti_image = nibabel.Nifti1Image(self.dti_parameters,
                                        affine=self.dwi.get_affine())
        tensor_file = os.path.join(self.output_directory,
                                   self.model_name + ".nii.gz")
        dti_image.to_filename(tensor_file)
        self.tensor_file = tensor_file

    def load_dataset(self):
        """ Load the diffusion dataset
        """
        # Load
        self.dwi = nibabel.load(self.dwi_file)
        self.bvals = numpy.loadtxt(self.bvals_file)
        self.bvecs = numpy.loadtxt(self.bvecs_file)
        data = numpy.asarray(self.dwi.get_data())
        self.shape = data.shape
        if isinstance(self.mask_file, _Undefined):
            mask = numpy.ones(self.shape[:-1], dtype=bool)
        else:
            mask = numpy.array(nibabel.load(self.mask_file).get_data(),
                               dtype=bool, copy=False)
        # data_in_mask = data[self.mask]
        self.mask_flat = mask.reshape((-1,))
        self.data_flat = data.reshape((-1, data.shape[-1]))

        # Check parameters
        if self.bvecs.shape[1] != 3 and self.bvecs.shape[0] == 3:
            self.bvecs = self.bvecs.T
        if self.model_order % 2 == 1:
            raise Exception("An even model order is expected, got "
                            "{0}".format(self.model_order))

    def ols_tensor_fit(self):
        """ Fits a diffusion tensor given diffusion-weighted signals and
        gradient info using a least square strategy.

        The ordinary least squares do not ensure the positive nature of tensors

        Returns
        -------
        dti_parameters: array [N, e]
            the tensor independant coefficients
            be careful, multiplicity is include in tensors.

       Reference
           Basser, P., Pierpaoli, C., 1996. Microstructural and physiological
           features of tissues elucidated by quantitative diffusion-tensor MRI.
           Journal of Magnetic Resonance 111, 209-219.
        """
        # Get polynomial basis
        B = -construct_matrix_of_monomials(self.bvecs, self.model_order)
        self.e = B.shape[1]
        # Bvals
        for col_index in range(B.shape[1]):
            B[:, col_index] *= self.bvals
        # Add dummy col
        dummy_col = numpy.ones((self.bvecs.shape[0], 1))
        B = numpy.append(B, dummy_col, 1)

        # Invert design matrix
        Binv = numpy.linalg.pinv(B)

        # Allocate
        dti_parameters = numpy.zeros((len(self.data_flat), self.e))

        # OLS
        for dti_parameter, dw_signal, in_mask in zip(dti_parameters,
                                                     self.data_flat,
                                                     self.mask_flat):
            if in_mask:
                # Throw out small signals
                dw_signal = numpy.maximum(dw_signal, self.min_signal)
                # Adc
                y = numpy.log(dw_signal)
                # OLS fit
                dti_parameter[:] = numpy.dot(Binv, y)[:-1]

        return dti_parameters


##############################################################
#               QUARTIC Estimation Process definition
##############################################################


class QUARTICTensorEstimation(Process):
    """ Fits a diffusion tensor given diffusion-weighted signals and
    gradient info using a quartic decomposition and non negative least square
    estimation strategy [1]_.

    **References**

    .. [1] A. Barmpoutis et B. Vermuri : A unified framework
           for estimating diffusion tensors of any order with
           symmetric positive-definite constraints.
           In IEEE Internaional Symposium on Biomedical
           Imaging, Rotterdam, ISBI, p1385-1388, 2010.
    """

    def __init__(self):
        """ Initialize QUARTICTensorEstimation class
        """
        # Inheritance
        super(QUARTICTensorEstimation, self).__init__()

        # Inputs
        self.add_trait("dwi_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="an existing diffusion weighted image"))
        self.add_trait("reference_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the referecne b=0 image"))
        self.add_trait("bvals_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the the diffusion b-values"))
        self.add_trait("bvecs_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the the diffusion b-vectors"))
        self.add_trait("model_order", Int(
            2,
            optional=False,
            output=False,
            exists=True,
            desc="the estimated model order (even)"))
        self.add_trait("mask_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a mask image"))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor model will be "
                  "written")))
        self.add_trait("model_name", Str(
            "tensor",
            optional=True,
            output=False,
            desc=("the name of the output tensor model file")))
        self.add_trait("number_of_workers", Int(
            1,
            optional=True,
            output=False,
            desc="the number of CPUs to use during the execution"))
        self.add_trait("estimate_odf", Bool(
            False,
            optional=True,
            output=False,
            desc="estimate the odf"))

        # Outputs
        self.add_trait("tensor_file", File(
            output=True,
            desc="the result file containing the tensor model coefficients"))

        # Intern parameters
        # # Replace diffusion signal smaller than this threshold in order to
        # # avoid taking log(0) during the ols estimation
        self.min_signal = 1
        # # Odf kernel
        self.delta = 100.

    def _run_process(self):
        """ LSTensorEstimation execution code
        """
        # Load
        self.load_dataset()

        # Estimation
        if self.estimate_odf:
            dti_parameters_flat = self.quartic_tensor_odf_fit()
        else:
            dti_parameters_flat = self.quartic_tensor_fit()

        # Save
        self.dti_parameters = dti_parameters_flat.reshape(
            self.shape[:-1] + (self.e, ))
        dti_image = nibabel.Nifti1Image(self.dti_parameters,
                                        affine=self.dwi.get_affine())
        tensor_file = os.path.join(self.output_directory,
                                   self.model_name + ".nii.gz")
        dti_image.to_filename(tensor_file)
        self.tensor_file = tensor_file

    def load_dataset(self):
        """ Load the diffusion dataset
        """
        # Load
        self.dwi = nibabel.load(self.dwi_file)
        self.reference = nibabel.load(self.reference_file)
        self.bvals = numpy.loadtxt(self.bvals_file)
        self.bvecs = numpy.loadtxt(self.bvecs_file)
        data = numpy.asarray(self.dwi.get_data())
        reference_data = numpy.asarray(self.reference.get_data())
        self.shape = data.shape
        if isinstance(self.mask_file, _Undefined):
            mask = numpy.ones(self.shape[:-1], dtype=bool)
        else:
            mask = numpy.array(nibabel.load(self.mask_file).get_data(),
                               dtype=bool, copy=False)
        # data_in_mask = data[self.mask]
        self.mask_flat = mask.reshape((-1,))
        self.data_flat = data.reshape((-1, data.shape[-1]))
        self.reference_flat = reference_data.reshape((-1,))

        # Check parameters
        if self.bvecs.shape[1] != 3 and self.bvecs.shape[0] == 3:
            self.bvecs = self.bvecs.T
        if self.model_order % 2 == 1:
            raise Exception("An even model order is expected, got "
                            "{0}".format(self.model_order))

    def quartic_tensor_fit(self):
        """ Fits a diffusion tensor given diffusion-weighted signals and
        gradient info using a quartic decomposition and non negative least
        square estimation strategy.

        This procedure guarentees the positive-definite or at least positive
        semi-definite nature of tensors.

        Returns
        -------
        dti_parameters: array [N, e]
            the tensor independant coefficients
            be careful, multiplicity is include in tensors.

       Reference
           Barmpoutnis
        """
        # Construct b diag
        b_diag = numpy.diag(self.bvals)

        # construct basis
        G = construct_matrix_of_monomials(self.bvecs, self.model_order)
        C = construct_set_of_polynomials(self.model_order).T
        P = numpy.dot(G, C)
        P = numpy.dot(- b_diag, P)
        self.e = G.shape[1]

        # Allocate
        dti_parameters = numpy.empty((len(self.data_flat), self.e))

        # NNLS
        nb_cpus = None
        if self.number_of_workers > 0:
            nb_cpus = self.number_of_workers
        results = multi_processing(
            nnls_multi, nb_cpus,
            self.data_flat, self.reference_flat,
            itertools.repeat(P), itertools.repeat(C),
            itertools.repeat(self.min_signal), self.mask_flat,
            itertools.repeat(True))

        # dti_parameters = numpy.asarray(results)
        for cnt, item in enumerate(results):
            dti_parameters[cnt] = item

        return dti_parameters

    def quartic_tensor_odf_fit(self):
        """ Compute a Cartesian tensor Odf from a given DW dataset.

        Returns
        -------
        dti_parameters: array [N, e]
            the odf tensor independant coefficients
            be careful, multiplicity is include in tensors.

       Reference
           Barmpoutnis
        """
        # Contruct basis
        C = construct_set_of_polynomials(self.model_order).T
        BG = construct_matrix_of_integrals(self.bvecs, self.model_order,
                                           self.delta)
        B = numpy.dot(BG, C)
        self.e = C.shape[0]

        # Allocate
        dti_parameters = numpy.empty((len(self.data_flat), self.e))

        # NNLS
        nb_cpus = None
        if self.number_of_workers > 0:
            nb_cpus = self.number_of_workers
        results = multi_processing(
            nnls_multi, nb_cpus,
            self.data_flat, self.reference_flat,
            itertools.repeat(B), itertools.repeat(C),
            itertools.repeat(self.min_signal), self.mask_flat,
            itertools.repeat(False))

        # dti_parameters = numpy.asarray(results)
        for cnt, item in enumerate(results):
            dti_parameters[cnt] = item

        return dti_parameters


def nnls_multi(parameters):
    return nnls_iter(*parameters)


def nnls_iter(dw_signal, ref_signal, P, C, min_signal, in_mask, take_log):
    """ NNLS tensor fit
    """
    if in_mask:
        # Throw out small signals
        dw_signal = numpy.maximum(dw_signal, min_signal)
        ref_signal = numpy.maximum(ref_signal, min_signal)
        # Signal
        y = dw_signal / ref_signal
        if take_log:
            y = numpy.log(y)
        # NNLS fit
        x = scipy.optimize.nnls(P, y)[0]
        # Tensor
        return numpy.dot(C, x)
    else:
        return numpy.zeros((C.shape[0], ))


def tensor2odf(tensors, b, order):
    """ Compute a Cartesian Tensor ODF from a given Higher-order diffusion
    tensor
    Parameters
    ----------
    tensors: list of array [e,] (mandatory)
        a list with tensor independent coefficients
    b: float (mandatory)
        the diffusion b-value

    Returns
    -------
    odfs list of array [e,]
        a list of tensor independant coefficients

    Reference
        Barmpoutnis
    """
    # Unit vectors [321,3]
    g = numpy.loadtxt(get_sphere("symmetric321"))

    # Construct basis
    G = construct_matrix_of_monomials(g, order)
    C = construct_set_of_polynomials(order).T
    BG = construct_matrix_of_integrals(g, order, 100)
    B = numpy.dot(BG, C)

    # loop over elements
    odfs = []
    for tensor in tensors:
        x = scipy.optimize.nnls(B, numpy.exp(-b * numpy.dot(G, tensor)))[0]
        odfs.append(numpy.dot(C, x))

    return odfs


def print_tensor(tensor, order):
    """ Print the tensor coefficients

    Parameters
    ----------
    tensor: array [e,] (mandatory)
        the tensor independent coefficients
    order: odd int (mandatory)
        the tensor order
    """
    c = 0
    for i in range(order + 1):
        for j in range(order + 1 - i):
            print ("D (x,y,z)=({0},{1},{2}) - Coefficient: "
                   "{3}".format(i, j, order - i - j, tensor[c]))
            c = c + 1

if __name__ == "__main__":

    from caps.toy_datasets import get_sample_data
    toy_dataset = get_sample_data("dwi")

    ls_estimator = LSTensorEstimation()
    ls_estimator.dwi_file = toy_dataset.dwi
    ls_estimator.bvals_file = toy_dataset.bvals
    ls_estimator.bvecs_file = toy_dataset.bvecs
    ls_estimator.output_directory = "/volatile/nsap/caps/diffusion_estimation"

    # ls_estimator._run_process()

    # print stop

    import fvtk

    b = 1500
    order = 2
    S0 = 1
    g = numpy.array([
        [0.1639, 0.5115, 0.8435],
        [0.1176, -0.5388, 0.8342],
        [0.5554, 0.8278, -0.0797],
        [-0.4804, 0.8719, 0.0948],
        [0.9251, -0.0442, 0.3772],
        [0.7512, -0.0273, -0.6596],
        [0.1655, -0.0161, 0.9861],
        [0.6129, -0.3427, 0.7120],
        [0.6401, 0.2747, 0.7175],
        [-0.3724, -0.3007, 0.8780],
        [-0.3451, 0.3167, 0.8835],
        [0.4228, 0.7872, 0.4489],
        [0.0441, 0.9990, 0.0089],
        [-0.1860, 0.8131, 0.5515],
        [0.8702, 0.4606, 0.1748],
        [-0.7239, 0.5285, 0.4434],
        [-0.2574, -0.8032, 0.5372],
        [0.3515, -0.8292, 0.4346],
        [-0.7680, -0.4705, 0.4346],
        [0.8261, -0.5384, 0.1660],
        [0.9852, -0.0420, -0.1660]])

    dwi = []
    # fiber1 = (pi/2,100*pi/180) - fiber2 = (pi/2,20*pi/180)
    dwi.append(numpy.array([
        0.39481, 0.43774, 0.12879, 0.31532, 0.31744,
        0.36900, 0.59490, 0.35280, 0.36880, 0.44046, 0.48088,
        0.17118, 0.22700, 0.34665, 0.26000, 0.25414, 0.21642,
        0.34456, 0.26625, 0.20723, 0.30364]) * 1e-3)

    # fiber1 = (pi/2,0) - fiber2 = (pi/2,pi/2)
    dwi.append(numpy.array([0.43670, 0.43596, 0.18206, 0.20415, 0.33573,
                            0.37296, 0.59236, 0.33340, 0.34970, 0.45040,
                            0.45559, 0.24635, 0.32270, 0.33154, 0.21289,
                            0.21758, 0.30981, 0.26820, 0.23028, 0.18931,
                            0.32519]) * 1e-3)

    # fiber1 = (pi/2,0) - fiber2 = (pi/4,pi/2)
    dwi.append(numpy.array([
        0.30972, 0.56842, 0.27685, 0.24966, 0.29334,
        0.22803, 0.37018, 0.36464, 0.18036, 0.40585,
        0.26687, 0.22845, 0.38253, 0.30230, 0.21773,
        0.15808, 0.53451, 0.46730, 0.36886, 0.30290,
        0.30921]) * 1e-3)

    # fiber1 = (pi/2,pi/8) - fiber2 = (pi/2,3*pi/8)
    dwi.append(numpy.array([0.36248, 0.47541, 0.06924, 0.40454, 0.28182,
                            0.33958, 0.59539, 0.48527, 0.23793, 0.36287,
                            0.56245, 0.11984, 0.21594, 0.37846, 0.08456,
                            0.44135, 0.18359, 0.41061, 0.10898, 0.41320,
                            0.26074]) * 1e-3)

    # one fiber (1,0,0)
    dwi.append(numpy.array([0.57138, 0.59235, 0.26610, 0.32803, 0.06001,
                            0.13251, 0.57054, 0.22062, 0.20057, 0.42144,
                            0.44422, 0.37747, 0.61147, 0.55894, 0.08094,
                            0.14717, 0.51133, 0.43896, 0.12416, 0.09872,
                            0.03862]) * 1e-3)

    # one fiber (0,1,0)
    dwi.append(numpy.array([0.30201, 0.27957, 0.09802, 0.08027, 0.61146,
                            0.61340, 0.61418, 0.44618, 0.49883, 0.47935,
                            0.46697, 0.11523, 0.03394, 0.10413, 0.34484,
                            0.28799, 0.10829, 0.09744, 0.33641, 0.27990,
                            0.61176]) * 1e-3)

    refi = [S0 * 1e-3, ] * len(dwi)

    # Estimation
    lstensors = nnls_tensor_estimation_2(dwi, refi, g, b, order)
    nnlstensors = nnls_tensor_estimation(dwi, refi, g, b, order)
    # pipe_odfs = tensor2odf(lstensors, b, order)
    # odfs = nnls_tensor_odf_estimation(dwi, refi, g, b, order)

    print "Tensor:"
    for tensornnls, tensorls in zip(nnlstensors, lstensors):
        print "ls:"
        print_tensor(tensorls, order)
        print "nnls:"
        print_tensor(tensornnls, order)

    print stop

    print "ODF:"
    for odf, pipe_odf in zip(odfs, pipe_odfs):
        print "odf:"
        print_tensor(odf, order)
        print "pipe odf:"
        print_tensor(pipe_odf, order)

    # Plot
    ren = fvtk.ren()
    for cnt_row, row_tensors in enumerate((nnlstensors, lstensors, odfs,
                                           pipe_odfs)):
        for cnt_col, tensor_coeff in enumerate(row_tensors):
            actor = fvtk.tensor(tensor_coeff, order,
                                position=(cnt_row, cnt_col, 0))
            fvtk.add(ren, actor)
    fvtk.show(ren)