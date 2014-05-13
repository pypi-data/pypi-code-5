#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Capsul import
from capsul.pipeline import Pipeline


##############################################################
#         Susceptibility Correction Pipeline Definition
##############################################################

class SusceptibilityCorrection(Pipeline):
    """ FSL suceptibility correction
    """

    def pipeline_definition(self):
        """ Pipeline definition
        """

        # Create processes
        self.add_process("phase_unwarpping", "nipype.interfaces.fsl.PRELUDE",
                          make_optional=["terminal_output"])
        self.add_process("susceptibility_correction",
                         "nipype.interfaces.fsl.FUGUE",
                          make_optional=["terminal_output"])

        # Export inputs
        self.export_parameter("phase_unwarpping", "magnitude_file")
        self.export_parameter("phase_unwarpping", "phase_file")
        self.export_parameter("phase_unwarpping", "mask_file")
        self.export_parameter("susceptibility_correction", "in_file",
                              pipeline_parameter="dw_file")

        # Link input
        self.add_link("mask_file->susceptibility_correction.mask_file")

        # Link phase unwarpping
        self.add_link("phase_unwarpping._unwrapped_phase_file->"
                      "susceptibility_correction.phasemap_file")

        # Export outputs
        self.export_parameter("susceptibility_correction", "_unwarped_file",
                          pipeline_parameter="susceptibility_corrected_file")
        self.export_parameter("phase_unwarpping", "_unwrapped_phase_file",
                          pipeline_parameter="unwrapped_phase_file")
