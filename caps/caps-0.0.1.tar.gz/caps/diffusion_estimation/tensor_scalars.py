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
import numpy as numpy
import logging
import nibabel
import os

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


##############################################################
#      Second Order Tensor Parameters Process definition
##############################################################

class SecondOrderScalarParameters(Process):
    """ Compute the Fractional Anisotropy [1]_ (FA),
    Mean Diffusivity (MD) and the Westion Shapes coefficients [1]_
    (cl, cp, cs) of a second order tensor.
    
    .. hidden-technical-block::
        :label: [+show/hide second order tensor scalars]
        :starthidden: True

        .. include:: source/_static/technical_documentation/dt2_scalars.txt

    **References**

    .. [1] C. Westin, S. Maier, H. Mamata, A. Nabavi, F. Jolesz and
           R. Kikinis : Processing and visualization of diffusion tensor
           MRI. Medical Image Analysis, 6(2):93-108, 2002.
    """

    def __init__(self):
        """ Initialize SecondOrderScalarParameters class
        """
        # Inheritance
        super(SecondOrderScalarParameters, self).__init__()

        # Inputs
        self.add_trait("eigenvalues_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a second order tensor eigen values"))
        self.add_trait("fa_basename", Str(
            "fa",
            optional=True,
            output=False,
            desc=("the basename of the output fa file")))
        self.add_trait("md_basename", Str(
            "md",
            optional=True,
            output=False,
            desc=("the basename of the output md file")))
        self.add_trait("cl_basename", Str(
            "cl",
            optional=True,
            output=False,
            desc=("the basename of the output linearity coefficients file")))
        self.add_trait("cp_basename", Str(
            "cp",
            optional=True,
            output=False,
            desc=("the basename of the output planarity coefficients file")))
        self.add_trait("cs_basename", Str(
            "cs",
            optional=True,
            output=False,
            desc=("the basename of the output sphericity coefficients file")))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor scalars will be "
                 "written")))
        # Ouputs
        self.add_trait("fractional_anisotropy_file", File(
            output=True,
            desc=("the name of the output fa file")))
        self.add_trait("mean_diffusivity_file", File(
            output=True,
            desc=("the name of the output md file")))
        self.add_trait("linearity_file", File(
            output=True,
            desc=("the name of the fie that contains the linerity "
                  "coefficients")))
        self.add_trait("planarity_file", File(
            output=True,
            desc=("the name of the fie that contains the planarity "
                  "coefficients")))
        self.add_trait("sphericity_file", File(
            output=True,
            desc=("the name of the fie that contains the sphericity "
                  "coefficients")))

    def _run_process(self):
        """ SecondOrderScalarParameters execution code
        """
        # Load
        self.eigenvalues = nibabel.load(self.eigenvalues_file)
        self.eigenvalues_array = numpy.asarray(self.eigenvalues.get_data())
        self.shape = self.eigenvalues_array.shape
        if self.shape[-1] != 3:
            raise Exception("Expect second order tensor eiganvalues with 3 "
                            "parameters (...,3), got "
                            "{0}".format(self.shape))

        # Get scalar parameters
        (fa_array, md_array ,cl_array, cp_array,
         cs_array) = self.compute_second_order_scalar_parameters()

        # Save scalar images
        for array, basename, out_trait_name in [
            (fa_array, self.fa_basename, "fractional_anisotropy_file"),
            (md_array, self.md_basename, "mean_diffusivity_file"),
            (cl_array, self.cl_basename, "linearity_file"),
            (cp_array, self.cp_basename, "planarity_file"),
            (cs_array, self.cs_basename, "sphericity_file")]:

            # Create a nifti image from the scalar array
            image = nibabel.Nifti1Image(
                array, affine=self.eigenvalues.get_affine())
            # Generate the output file name
            out_file = os.path.join(
                self.output_directory, basename + ".nii.gz")
            # Save the image to the output file name
            image.to_filename(out_file)
            # Update output trait
            setattr(self, out_trait_name, out_file)

    def compute_second_order_scalar_parameters(self):
        r""" Compute the Fractional Anisotropy [1]_ (FA),
        Mean Diffusivity (MD) and the Westion Shapes coefficients [1]_
        (cl, cp, cs) of a second order tensor.

        Returns
        -------
        fa: array [...,]
            fractional anisotropy
        md: array [...,]
            mean diffusivity
        cl: array [...,]
            linearity coefficient
        cp: array [...,]
            planarity coefficient
        cs: array [...,]
            sphericity coefficient
        """

        ev1 = self.eigenvalues_array[..., 0]
        ev2 = self.eigenvalues_array[..., 1]
        ev3 = self.eigenvalues_array[..., 2]
        all_zero = (self.eigenvalues_array == 0).all(axis=-1)
        ev2 = ev1*ev1 + ev2*ev2 + ev3*ev3 + all_zero

        # md
        md = numpy.mean(self.eigenvalues_array, axis=3)

        # fa
        fa = numpy.sqrt(0.5 * ((ev1 - ev2) ** 2 + (ev2 - ev3) ** 2 +
                               (ev3 - ev1) ** 2)
                               / ev2)

        # cl
        cl = (ev1 - ev2) / numpy.sqrt(ev2)

        # cp
        cp = 2 * (ev2 - ev3) / numpy.sqrt(ev2)

        # cs
        cs = 3 * ev3 / numpy.sqrt(ev2)

        return fa, md, cl, cp, cs


