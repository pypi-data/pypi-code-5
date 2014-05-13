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
import nibabel

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, Int, Str, Directory)
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import (File, Int, Str, Directory)

# Capsul import
from capsul.process import Process


class DecomposeSecondOrderTensor(Process):
    r""" Compute the eigenvalues and eigenvectors of a given diffusion tensor.
    
    .. math::
        
        \textbf{D} = [ \vec{e_{1}}, \vec{e_{2}}, \vec{e_{3}} ]
                     diag[\lambda_{1}, \lambda_{2}, \lambda_{3}]
                     [ \vec{e_{1}}, \vec{e_{2}}, \vec{e_{3}} ]^{-t} = 
                     \textbf{U} \textbf{V} \textbf{U}^{-t}
                     
    .. math::
        \textbf{D} = \sum_{i=1}^{3} \lambda_i \vec{e_i} \vec{e_i}^{T}
    """

    def __init__(self):
        """ Initialize DecomposeSecondOrderTensor class
        """
        # Inheritance
        super(DecomposeSecondOrderTensor, self).__init__()

        # Inputs
        self.add_trait("tensor_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a second order tensor model"))
        self.add_trait("eigenvecs_basename", Str(
            "eigenvecs",
            optional=True,
            output=False,
            desc=("the basename of the output eigen vectors file")))
        self.add_trait("eigenvals_basename", Str(
            "eigenvals",
            optional=True,
            output=False,
            desc=("the basename of the output eigen values file")))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor eigenvalues and "
                  "eigenvectors will be written")))
        self.add_trait("number_of_workers", Int(
            1,
            optional=True,
            output=False,
            desc="the number of CPUs to use during the execution"))

        # Ouputs
        self.add_trait("eigen_values_file", File(
            output=True,
            desc=("the name of the output eigen values file")))
        self.add_trait("eigen_vectors_file", File(
            output=True,
            desc=("the name of the output eigen vectors file")))

        # Intern parameters
        # Negative or null diffusivity values are not physical
        # This threshold guarantee the positive nature of the diffusivity
        # value
        # It also avoid taking log(0) during the tensor log transformation
        self.min_diffusivity = 1e-8

    def _run_process(self):
        """ SecondOrderScalarParameters execution code
        """
        # Load
        self.dti_parameters = nibabel.load(self.tensor_file)
        dt6_array = numpy.asarray(self.dti_parameters.get_data())
        self.shape = dt6_array.shape
        if self.shape[-1] != 6:
            raise Exception("Expect a second order tensor model with six "
                            "independent parameters (...,6), got "
                            "{0}".format(self.shape))
        dt33_array = dti6to33(dt6_array)
        self.dt33_flat = dt33_array.reshape(
            (-1, dt33_array.shape[-2], dt33_array.shape[-1]))

        # Get decomposition
        eigenvals_array, eigenvecs_array = self.decompose_second_order_tensor()
        eigenvals_array = eigenvals_array.reshape(self.shape[:-1] + (3, ))
        eigenvecs_array = eigenvecs_array.reshape(self.shape[:-1] + (3, 3))

        # Save
        # Save eigenvalues and eigenvectors images
        for array, basename, out_trait_name in [
            (eigenvals_array, self.eigenvals_basename, "eigen_values_file"),
            (eigenvecs_array, self.eigenvecs_basename, "eigen_vectors_file")]:

            # Create a nifti image from the scalar array
            image = nibabel.Nifti1Image(
                array, affine=self.dti_parameters.get_affine())
            # Generate the output file name
            out_file = os.path.join(
                self.output_directory, basename + ".nii.gz")
            # Save the image to the output file name
            image.to_filename(out_file)
            # Update output trait
            setattr(self, out_trait_name, out_file)

    def decompose_second_order_tensor(self):
        """ Returns eigenvalues and eigenvectors of a given diffusion tensor

        Returns
        -------
        eigvals : array [...,,]
            the eignevalues for the eigen decomposition
            sorted from largest to smallest.
        eigvecs : array [...,3,3]
            associated eigenvectors
        """
        # Eigen decomposition
        eigenvals, eigenvecs = numpy.linalg.eigh(self.dt33_flat)

        # Need to sort the eigenvalues and associated eigenvectors
        # note that each direction is a column
        order = eigenvals.argsort()[::-1]
        indices = numpy.indices(eigenvals.shape)
        eigenvals = eigenvals[indices[0], order]
        indices = numpy.indices(eigenvecs.shape)
        order = order.repeat(3, axis=0).reshape(eigenvecs.shape)
        eigenvecs = eigenvecs[indices[0], indices[1], order]

        # Eigenvalues are positive definite
        eigenvals = eigenvals.clip(min=1e-8)

        return eigenvals, eigenvecs


