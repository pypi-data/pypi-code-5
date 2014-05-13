#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os

from traits.trait_base import _Undefined

from capsul.pipeline import Pipeline


##############################################################
#         Brain Extraction Pipeline Definition
##############################################################

class BET(Pipeline):
    """ BET

    Brain Extraction Tool
    """

    def pipeline_definition(self):

        # Create processes
        self.add_process('bet', 'nipype.interfaces.fsl.BET',
                         make_optional=["terminal_output"])

        # Export Inputs
        self.export_parameter("bet", "in_file",
                              pipeline_parameter="input_file")
        self.export_parameter("bet", "mask",
                              pipeline_parameter="generate_binary_mask")
        self.export_parameter("bet", "functional",
                              pipeline_parameter="use_4d_input")
        self.export_parameter("bet", "mesh",
                              pipeline_parameter="generate_mesh")
        self.export_parameter("bet", "skull",
                              pipeline_parameter="generate_skull")
        self.export_parameter("bet", "frac",
                              pipeline_parameter="bet_threshold")

        # Export outputs
        self.export_parameter("bet", "_outskin_mesh_file",
                              pipeline_parameter="bet_outskin_mesh_file")
        self.export_parameter("bet", "_outskull_mesh_file",
                              pipeline_parameter="bet_outskull_mesh_file")
        self.export_parameter("bet", "_out_file",
                              pipeline_parameter="bet_out_file")
        self.export_parameter("bet", "_outskull_mask_file",
                              pipeline_parameter="bet_outskull_mask_file")
        self.export_parameter("bet", "_inskull_mesh_file",
                              pipeline_parameter="bet_inskull_mesh_file")
        self.export_parameter("bet", "_skull_mask_file",
                              pipeline_parameter="bet_skull_mask_file")
        self.export_parameter("bet", "_inskull_mask_file",
                              pipeline_parameter="bet_inskull_mask_file")
        self.export_parameter("bet", "_meshfile",
                              pipeline_parameter="bet_meshfile")
        self.export_parameter("bet", "_outskin_mask_file",
                              pipeline_parameter="bet_outskin_mask_file")
        self.export_parameter("bet", "_mask_file",
                              pipeline_parameter="bet_mask_file")

        # FSL BET algorithm parameters
        self.input_file = _Undefined()
        self.use_4d_input = False
        self.generate_binary_mask = True
        self.generate_mesh = False
        self.generate_skull = False
        self.bet_threshold = 0.5


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir='/volatile/nsap/casper',
          **kwargs):
    """ FSL Brain Extraction Tool
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("mni_2mm")

    # Create FSL brain extraction pipeline
    bet_pipeline = BET()

    # Print Input Spec
    print bet_pipeline.get_input_spec()

    # Initialize BET pipeline
    bet_pipeline.input_file = toy_dataset.mni

    # Execute the pipeline
    bet_working_dir = os.path.join(working_dir, "bet")
    ensure_is_dir(bet_working_dir)
    default_config = SortedDictionary(
        ("output_directory", bet_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(bet_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in bet_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

if __name__ == '__main__':
    pilot()

