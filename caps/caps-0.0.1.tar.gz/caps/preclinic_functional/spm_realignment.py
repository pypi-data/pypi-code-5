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
    from traits.api import File, List
except ImportError:
    from enthought.traits.api import File, List

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
        self.add_trait("time_series_image", File(optional=False))

        # Outputs
        self.add_trait("out_time_series_image",
                       List(File(), optional=False, output=True))

    def _run_process(self):
        # Ungzip func image
        spm_image = ungzip_image(self.time_series_image,
                                 self.output_directory)
        self.out_time_series_image = [spm_image, ]

    run = property(_run_process)


class OutputDataManager(Process):
    """ Process that format the fonctional slice time corrected image
    accordingly to the switch value.
    """
    def __init__(self):
        super(OutputDataManager, self).__init__()

        # Inputs
        self.add_trait("unformated_realigned_time_series_image",
                       List(File(), optional=False))
        self.add_trait("unformated_realigned_time_series_header_modified",
                       List(File(), optional=False))
        self.add_trait("unformated_reference_mean_image",
                       File(optional=False))

        # Outputs
        self.add_trait("realigned_time_series_image",
                       File(optional=False, output=True))
        self.add_trait("realigned_time_series_header_modified",
                       File(optional=False, output=True))
        self.add_trait("reference_mean_image",
                       File(optional=False, output=True))

    def _run_process(self):
        self.realigned_time_series_image = gzip_image(
            self.unformated_realigned_time_series_image[0],
            self.output_directory)
        self.realigned_time_series_header_modified = gzip_image(
            self.unformated_realigned_time_series_header_modified[0],
            self.output_directory)
        self.reference_mean_image = gzip_image(
            self.unformated_reference_mean_image,
            self.output_directory)

    run = property(_run_process)


##############################################################
#         Realign Pipeline Definition
##############################################################

class Realignment(Pipeline):
    """ Realignement Pipeline

    Estimating within modality rigid body alignment.
    """
    def pipeline_definition(self):

        # Create processes
        self.add_process("spm_realignment", "nipype.interfaces.spm.Realign")
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.spm_realignment.InputDataManager")
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.spm_realignment.OutputDataManager")

        # Export inputs
        self.export_parameter("in_data_manager", "time_series_image")
        self.export_parameter("spm_realignment", "register_to_mean")

        # Link input DataManager
        self.add_link("in_data_manager.out_time_series_image->"
                      "spm_realignment.in_files")

        # Link spm realignement
        self.add_link("spm_realignment._mean_image->"
                      "out_data_manager.unformated_reference_mean_image")
        self.add_link("spm_realignment._modified_in_files->"
         "out_data_manager.unformated_realigned_time_series_header_modified")
        self.add_link("spm_realignment._realigned_files->"
                   "out_data_manager.unformated_realigned_time_series_image")

        # Export outputs
        self.export_parameter("spm_realignment", "_realignment_parameters",
                              pipeline_parameter="realignment_parameters")
        self.export_parameter("out_data_manager", "reference_mean_image")
        self.export_parameter("out_data_manager",
                              "realigned_time_series_header_modified")
        self.export_parameter("out_data_manager",
                              "realigned_time_series_image")

        # SPM realignement algorithm parameters
        self.time_series_image = _Undefined()
        self.register_to_mean = True
        self.nodes["spm_realignment"].process.jobtype = "estwrite"
        self.nodes["spm_realignment"].process.quality = 0.9
        self.nodes["spm_realignment"].process.separation = 4
        self.nodes["spm_realignment"].set_plug_value("fwhm", 5)
        self.nodes["spm_realignment"].process.interp = 2
        self.nodes["spm_realignment"].process.wrap = [0, 0, 0]
        self.nodes["spm_realignment"].process.write_which = [2, 1]
        self.nodes["spm_realignment"].process.write_interp = 4
        self.nodes["spm_realignment"].process.write_wrap = [0, 0, 0]
        self.nodes["spm_realignment"].process.write_mask = True
        self.nodes["spm_realignment"].process.out_prefix = "r"


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
    toy_dataset = get_sample_data("localizer")

    # Create
    realign_pipeline = Realignment()

    # Print Input Spec
    print realign_pipeline.get_input_spec()

    # Initialize Coregistration pipeline
    realign_pipeline.time_series_image = toy_dataset.fmri

    # Execute the pipeline
    realign_working_dir = os.path.join(working_dir, "realign")
    ensure_is_dir(realign_working_dir)
    default_config = SortedDictionary(
        ("output_directory", realign_working_dir),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(realign_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in realign_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()
