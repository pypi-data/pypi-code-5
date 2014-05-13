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
from capsul.pipeline import Pipeline

# Trait import
try:
    from traits.api import List, Bool, File, Int, String, Float, Directory
except ImportError:
    from enthought.traits.api import (List, Bool, File, Int, String,
                                        Float, Directory)


##############################################################
#      FSL diffusion preprocessings Pipeline Definition
##############################################################

class FslDiffsuionPpreprocessings(Pipeline):
    """ FSL diffusion preprocessings

    * :ref:`Motion Correction <caps.diffusion_preproc.motion_correction.TimeSerieMotionCorrection>` (optional)
    * :ref:`Eddy Currents Correction <caps.diffusion_preproc.eddy_correction.EddyCorrection>`
    * :ref:`Susceptibility Artifacts Correction <caps.diffusion_preproc.susceptibility_correction.SusceptibilityCorrection>` (optional)

    .. note::

        This script rotates the b-vectors to ensure the consistency
        between the resulting nifti orientation and the b matrix table.
    """

    def pipeline_definition(self):
        """ Pipeline Definition
        """

        # Create processes
        self.add_process("bet", "caps.diffusion_preproc.bet.dBET")
        self.add_process("motion_correction",
        "caps.diffusion_preproc.motion_correction.TimeSerieMotionCorrection")
        self.add_process("eddy_correction",
                     "caps.diffusion_preproc.eddy_correction.EddyCorrection")
        self.add_process("merge_motion", "nipype.interfaces.fsl.Merge",
                         make_optional=["terminal_output", "dimension"])
        self.add_process("merge_eddy", "nipype.interfaces.fsl.Merge",
                         make_optional=["terminal_output", "dimension"])
        self.add_process("susceptibility_correction",
                         "caps.diffusion_preproc.susceptibility_correction."
                         "SusceptibilityCorrection")

        # Create switches
        self.add_switch("do_motion_correction", ["YES", "NO"],
                        ["reoriented_bvecs", "motion_corrected_files"])
        self.add_switch("do_susceptibility_correction", ["NO", "YES"],
                        ["corrected_file"])

        # Merge algorithms parameters
        self.nodes["merge_motion"].process.dimension = "t"
        self.nodes["merge_eddy"].process.dimension = "t"

        # Export Inputs
        self.export_parameter("bet", "dw_image")
        self.export_parameter("bet", "bvals")
        self.export_parameter("bet", "specified_index_of_ref_image")
        self.export_parameter("motion_correction", "bvecs")

        # Link input
        self.add_link("bvecs->"
                      "do_motion_correction.NO_switch_reoriented_bvecs")

        # Link bet
        self.add_link("bet.splited_images->motion_correction.in_files")
        self.add_link("bet.ref_image->motion_correction.reference_file")
        self.add_link("bet.ref_image->eddy_correction.reference_file")
        self.add_link("bet.splited_images->"
                      "do_motion_correction.NO_switch_motion_corrected_files")
        self.add_link("bet.bet_mask_file->susceptibility_correction.mask_file")

        # Link motion correction
        self.add_link("motion_correction.reoriented_bvecs->"
                      "do_motion_correction.YES_switch_reoriented_bvecs")
        self.add_link("motion_correction.motion_corrected_files->"
                      "do_motion_correction.YES_switch_motion_corrected_files")

        # Link switch motion
        self.add_link("do_motion_correction.motion_corrected_files->"
                      "eddy_correction.in_files")
        self.add_link("do_motion_correction.motion_corrected_files->"
                      "merge_motion.in_files")

        # Link eddy
        self.add_link("eddy_correction.eddy_corrected_files->"
                      "merge_eddy.in_files")

        # Link merge eddy
        self.add_link("merge_eddy._merged_file->"
                      "susceptibility_correction.dw_file")
        self.add_link("merge_eddy._merged_file->"
                      "do_susceptibility_correction.NO_switch_corrected_file")

        # Link susceptibility
        self.add_link("susceptibility_correction.susceptibility_"
                      "corrected_file->do_susceptibility_correction."
                      "YES_switch_corrected_file")

        # Export outputs:
        self.export_parameter("do_susceptibility_correction", "corrected_file")
        self.export_parameter("susceptibility_correction",
                              "susceptibility_corrected_file", weak_link=True)
        self.export_parameter("susceptibility_correction",
                              "unwrapped_phase_file", weak_link=True)
        self.export_parameter("motion_correction", "rigid_transformations",
                              weak_link=True)
        self.export_parameter("merge_motion", "_merged_file",
                              pipeline_parameter="motion_corrected_image")
        self.export_parameter("do_motion_correction", "reoriented_bvecs")
        self.export_parameter("merge_eddy", "_merged_file",
                              pipeline_parameter="eddy_corrected_files")
        self.export_parameter("eddy_correction", "affine_transformations")


