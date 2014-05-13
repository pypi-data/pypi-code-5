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
except ImportError:
    from enthought.traits.api import File, Float, Int, List, Any, Str

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
        self.add_trait("coregistered_struct_image", File(optional=False))
        self.add_trait("func_image", File(optional=False))

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
        self.add_trait("list_image",
                       List(File(), optional=False))

        # Outputs
        self.add_trait("image",
                       File(optional=False, output=True))

    def _run_process(self):
        self.image = self.list_image[0]

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

class SPMNewSegment(Pipeline):
    """ SPM structural and functional normalization to template.

    Steps:
        * Segement or NewSegment: Structural Normalization anat -> ICBM
        * Functional/Structural normalization
    """

    def pipeline_definition(self):

        # Create process
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.spm_new_segment.InputDataManager")
        self.add_process("norm_new_segment",
                         "nipype.interfaces.spm.NewSegment")
        self.add_process("list_converter",
                         "caps.preclinic_functional.spm_new_segment.ListDataManager")
        self.add_process("struct_normalize",
                         "nsap.nipype.spm_interface.ApplyDeformationField",
                         make_optional=["source", "template"])
        self.add_process("func_normalize",
                         "nsap.nipype.spm_interface.ApplyDeformationField",
                         make_optional=["source", "template"])
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.spm_new_segment.OutputDataManager")

        # Export inputs
        self.export_parameter("in_data_manager", "coregistered_struct_image")
        self.export_parameter("in_data_manager", "func_image")
        self.export_parameter("struct_normalize", "voxel_sizes",
                              pipeline_parameter="struct_voxel_sizes")
        self.export_parameter("func_normalize", "voxel_sizes",
                              pipeline_parameter="func_voxel_sizes")
                              
        # Link input DataManager
        self.add_link("in_data_manager.output_coregistered_struct_image->"
                      "norm_new_segment.channel_files")
        self.add_link("in_data_manager.output_func_image->"
                      "func_normalize.in_files")

        # Link NewSegment
        self.add_link("norm_new_segment._forward_deformation_field->"
                      "list_converter.list_image")
        self.add_link("norm_new_segment._bias_corrected_images->"
                      "struct_normalize.in_files")

        # Link list DataManager
        self.add_link("list_converter.image->"
                      "struct_normalize.deformation_field")
        self.add_link("list_converter.image->"
                      "func_normalize.deformation_field")

        # Link output DataManager
        self.add_link("func_normalize._normalized_files->"
                      "out_data_manager.unformated_normalized_func_image")
        self.add_link("struct_normalize._normalized_files->"
                      "out_data_manager.unformated_normalized_struct_image")

        # Export outputs
        self.export_parameter("list_converter", "image",
                              pipeline_parameter="normalization_parameter")
        self.export_parameter("out_data_manager", "normalized_struct_image")
        self.export_parameter("out_data_manager", "normalized_func_image")

        # SPM NewSegment algorithm parameters
        tmp_image = get_sample_data('tpm').all
        tissue1 = ((tmp_image, 1), 2, (True, True), (False, True))
        tissue2 = ((tmp_image, 2), 2, (True, True), (False, True))
        tissue3 = ((tmp_image, 3), 2, (True, False), (False, False))
        tissue4 = ((tmp_image, 4), 3, (False, False), (False, False))
        tissue5 = ((tmp_image, 5), 4, (False, False), (False, False))
        self.nodes["norm_new_segment"].process.tissues = [
            tissue1, tissue2, tissue3, tissue4, tissue5]
        self.nodes["norm_new_segment"].process.channel_info = (
            (0.0001, 60, (True, True)))
        self.nodes["norm_new_segment"].process.affine_regularization = "mni"
        self.nodes["norm_new_segment"].process.warping_regularization = 4
        self.nodes["norm_new_segment"].process.sampling_distance = 3
        self.nodes["norm_new_segment"].process.write_deformation_fields = [
            True, True]

        # SPM struct apply field algorithm parameters
        self.nodes["struct_normalize"].process.bounding_box = [
            [-78, -112, -50], [78, 76, 85]]
        self.nodes["struct_normalize"].process.interpolation = 1
        self.voxel_sizes = [1., 1., 1.]
        
        # SPM func apply field algorithm parameters
        self.nodes["func_normalize"].process.bounding_box = [
            [-78, -112, -50], [78, 76, 85]]
        self.nodes["func_normalize"].process.interpolation = 1
        self.voxel_sizes = [3., 3., 3.]

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
    norm_pipeline = SPMNewSegment()

    # Print Input Spec
    print norm_pipeline.get_input_spec()

    # Initialize Normalization pipeline
    norm_pipeline.coregistered_struct_image = toy_dataset.mean
    norm_pipeline.func_image = toy_dataset.fmri

    # Execute the pipeline
    norm_working_dir = os.path.join(working_dir, "newsegment")
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
