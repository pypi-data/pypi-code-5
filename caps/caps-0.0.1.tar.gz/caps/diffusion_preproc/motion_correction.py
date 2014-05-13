#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import numpy

# Capsul import
from capsul.process import Process
from capsul.process import get_process_instance

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import List, Directory, File
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import List, Directory, File


class TimeSerieMotionCorrection(Process):
    """ FSL rigid registration of a time serie sequence to a reference volume

    .. note::

        This script rotates the b-vectors, so ensure the consistency
        between the resulting nifti orientation and the b matrix table.

    For complete details on the registration algorithm, see
    the `FLIRT Documentation. <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT>`_
    """

    def __init__(self):
        """ Initialize TimeSerieMotionCorrection class
        """
        # Inheritance
        super(TimeSerieMotionCorrection, self).__init__()

        # Inputs
        self.add_trait("in_files", List(File(exists=True),
            optional=False,
            output=False,
            desc="a serie of images to registered"))
        self.add_trait("reference_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the reference image"))
        self.add_trait("bvecs", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the diffusion b-vectors"))
        self.add_trait("output_directory", Directory(
            os.getcwd(),
            optional=True,
            output=False,
            exists=True,
            desc="the output directory"))

        # Outputs
        self.add_trait("reoriented_bvecs", File(
            _Undefined(),
            output=True,
            exists=True,
            desc="the reoriented diffusion b-vectors"))
        self.add_trait("motion_corrected_files", List(File(exists=True),
            output=True,
            desc="path of the registered images"))
        self.add_trait("rigid_transformations", List(File(exists=True),
            output=True,
            desc="path of the calculated rigid transformations"))

    def _run_process(self):
        """ TimeSerieMotionCorrection execution code
        """
        # Create rigid registration object
        flirt_instance = get_process_instance("nipype.interfaces.fsl.FLIRT")
        flirt_instance.reference = self.reference_file
        flirt_instance.no_search = True
        flirt_instance.padding_size = 1
        flirt_instance.dof = 6
        flirt_instance.set_output_directory(self.output_directory)

        # Start rigid registration
        motion_corrected_files = []
        out_matrix_files = []
        for file_path in self.in_files:
            flirt_instance.in_file = file_path
            flirt_instance._run_process()
            motion_corrected_files.append(flirt_instance._out_file)
            out_matrix_files.append(flirt_instance._out_matrix_file)
        self.rigid_transformations = out_matrix_files
        self.motion_corrected_files = motion_corrected_files

        # Need to realign all bvecs
        self.rotate_bvecs()

    def rotate_bvecs(self):
        """ Rotates the diffusion b-vectors
        """
        # Generate output file name
        name, fext = os.path.splitext(os.path.basename(self.bvecs))
        if fext == '.gz':
            name, _ = os.path.splitext(name)
        out_file = os.path.join(self.output_directory,
                                "{0}_rotated.bvec".format(name))

        # Load bvecs
        bvecs = numpy.loadtxt(self.bvecs)

        # Reorientation
        new_bvecs = numpy.zeros(shape=bvecs.T.shape)
        for i, transformation in enumerate(self.rigid_transformations):
            bvec = numpy.matrix(bvecs[:, i])
            rot = numpy.matrix(numpy.loadtxt(transformation)[0:3, 0:3])
            new_bvecs[i] = (numpy.array(rot * bvec.T).T)[0]

        # Save reoriented bvecs
        numpy.savetxt(out_file, numpy.array(new_bvecs).T, fmt="%0.15f")
        self.reoriented_bvecs = out_file

    run = property(_run_process)


if __name__ == "__main__":
    p = DiffusionMotionCorrection()