##############################################################
#      Fourth Order Tensor Parameters Process definition
##############################################################

class FourthOrderScalarParameters(Process):
    r""" Compute the Generalized Anisotropy (GA) and
    Meand Diffusivity (MD) of fourth order tensors.
    """

    def __init__(self):
        """ Initialize FourthOrderScalarParameters class
        """
        # Inheritance
        super(FourthOrderScalarParameters, self).__init__()

        # Inputs
        self.add_trait("tensor_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a fourth order tensor model"))
        self.add_trait("mask_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a mask image"))
        self.add_trait("ga_basename", Str(
            "ga",
            optional=True,
            output=False,
            desc=("the basename of the output ga file")))
        self.add_trait("md_basename", Str(
            "md",
            optional=True,
            output=False,
            desc=("the basename of the output md file")))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor scalars will be "
                 "written")))
        # Ouputs
        self.add_trait("generalized_anisotropy_file", File(
            output=True,
            desc=("the name of the output fa file")))
        self.add_trait("mean_diffusivity_file", File(
            output=True,
            desc=("the name of the output md file")))

        # Intern parameters
        ## The state of the art GA regularization parameters
        self.k1 = 5000.
        self.k2 = 250.

    def _run_process(self):
        """ FourthOrderScalarParameters execution code
        """
        # Load
        self.tensor = nibabel.load(self.tensor_file)
        data = numpy.asarray(self.tensor.get_data())
        self.shape = data.shape
        if self.shape[-1] != 15:
            raise Exception("Expect fourth order tensor coefficients "
                            "(...,15), got {0}".format(self.shape))
        if isinstance(self.mask_file, _Undefined):
            mask = numpy.ones(self.shape[:-1], dtype=bool)
        else:
            mask = numpy.array(nibabel.load(self.mask_file).get_data(),
                                    dtype=bool, copy=False)
        self.mask_flat = mask.reshape((-1,))
        self.data_flat = data.reshape((-1, data.shape[-1]))

        # Get GA and MD parameters
        ga_array, md_array = self.compute_fourth_order_scalar_parameters()
        ga_array = ga_array.reshape(self.shape[:-1])
        md_array = md_array.reshape(self.shape[:-1])

        # Save
        ga_image = nibabel.Nifti1Image(ga_array,
                                       affine=self.tensor.get_affine())
        generalized_anisotropy_file = os.path.join(
            self.output_directory, self.ga_basename + ".nii.gz")
        ga_image.to_filename(generalized_anisotropy_file)
        self.generalized_anisotropy_file = generalized_anisotropy_file
        md_image = nibabel.Nifti1Image(md_array,
                                       affine=self.tensor.get_affine())
        mean_diffusivity_file = os.path.join(
            self.output_directory, self.md_basename + ".nii.gz")
        md_image.to_filename(mean_diffusivity_file)
        self.mean_diffusivity_file = mean_diffusivity_file

    def compute_fourth_order_scalar_parameters(self):
        """ Compute the Generalized Anisotropy (GA) and Meand Diffusivity (MD)
        of fourth order tensors

        Returns
        -------
        fas: array [N,]
            fractional anisotropy
        mds: array [N]
            mean diffusivity

        Reference
            Ozarslan and Barmpoutnis
        """
        gas = numpy.zeros((len(self.data_flat), 1))
        mds = numpy.zeros((len(self.data_flat), 1))
        for tensor, ga, md, in_mask in zip(self.data_flat, gas, mds,
                                           self.mask_flat):
            if in_mask:
                md[:] = 0.2 * (tensor[14] + tensor[4] + tensor[0] + 1 / 3 *
                              (tensor[11] + tensor[2] + tensor[9]))
                dist = Hellinger(tensor,
                                 numpy.zeros((15, ), dtype=numpy.single))
                # variance of the normalized diffusivities as a measure of
                # anisotropy
                if md > 0:
                    var = 1 / 9 * (dist / md ** 2 - 1)
                    epsi = 1 + 1 / (1 + self.k1 * var)
                    ga[:] = 1 - 1 / (1 + (self.k2 * var) ** epsi)

        return gas, mds


