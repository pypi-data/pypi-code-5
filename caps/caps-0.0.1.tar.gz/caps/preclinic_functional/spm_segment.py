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
    from traits.api import File, Float, Int, List, Any, Str
    from traits.trait_base import _Undefined
except ImportError:
    from enthought.traits.api import File, Float, Int, List, Any, Str
    from enthought.traits.trait_base import _Undefined

from capsul.process import Process
from capsul.pipeline import Pipeline

from caps.preclinic_functional.spm_utility import ungzip_image, gzip_image
from caps.toy_datasets import get_sample_data


##############################################################
#               Normalization Tool Processes
##############################################################

class InputDataManager(Process):
    """ Process that copy and ungzip the image.
    """
    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("coregistered_struct_image", File(_Undefined(),
                                                         optional=False))
        self.add_trait("func_image", File(_Undefined(),
                                          optional=False))

        # Outputs
        self.add_trait("output_coregistered_struct_image",
                       List(File(), optional=False, output=True))
        self.add_trait("output_func_image",
                       List(File(), optional=False, output=True))

    def _run_process(self):
        # Ungzip struct image
        spm_image = ungzip_image(self.coregistered_struct_image,
                                 self.output_directory)
        self.output_coregistered_struct_image = [spm_image, ]
        # Ungzip func image
        spm_image = ungzip_image(self.func_image,
                                 self.output_directory)
        self.output_func_image = [spm_image, ]

    run = property(_run_process)


class ListDataManager(Process):
    """ Process that put an image to a list
    """
    def __init__(self):
        super(ListDataManager, self).__init__()

        # Inputs
        self.add_trait("image",
                       File(optional=False))

        # Outputs
        self.add_trait("list_image",
                       List(File(), optional=False, output=True))

    def _run_process(self):
        self.list_image = [self.image, ]

    run = property(_run_process)


class OutputDataManager(Process):
    """ Process that zip the output image.
    """
    def __init__(self):
        super(OutputDataManager, self).__init__()

        # Inputs
        self.add_trait("unformated_normalized_struct_image",
                       Any(optional=False))
        self.add_trait("unformated_normalized_func_image",
                       Any(optional=False))

        # Outputs
        self.add_trait("normalized_struct_image",
                       File(optional=False, output=True))
        self.add_trait("normalized_func_image",
                       File(optional=False, output=True))

    def _run_process(self):
        self.normalized_struct_image = gzip_image(
            self.unformated_normalized_struct_image[0], self.output_directory)
        self.normalized_func_image = gzip_image(
            self.unformated_normalized_func_image[0], self.output_directory)
    
    run = property(_run_process)


##############################################################
#                   SPM Segment
##############################################################

class SPMSegment(Pipeline):
    """ SPM structural and functional normalization to template.

    Steps:
        * Segement or NewSegment: Structural Normalization anat -> ICBM
        * Functional/Structural normalization
    """

    def pipeline_definition(self):

        # Create process
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.spm_segment.InputDataManager")
        self.add_process("norm_segment", "nipype.interfaces.spm.Segment")
        self.add_process("list_converter",
                         "caps.preclinic_functional.spm_segment.ListDataManager")
        self.add_process("struct_normalize",
                         "nipype.interfaces.spm.Normalize",
                         make_optional=["source", "template"])
        self.add_process("func_normalize",
                         "nipype.interfaces.spm.Normalize",
                         make_optional=["source", "template"])
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.spm_segment.OutputDataManager")

        # Export inputs
        self.export_parameter("in_data_manager", "coregistered_struct_image")
        self.export_parameter("in_data_manager", "func_image")
        self.export_parameter("struct_normalize", "write_voxel_sizes",
                              pipeline_parameter="struct_voxel_sizes")
        self.export_parameter("func_normalize", "write_voxel_sizes",
                              pipeline_parameter="func_voxel_sizes")

        # Link input DataManager
        self.add_link("in_data_manager.output_coregistered_struct_image->"
                      "norm_segment.data")
        self.add_link("in_data_manager.output_func_image->"
                      "func_normalize.apply_to_files")

        # Link Segment
        self.add_link("norm_segment._transformation_mat->"
                      "struct_normalize.parameter_file")
        self.add_link("norm_segment._transformation_mat->"
                      "func_normalize.parameter_file")

        # Link list DataManager
        self.add_link("norm_segment._bias_corrected_image->"
                      "list_converter.image")
        self.add_link("list_converter.list_image->"
                      "struct_normalize.apply_to_files")

        # Link output DataManager
        self.add_link("func_normalize._normalized_files->"
                      "out_data_manager.unformated_normalized_func_image")
        self.add_link("struct_normalize._normalized_files->"
                      "out_data_manager.unformated_normalized_struct_image")

        # Export outputs
        self.export_parameter("norm_segment", "_transformation_mat",
                              pipeline_parameter="normalization_parameter")
        self.export_parameter("out_data_manager", "normalized_struct_image")
        self.export_parameter("out_data_manager", "normalized_func_image")

        # SPM Segment algorithm parameters
        tpm = get_sample_data('tpm')
        self.nodes["norm_segment"].process.gm_output_type = [True, False, True]
        self.nodes["norm_segment"].process.wm_output_type = [True, False, True]
        self.nodes["norm_segment"].process.csf_output_type = [
            False, False, False]
        self.nodes["norm_segment"].process.save_bias_corrected = True
        self.nodes["norm_segment"].process.clean_masks = "no"
        self.nodes["norm_segment"].process.tissue_prob_maps = [
            tpm.gm, tpm.wm, tpm.csf]
        self.nodes["norm_segment"].process.gaussians_per_class = [2, 2, 2, 4]
        self.nodes["norm_segment"].process.affine_regularization = "mni"
        self.nodes["norm_segment"].process.warping_regularization = 1
        self.nodes["norm_segment"].process.warp_frequency_cutoff = 25
        self.nodes["norm_segment"].process.bias_regularization = 0.0001
        self.nodes["norm_segment"].process.bias_fwhm = 60
        self.nodes["norm_segment"].process.sampling_distance = 3

        # SPM struct normalization algorithm parameters
        self.nodes["struct_normalize"].process.jobtype = "write"
        self.nodes["struct_normalize"].process.write_preserve = False
        self.nodes["struct_normalize"].process.write_bounding_box = [
            [-78, -112, -50], [78, 76, 85]]
        self.nodes["struct_normalize"].process.write_interp = 1
        self.nodes["struct_normalize"].process.write_wrap = [0, 0, 0]
        self.nodes["struct_normalize"].process.out_prefix = "w"
        self.nodes["struct_normalize"].process.voxel_sizes = [1., 1., 1.]

        # SPM func normalization algorithm parameters
        self.nodes["func_normalize"].process.jobtype = "write"
        self.nodes["func_normalize"].process.write_preserve = False
        self.nodes["func_normalize"].process.write_bounding_box = [
            [-78, -112, -50], [78, 76, 85]]
        self.nodes["func_normalize"].process.write_interp = 1
        self.nodes["func_normalize"].process.write_wrap = [0, 0, 0]
        self.nodes["func_normalize"].process.out_prefix = "w"
        self.nodes["func_normalize"].process.voxel_sizes = [3., 3., 3.]


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

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create FSL brain extraction pipeline
    norm_pipeline = SPMSegment()

    # Print Input Spec
    print norm_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    norm_pipeline.coregistered_struct_image = toy_dataset.mean
    norm_pipeline.func_image = toy_dataset.fmri

    # Execute the pipeline
    norm_working_dir = os.path.join(working_dir, "segment")
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
