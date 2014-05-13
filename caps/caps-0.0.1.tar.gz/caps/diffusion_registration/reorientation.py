#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import numpy
import os
import nibabel

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (List, Bool, File, Int, Str, Float, Directory,
                            Enum)
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import (List, Bool, File, Int, Str,
                                      Float, Directory, Enum)

# Capsul import
from capsul.process import Process

# Caps import
from caps.diffusion_estimation.tensor_utils import eigen_compose


##############################################################
#          Jacobian Approximation Process definition
##############################################################

class LocalAffineTransformation(Process):
    """ Approximate a vector field by local affine transformations
    """

    def __init__(self):
        """ Initialize LocalAffineTransformation class
        """
        # Inheritance
        super(LocalAffineTransformation, self).__init__()

        # Inputs
        self.add_trait("field_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the deformation field (dx, dy, dz)"))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor model will be "
                  "written")))
        self.add_trait("local_affine_transform_name", Str(
            "local_affine_transform",
            optional=True,
            output=False,
            desc=("the name of the output local affine transform file")))

        # Outputs
        self.add_trait("local_affine_transform_file", File(
            output=True,
            desc="the approximated local affine transformation"))

    def _run_process(self):
        """ LocalAffineTransformation execution code
        """
        # Load
        self.load_dataset()

        # Local transformation
        self.get_local_affine_transformation()

        # Save
        local_affine_image = nibabel.Nifti1Image(
            self.local_affine_transform,
            affine=self.field.get_affine())
        local_affine_file = os.path.join(
            self.output_directory,
            self.local_affine_transform_name + ".nii.gz")
        local_affine_image.to_filename(local_affine_file)
        self.local_affine_transform_file = local_affine_file

    def load_dataset(self):
        """ Load the vector field
        """
        # Load
        self.field = nibabel.load(self.field_file)
        self.field_data = numpy.asarray(self.field.get_data())
        self.shape = self.field_data.shape

        # Check parameters
        if self.shape[-1] != 3:
            raise Exception("A vector field (...,3) is expected, got "
                            "{0}".format(self.shape))

    def get_local_affine_transformation(self):
        """ Approximate a vector field by local affine transformations
        """
        jacobian = numpy.zeros(self.shape[:-1] + (3, 3))
        # compute Ji <- di
        for i in range(3):
            g = numpy.gradient(self.field_data[..., i])
            jacobian[..., i, 0] = g[0]  # dfi/dx
            jacobian[..., i, 1] = g[1]  # dfi/dy
            jacobian[..., i, 2] = g[2]  # dfi/dz

        identity = numpy.zeros(jacobian.shape)
        identity[..., 0, 0] = 1
        identity[..., 1, 1] = 1
        identity[..., 2, 2] = 1
        self.local_affine_transform = identity + jacobian


##############################################################
#      Second Order Tensor Reorientation Process definition
##############################################################