def Hellinger(D1, D2):
    """ Compute a distance measure between 4th order diffusion tensor
    D1 and D2 by computing the normalized L2 distance between the
    corresponding diffusivity functuions d1(g) and d2(g)

    Parameters
    ----------
    D1: array [15,]
        4th order diffusion tensor
    D2: array [15,]
        4th order diffusion tensor

    Returns
    -------
    dist: float
        Hellinger distance
    """
    diff = D1 - D2
    dist = 0.0

    a = 1 / 9
    b = 1 / 105
    c = 1 / 63
    d = 1 / 315

    dist += d * (diff[14] + diff[4] + diff[0] + diff[11] + diff[2] +
                 diff[9]) ** 2
    dist += (b - d) * (diff[14] + diff[4] + diff[0]) ** 2
    dist += (c - d) * ((diff[14] + diff[11]) ** 2 + (diff[14] + diff[9]) ** 2)
    dist += (c - d) * ((diff[4] + diff[11]) ** 2 + (diff[4] + diff[2]) ** 2)
    dist += (c - d) * ((diff[0] + diff[2]) ** 2 + (diff[0] + diff[9]) ** 2)
    dist += (a - b - 2 * (c - d)) * (diff[14] ** 2 + diff[4] ** 2 +
                                     diff[0] ** 2)
    dist += (b - d - 2 * (c - d)) * (diff[11] ** 2 + diff[2] ** 2 +
                                     diff[9] ** 2)
    dist += d * (diff[10] + diff[3] + diff[1]) ** 2
    dist += d * (diff[7] + diff[12] + diff[5]) ** 2
    dist += d * (diff[6] + diff[13] + diff[8]) ** 2
    dist += (b - d) * ((diff[13] + diff[8]) ** 2 + (diff[12] + diff[5]) ** 2 +
                      (diff[3] + diff[1]) ** 2)
    dist += (c - b) * (diff[13] ** 2 + diff[12] ** 2 + diff[8] ** 2 +
                       diff[3] ** 2 + diff[5] ** 2 + diff[1] ** 2)

    return dist


if __name__ == "__main__":

    scalar = SecondOrderScalarParameters()
    scalar.eigenvalues_file = "/volatile/nsap/caps/diffusion_estimation/eigenvals.nii.gz"
    scalar.output_directory = "/volatile/nsap/caps/diffusion_estimation"

    scalar._run_process()

    print stop

    # fourth order tensor
    tensor = numpy.zeros((15, ), dtype=numpy.single)
    # isotropic diffusion
    d = 0.001
    tensor[:3] = d
    tensor[3:6] = 2 * d
    print tensor

    gas, mds = compute_fourth_order_scalar_parameters([tensor, ])
    print gas
    print mds

    # second order tensor
    tensor = numpy.zeros((6, ), dtype=numpy.single)
    # isotropic diffusion
    d = 0.001
    tensor[:3] = d
    print tensor

    fas, mds = compute_second_order_scalar_parameters([tensor, ])
    print fas
    print mds
