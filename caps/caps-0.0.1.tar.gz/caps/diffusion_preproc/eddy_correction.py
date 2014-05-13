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


class EddyCorrection(Process):
    """ FSL eddy distortion correction

    For complete details on the registration algorithm, see
    the `FLIRT Documentation. <http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT>`_
    """

    def __init__(self):
        """ Initialize EddyCorrection class
        """
        # Inheritance
        super(EddyCorrection, self).__init__()

        # Inputs
        self.add_trait("in_files", List(File(exists=True),
            optional=False,
            output=False,
            desc="a serie of images to correct"))
        self.add_trait("reference_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="the reference image"))
        self.add_trait("output_directory", Directory(
            os.getcwd(),
            optional=True,
            output=False,
            exists=True,
            desc="the output directory"))

        # Outputs
        self.add_trait("eddy_corrected_files", List(File(exists=True),
            output=True,
            desc="path of the registered images"))
        self.add_trait("affine_transformations", List(File(exists=True),
            output=True,
            desc="path of the calculated rigid transformations"))

    def _run_process(self):
        """ EddyCorrection execution code
        """
        # Create affine registration object
        flirt_instance = get_process_instance("nipype.interfaces.fsl.FLIRT")
        flirt_instance.reference = self.reference_file
        flirt_instance.no_search = True
        flirt_instance.padding_size = 1
        flirt_instance.dof = 12
        flirt_instance.set_output_directory(self.output_directory)

        # Start rigid registration
        eddy_corrected_files = []
        out_matrix_files = []
        for file_path in self.in_files:
            flirt_instance.in_file = file_path
            flirt_instance._run_process()
            eddy_corrected_files.append(flirt_instance._out_file)
            out_matrix_files.append(flirt_instance._out_matrix_file)
        self.affine_transformations = out_matrix_files
        self.eddy_corrected_files = eddy_corrected_files

    run = property(_run_process)


if __name__ == "__main__":
    p = EddyCorrection()