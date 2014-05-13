#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

try:
    from traits.api import File, Float, Int, List
except ImportError:
    from enthought.traits.api import File, Float, Int, List

import os

from capsul.process import Process
from capsul.pipeline import Pipeline

from traits.trait_base import _Undefined

from caps.preclinic_functional.spm_utility import ungzip_image, gzip_image


##############################################################
#         Coregistration Tool Processes
##############################################################

class InputDataManager(Process):
    """ Process that copy and ungzip the fonctional image.
    """
    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("moving_image", File(optional=False))
        self.add_trait("reference_image", File(optional=False))

        # Outputs
        self.add_trait("out_moving_image",
                       List(File(), optional=False, output=True))
        self.add_trait("out_reference_image",
                       File(optional=False, output=True))

    def _run_process(self):
        # Ungzip func image
        spm_image = ungzip_image(self.moving_image, self.output_directory)
        self.out_moving_image = [spm_image, ]
        # Ungzip template
        self.out_reference_image = ungzip_image(self.reference_image,
                                                self.output_directory)

    run = property(_run_process)


class OutputDataManager(Process):
    """ Process that format the fonctional slice time corrected image
    accordingly to the switch value.
    """
    def __init__(self):
        super(OutputDataManager, self).__init__()

        # Inputs
        self.add_trait("unformated_image_result", List(File(), optional=False))

        # Outputs
        self.add_trait("coregistered_image",
                       File(optional=False, output=True))

    def _run_process(self):
        self.coregistered_image = gzip_image(
            self.unformated_image_result[0], self.output_directory)

    run = property(_run_process)


##############################################################
#         Coregistration Pipeline Definition
##############################################################

class Coregistration(Pipeline):
    """ Coregistration Pipeline.
    
    Register a moving image to a reference one.
    """
    def pipeline_definition(self):

        # Create processes
        self.add_process("spm_coregistration",
                         "nipype.interfaces.spm.Coregister")
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.spm_coregistration.InputDataManager")
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.spm_coregistration.OutputDataManager")

        # Export inputs
        self.export_parameter("in_data_manager", "moving_image")
        self.export_parameter("in_data_manager", "reference_image")
        self.export_parameter("spm_coregistration", "fwhm")

        # Link input DataManager
        self.add_link("in_data_manager.out_moving_image->"
                      "spm_coregistration.source")
        self.add_link("in_data_manager.out_reference_image->"
                      "spm_coregistration.target")

        # Link spm_coregistration
        self.add_link("spm_coregistration._coregistered_source->"
                      "out_data_manager.unformated_image_result")

        # Export outputs
        self.export_parameter("out_data_manager", "coregistered_image")

        # SPM coregistered algorithm parameters
        self.moving_image = _Undefined()
        self.reference_image = _Undefined()
        self.nodes["spm_coregistration"].process.jobtype = "estimate"
        self.nodes["spm_coregistration"].process.cost_function = "nmi"
        self.nodes["spm_coregistration"].process.separation = [4, 2]
        self.nodes["spm_coregistration"].process.tolerance = \
            [0.02, 0.02, 0.02, 0.001, 0.001, 0.001, 0.01,
             0.01, 0.01, 0.001, 0.001, 0.001]
        self.fwhm = [7, 7]
        self.nodes["spm_coregistration"].process.out_prefix = "c"


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/casper",
          **kwargs):
    """ Coregistration Tool
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_src_dataset = get_sample_data("mni_1mm")
    toy_dest_dataset = get_sample_data("mni_2mm")

    # Create
    coreg_pipeline = Coregistration()

    # Print Input Spec
    print coreg_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    coreg_pipeline.moving_image = toy_src_dataset.mni
    coreg_pipeline.reference_image = toy_dest_dataset.mni

    # Execute the pipeline
    coreg_working_dir = os.path.join(working_dir, "coregistration")
    ensure_is_dir(coreg_working_dir)
    default_config = SortedDictionary(
        ("output_directory", coreg_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(coreg_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in coreg_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()