def dti6to33(dt6):
    """ Full second order symmetric tensor from the six independent components.

    Parameters
    ----------
    dt6: numpy array (...,6)

    Returns
    -------
    dt33: numpy array (...,3,3)
    """

    dt33 = numpy.zeros(dt6.shape[:-1] + (3, 3), dtype=dt6.dtype)
    dt33[..., 0, 0] = dt6[..., 5]  # dxx
    dt33[..., 0, 1] = dt33[..., 1, 0] = dt6[..., 4] / 2  # dxy
    dt33[..., 0, 2] = dt33[..., 2, 0] = dt6[..., 3] / 2  # dxz
    dt33[..., 1, 1] = dt6[..., 2]  # dyy
    dt33[..., 1, 2] = dt33[..., 2, 1] = dt6[..., 1] / 2  # dyz
    dt33[..., 2, 2] = dt6[..., 0]  # dzz

    return dt33


def dti33to6(dt33):
    """ Six independent components from the full second order symmetric tensor.

    Parameters
    ----------
    dt33: numpy array (...,3,3)

    Returns
    -------
    dt6: numpy array (...,6)
    """

    dt6 = numpy.zeros(dt33.shape[:-2] + (6, ), dtype=dt33.dtype)
    dt6[..., 5] = dt33[..., 0, 0]
    dt6[..., 4] = dt33[..., 0, 1] + dt33[..., 1, 0]
    dt6[..., 3] = dt33[..., 0, 2] + dt33[..., 2, 0]
    dt6[..., 2] = dt33[..., 1, 1]
    dt6[..., 1] = dt33[..., 1, 2] + dt33[..., 2, 1]
    dt6[..., 0] = dt33[..., 2, 2]

    return dt6


def eigen_compose(eigenvals, eigenvecs):
    """ Recover a second order tensor image [Dxx, Dyy, Dzz, Dxy, Dxz, Dyz]
    """
    tensor = numpy.zeros(eigenvals.shape[:-1] + (6,))

    tensor[..., 5] = numpy.sum(
        eigenvecs[..., 0, i] * eigenvals[..., i] * eigenvecs[..., 0, i]
        for i in range(3))
    tensor[..., 2] = numpy.sum(
        eigenvecs[..., 1, i] * eigenvals[..., i] * eigenvecs[..., 1, i]
        for i in range(3))
    tensor[..., 0] = numpy.sum(
        eigenvecs[..., 2, i] * eigenvals[..., i] * eigenvecs[..., 2, i]
        for i in range(3))
    tensor[..., 4] = numpy.sum(
        eigenvecs[..., 0, i] * eigenvals[..., i] * eigenvecs[..., 1, i]
        for i in range(3))
    tensor[..., 3] = numpy.sum(
        eigenvecs[..., 0, i] * eigenvals[..., i] * eigenvecs[..., 2, i]
        for i in range(3))
    tensor[..., 1] = numpy.sum(
        eigenvecs[..., 1, i] * eigenvals[..., i] * eigenvecs[..., 2, i]
        for i in range(3))

    return tensor

if __name__ == "__main__":

    decompose = DecomposeSecondOrderTensor()
    decompose.tensor_file = "/volatile/nsap/caps/diffusion_estimation/tensor.nii.gz"
    decompose.output_directory = "/volatile/nsap/caps/diffusion_estimation"

    decompose._run_process()

    print stop