class SecondOrderTensorReorientation(Process):
    """ Second order tensor reorientation.

    Two methods are available: the finite strain (FS) and the preservation
    of the principal direction (PPD).
    """

    def __init__(self):
        """ Initialize SecondOrderTensorReorientation class
        """
        # Inheritance
        super(SecondOrderTensorReorientation, self).__init__()

        # Inputs
        self.add_trait("local_affine_transform_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the approximated local affine transformation"))
        self.add_trait("eigenvals_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the second order tensor eigenvalues"))
        self.add_trait("eigenvecs_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the second order tensor eigenvectors"))
        self.add_trait("reorientation_strategy", Enum(
            ("ppd", "fs"),
            optional=True,
            output=False,
            desc="the reorientation strategy: ppd or fs"))
        self.add_trait("output_directory", Directory(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc=("the output directory where the tensor model will be "
                  "written")))
        self.add_trait("reoriented_tensor_name", Str(
            "reoriented_tensor",
            optional=True,
            output=False,
            desc=("the name of the output reoriented tensor field")))

        # Outputs
        self.add_trait("reoriented_tensor_file", File(
            output=True,
            desc="the reoriented tensor field"))

    def _run_process(self):
        """ SecondOrderTensorReorientation execution code
        """
        # Load
        self.load_dataset()

        # Tensor reorientation
        if self.reorientation_strategy == "ppd":
            self.ppd()
        else:
            self.fs()

        # Save
        reoriented_tensor_image = nibabel.Nifti1Image(
            self.reoriented_tensor,
            affine=self.eigenvals.get_affine())
        reoriented_tensor_file = os.path.join(
            self.output_directory,
            self.reoriented_tensor_name + ".nii.gz")
        reoriented_tensor_image.to_filename(reoriented_tensor_file)
        self.reoriented_tensor_file = reoriented_tensor_file

    def load_dataset(self):
        """ Load the tensor and local affine transformation
        """
        # Load
        self.local_affine = nibabel.load(self.local_affine_transform_file)
        self.eigenvals = nibabel.load(self.eigenvals_file)
        self.eigenvecs = nibabel.load(self.eigenvecs_file)
        self.local_affine_data = numpy.asarray(self.local_affine.get_data())
        self.eigenvals_data = numpy.asarray(self.eigenvals.get_data())
        self.eigenvecs_data = numpy.asarray(self.eigenvecs.get_data())
        self.shape = self.eigenvals_data.shape

        # Check parameters
        if self.eigenvals_data.shape[:-1] != self.local_affine_data.shape[:-2]:
            raise Exception("The tensor eigenvalues field has to be the same "
                            "size as the local affine transform field")
        if self.local_affine_data.shape[-2:] != (3, 3):
            raise Exception("A vector field (...,3, 3) is expected, got "
                            "{0}".format(self.local_affine.shape))
        if self.eigenvals_data.shape[-1] != 3:
            raise Exception("A second order eigenvalues field (...,3) is "
                            "expected, got {0}".format(self.shape))

    def ppd(self):
        """ Implementation of Alexander's preservation of principle direction
            algorithm.
        """
        # Short name
        eigenvals = self.eigenvals_data
        eigenvecs = self.eigenvecs_data

        # Use local affine F to find n1, n2
        # n1 = F*  v1
        n1 = numpy.zeros(self.shape[:-1] + (3,))
        n1[..., 0] = numpy.sum(self.local_affine_data[..., 0, i] *
                               eigenvecs[..., i, 0] for i in range(3))
        n1[..., 1] = numpy.sum(self.local_affine_data[..., 1, i] *
                               eigenvecs[..., i, 0] for i in range(3))
        n1[..., 2] = numpy.sum(self.local_affine_data[..., 2, i] *
                               eigenvecs[..., i, 0] for i in range(3))
        # norm(n1)
        norm = numpy.sqrt(n1[..., 0] ** 2 + n1[..., 1] ** 2 +
                          n1[..., 2] ** 2)
        norm = norm + (norm == 0)
        n1[..., 0] = n1[..., 0] / norm
        n1[..., 1] = n1[..., 1] / norm
        n1[..., 2] = n1[..., 2] / norm

        # n2 = F * v2
        n2 = numpy.zeros(self.shape[:-1] + (3,))
        n2[..., 0] = numpy.sum(self.local_affine_data[..., 0, i] *
                               eigenvecs[..., i, 1] for i in range(3))
        n2[..., 1] = numpy.sum(self.local_affine_data[..., 1, i] *
                               eigenvecs[..., i, 1] for i in range(3))
        n2[..., 2] = numpy.sum(self.local_affine_data[..., 2, i] *
                               eigenvecs[..., i, 1] for i in range(3))

        # Projecting n2 onto n1-n2 plane: P(n2) = Pn2 = n2 - (n2*n1')*n1
        Pn2 = numpy.zeros(self.shape[:-1] + (3,))
        # temp = (n2*n1)*n1, so Pn2 = n2 - temp
        temp = (n1[..., 0] * n2[..., 0] + n1[..., 1] * n2[..., 1] +
                n1[..., 2] * n2[..., 2])
        Pn2[..., 0] = temp * n1[..., 0]
        Pn2[..., 1] = temp * n1[..., 1]
        Pn2[..., 2] = temp * n1[..., 2]
        Pn2 = n2 - Pn2
        norm = numpy.sqrt(Pn2[..., 0] ** 2 + Pn2[..., 1] ** 2 +
                          Pn2[..., 2] ** 2)
        norm = norm + (norm == 0)
        Pn2[..., 0] = Pn2[..., 0] / norm
        Pn2[..., 1] = Pn2[..., 1] / norm
        Pn2[..., 2] = Pn2[..., 2] / norm

        # Computing n3 in order to have an orthogonal basis
        n3 = numpy.cross(n1, Pn2)
        norm = numpy.sqrt(n3[..., 0] ** 2 + n3[..., 1] ** 2 + n3[..., 2] ** 2)
        norm = norm + (norm == 0)
        n3[..., 0] = n3[..., 0] / norm
        n3[..., 1] = n3[..., 1] / norm
        n3[..., 2] = n3[..., 2] / norm

        eigenvecs[..., 0] = n1
        eigenvecs[..., 1] = Pn2
        eigenvecs[..., 2] = n3

        self.reoriented_tensor = eigen_compose(eigenvals, eigenvecs)

    def fs(self):
        """ Apply a rotation to all tensors
        """
        raise Exception("FS not implemented")