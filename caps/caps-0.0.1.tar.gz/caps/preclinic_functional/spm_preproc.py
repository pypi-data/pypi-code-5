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
    from traits.api import File, Float, Int, String, List
except ImportError:
    from enthought.traits.api import File, Float, Int, List

from capsul.pipeline import Pipeline


##############################################################
#                   SPM Preprocessings
##############################################################

class SPMPreproc(Pipeline):

    def pipeline_definition(self):

        # Create process
        self.add_process("spm_slice_timing",
                         "caps.preclinic_functional.slice_timing.SliceTiming")
        self.add_process("spm_realignment",
                         "caps.preclinic_functional.spm_realignment.Realignment")
        self.add_process("spm_coregistration",
                         "caps.preclinic_functional.spm_coregistration.Coregistration")
        self.add_process("spm_normalization",
                         "caps.preclinic_functional.spm_normalization.Normalization")
        self.add_process("spm_smoothing",
                         "caps.preclinic_functional.spm_smoothing.Smoothing")
        self.add_process("bet", "caps.preclinic_functional.bet.BET")

        # Export inputs
        self.export_parameter("spm_slice_timing", "fmri_image")
        self.export_parameter("spm_slice_timing", "force_repetition_time")
        self.export_parameter("spm_slice_timing", "force_slice_times")
        self.export_parameter("spm_slice_timing", "select_slicing")
        self.export_parameter("spm_realignment", "register_to_mean")
        self.export_parameter("spm_coregistration", "fwhm")
        self.export_parameter("spm_coregistration", "moving_image",
                              pipeline_parameter="struct_image")
        self.export_parameter("spm_normalization", "select_normalization")
        self.export_parameter("spm_smoothing", "fwhm",
                              pipeline_parameter="smooth_fwhm")
        self.export_parameter("bet", "generate_binary_mask")
        self.export_parameter("bet", "use_4d_input")
        self.export_parameter("bet", "generate_mesh")
        self.export_parameter("bet", "generate_skull")
        self.export_parameter("bet", "bet_threshold")

        # Link SliceTiming
        self.add_link("spm_slice_timing.time_corrected_fmri_image->"
                      "spm_realignment.time_series_image")

        # Link Realignment
        self.add_link("spm_realignment.reference_mean_image->"
                      "spm_coregistration.reference_image")
        self.add_link("spm_realignment.realigned_time_series_header_modified->"
                      "spm_normalization.func_image")

        # Link Coregistration
        self.add_link("spm_coregistration.coregistered_image->"
                      "spm_normalization.coregistered_struct_image")

        # Link Normalize
        self.add_link("spm_normalization.normalized_func_image->"
                      "spm_smoothing.input_image")

        # Link Smoothing
        self.add_link("spm_smoothing.smoothed_image->bet.input_file")

        # Export outputs
        self.export_parameter("spm_slice_timing", "time_corrected_fmri_image")
        self.export_parameter("spm_realignment", "reference_mean_image")
        self.export_parameter("spm_realignment", "realigned_time_series_image")
        self.export_parameter("spm_coregistration", "coregistered_image")
        self.export_parameter("spm_normalization", "normalization_parameter")
        self.export_parameter("spm_normalization", "normalized_struct_image")
        self.export_parameter("spm_normalization", "normalized_func_image")
        self.export_parameter("spm_smoothing", "smoothed_image")
        self.export_parameter("bet", "bet_outskin_mesh_file")
        self.export_parameter("bet", "bet_outskull_mesh_file")
        self.export_parameter("bet", "bet_out_file")
        self.export_parameter("bet", "bet_outskull_mask_file")
        self.export_parameter("bet", "bet_inskull_mesh_file")
        self.export_parameter("bet", "bet_skull_mask_file")
        self.export_parameter("bet", "bet_inskull_mask_file")
        self.export_parameter("bet", "bet_meshfile")
        self.export_parameter("bet", "bet_outskin_mask_file")
        self.export_parameter("bet", "bet_mask_file")


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir='/volatile/nsap/casper',
          **kwargs):
    """ SPM Preprocessings
    """
    # Pilot imports
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    spm_preproc_pipeline = SPMPreproc()

    # Print Input Spec
    print spm_preproc_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    spm_preproc_pipeline.fmri_image = toy_dataset.fmri
    spm_preproc_pipeline.struct_image = toy_dataset.anat
    spm_preproc_pipeline.select_normalization = "segment"
    spm_preproc_pipeline.select_slicing = "spm"
    spm_preproc_pipeline.force_repetition_time = toy_dataset.TR
    spm_preproc_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    spm_preproc_working_dir = os.path.join(working_dir, "spmpreproc")
    ensure_is_dir(spm_preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", spm_preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(spm_preproc_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in spm_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()
