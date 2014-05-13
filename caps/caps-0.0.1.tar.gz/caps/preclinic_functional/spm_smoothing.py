#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os

try:
    from traits.api import File, Float, Int, List
except ImportError:
    from enthought.traits.api import File, Float, Int, List

from capsul.pipeline import Pipeline
from capsul.process import Process

from caps.preclinic_functional.spm_utility import ungzip_image, gzip_image


##############################################################
#         Coregistration Tool Processes
##############################################################

class InputDataManager(Process):
    """ Process that copy and ungzip the image.
    """
    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("input_image", File(optional=False))

        # Outputs
        self.add_trait("output_image",
                       List(File(), optional=False, output=True))

    def _run_process(self):
        # Ungzip func image
        spm_image = ungzip_image(self.input_image, self.output_directory)
        self.output_image = [spm_image, ]

    run = property(_run_process)


class OutputDataManager(Process):
    """ Process that zip the output image.
    """
    def __init__(self):
        super(OutputDataManager, self).__init__()

        # Inputs
        self.add_trait("unformated_image", List(File(), optional=False))

        # Outputs
        self.add_trait("smoothed_image",
                       File(optional=False, output=True))

    def _run_process(self):
        self.smoothed_image = gzip_image(
            self.unformated_image[0], self.output_directory)

    run = property(_run_process)


##############################################################
#                   Smoothing
##############################################################

class Smoothing(Pipeline):
    """ SPM Smoothing
    """

    def pipeline_definition(self):

        # Create process
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.spm_smoothing.InputDataManager")
        self.add_process("spm_smoothing", "nipype.interfaces.spm.Smooth")
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.spm_smoothing.OutputDataManager")
                                 
        # SPM smoothing algorithm parameters
        self.nodes["spm_smoothing"].process.fwhm = [5, 5, 5]
        self.nodes["spm_smoothing"].process.data_type = 0
        self.nodes["spm_smoothing"].process.implicit_masking = False
        self.nodes["spm_smoothing"].process.out_prefix = "s"

        # Export Inputs
        self.export_parameter("in_data_manager", "input_image")
        self.export_parameter("spm_smoothing", "fwhm")

        # Link input DataManager
        self.add_link("in_data_manager.output_image->"
                      "spm_smoothing.in_files")

        # Link spm smoothing
        self.add_link("spm_smoothing._smoothed_files->"
                      "out_data_manager.unformated_image")

        # Export outputs
        self.export_parameter("out_data_manager", "smoothed_image")


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir='/volatile/nsap/casper',
          **kwargs):
    """ SPM Smoothing Tool
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("mni_2mm")

    # Create FSL brain extraction pipeline
    smooth_pipeline = Smoothing()

    # Print Input Spec
    print smooth_pipeline.get_input_spec()

    # Initialize Smoothing pipeline
    smooth_pipeline.input_image = toy_dataset.mni

    # Execute the pipeline
    smooth_working_dir = os.path.join(working_dir, "smoothing")
    ensure_is_dir(smooth_working_dir)
    default_config = SortedDictionary(
        ("output_directory", smooth_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(smooth_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in smooth_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()