##############################################################
#                            Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/caps"):
    """
    ============================
    FSL diffusion preprocessings
    ============================

    .. topic:: Objective

        We propose to correct some distortion of a diffusion sequence:
        Motion Correction - Eddy Currents Correction -
        Susceptibility Artifacts Correction (not tested yet)

    Import
    ------

    First we load the function that enables us to access the toy datasets
    """
    from caps.toy_datasets import get_sample_data

    """
    From capsul we then load the class to configure the study we want to
    perform
    """
    from capsul.study_config import StudyConfig

    """
    Here two utility tools are loaded. The first one enables the creation
    of ordered dictionary and the second ensure that a directory exist.
    Note that the directory will be created if necessary.
    """
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir

    """
    Load the toy dataset
    --------------------

    We want to perform BET on a diffusion sequence.
    To do so, we use the *get_sample_data* function to load this
    dataset.

    .. seealso::

        For a complete description of the *get_sample_data* function, see the
        :ref:`Toy Datasets documentation <toy_datasets_guide>`
    """
    toy_dataset = get_sample_data("dwi")

    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)

    """
    Will return:

    .. code-block:: python

        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

    We can see that the image has been found in a local directory

    Processing definition
    ---------------------

    Now we need to define the processing step that will perform the diffusion
    preprocessings.
    """
    fsl_preproc_pipeline = FslDiffsuionPpreprocessings()

    """
    It is possible to access the ipeline input specification.
    """
    print(fsl_preproc_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        do_motion_correction: ['Enum']
        do_susceptibility_correction: ['Enum']
        dw_image: ['File']
        bvals: ['File']
        specified_index_of_ref_image: ['Int']
        bvecs: ['File']
        terminal_output: ['Enum']
        generate_binary_mask: ['Bool']
        use_4d_input: ['Bool']
        generate_mesh: ['Bool']
        generate_skull: ['Bool']
        bet_threshold: ['Float']
        magnitude_file: ['File']
        phase_file: ['File']
        complex_phase_file: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi file and associated b-values and b-vectors:
    """
    fsl_preproc_pipeline.dw_image = toy_dataset.dwi
    fsl_preproc_pipeline.bvals = toy_dataset.bvals
    fsl_preproc_pipeline.bvecs = toy_dataset.bvecs

    """
    We activate the motion correction
    """
    fsl_preproc_pipeline.do_motion_correction = "YES"

    """
    And desactivate the susceptibility correction
    """
    fsl_preproc_pipeline.do_susceptibility_correction = "YES"

    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`
    """
    preproc_working_dir = os.path.join(working_dir, "fsl_preproc")
    ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(fsl_preproc_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        fsl_preproc_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

    """
    .. note::
        Since only the motion and eddy corrections has been selected,
        the *unwrapped_phase_file* and *susceptibility_corrected_file*
        are not specified.
        Thus the *corrected_file* output contains the motion-eddy corrected
        image.
    """

if __name__ == '__main__':
    pilot()
