#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os

from capsul.pipeline import Pipeline


##############################################################
#                   SPM Normalization
##############################################################

class Normalization(Pipeline):
    """ SPM structural and functional normalization to template.

    Steps:
        * Segement or NewSegment: Structural Normalization anat -> ICBM
        * Functional/Structural normalization
    """

    def pipeline_definition(self):

        # Create process
        self.add_process("norm_new_segment",
                         "caps.preclinic_functional.spm_new_segment.SPMNewSegment")
        self.add_process("norm_segment",
                         "caps.preclinic_functional.spm_segment.SPMSegment")

        # Create switch
        self.add_switch("select_normalization", ["segment", "new_segment"],
                        ["normalization_parameter", "normalized_func_image",
                        "normalized_struct_image"])

        # Export inputs
        self.export_parameter("norm_new_segment", "coregistered_struct_image")
        self.export_parameter("norm_new_segment", "func_image")
        self.export_parameter("norm_new_segment", "struct_voxel_sizes")
        self.export_parameter("norm_new_segment", "func_voxel_sizes")

        # Link inputs
        self.add_link("coregistered_struct_image->"
                      "norm_segment.coregistered_struct_image")
        self.add_link("func_image->norm_segment.func_image")
        self.add_link("struct_voxel_sizes->"
                      "norm_segment.struct_voxel_sizes")
        self.add_link("func_voxel_sizes->"
                      "norm_segment.func_voxel_sizes")

        # Link new segment
        self.add_link("norm_new_segment.normalization_parameter->"
                 "select_normalization.new_segment_switch_normalization_parameter")
        self.add_link("norm_new_segment.normalized_struct_image->"
                 "select_normalization.new_segment_switch_normalized_struct_image")
        self.add_link("norm_new_segment.normalized_func_image->"
                 "select_normalization.new_segment_switch_normalized_func_image")

        # Link segment
        self.add_link("norm_segment.normalization_parameter->"
                 "select_normalization.segment_switch_normalization_parameter")
        self.add_link("norm_segment.normalized_struct_image->"
                 "select_normalization.segment_switch_normalized_struct_image")
        self.add_link("norm_segment.normalized_func_image->"
                 "select_normalization.segment_switch_normalized_func_image")

        # Export outputs
        self.export_parameter("select_normalization",
                              "normalization_parameter")
        self.export_parameter("select_normalization",
                              "normalized_struct_image")
        self.export_parameter("select_normalization",
                              "normalized_func_image")


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir='/volatile/nsap/casper',
          **kwargs):
    """ SPM Smoothing Tool
    """
    # Pilot imports
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    from caps.toy_datasets import get_sample_data
    
    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    norm_pipeline = Normalization()

    # Print Input Spec
    print norm_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    norm_pipeline.coregistered_struct_image = toy_dataset.mean
    norm_pipeline.func_image = toy_dataset.fmri
    print "SWITCH EVENT"
    norm_pipeline.select_normalization = "segment"
    print (norm_pipeline.nodes["select_normalization"].switch)

    # Execute the pipeline
    norm_working_dir = os.path.join(working_dir, "normalization")
    ensure_is_dir(norm_working_dir)
    default_config = SortedDictionary(
        ("output_directory", norm_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(norm_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in norm_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()
