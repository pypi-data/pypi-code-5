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
#         Conn Pipeline Definition
##############################################################

class Conn(Pipeline):
    """ Conn
    """

    def pipeline_definition(self):
        """ Pipeline definition
        """

        # Create processes
        self.add_process("manager",
            "caps.functional_connectivity.manager.InputDataManager")
        self.add_process("spreproc",
            "caps.functional_connectivity.spatial_preproc.SpatialPreproc",
            make_optional=["conn_batch"])
        self.add_process("setup",
            "caps.functional_connectivity.setup.Setup")
        self.add_process("tpreproc",
            "caps.functional_connectivity.temporal_preproc.TemporalPreproc")
        self.add_process("analysis",
            "caps.functional_connectivity.analysis.Analysis")
        self.add_process("results",
            "caps.functional_connectivity.results.Results")

        # Create switches
        self.add_switch("do_spatial_preproc", ["YES", "NO"],
                ["spreproc_functional_images", "spreproc_anatomical_images",
                 "normalized", "Grey_masks", "White_masks", "CSF_masks",
                 "realignment_covariate_files", "realignment_covariate_name",
                 "single_condition_name", "single_condition_onset",
                 "single_condition_duration"])

        # Export inputs
        self.export_parameter("manager", "functional_dir_name")
        self.export_parameter("manager", "anatomical_dir_name")
        self.export_parameter("setup", "output_directory")
        self.export_parameter("setup", "matlab_paths")
        self.export_parameter("setup", "execute_mfile",
                              pipeline_parameter="run_setup")
        self.export_parameter("tpreproc", "execute_mfile",
                              pipeline_parameter="run_tpreproc")
        self.export_parameter("analysis", "execute_mfile",
                              pipeline_parameter="run_analysis")
        self.export_parameter("results", "execute_mfile",
                              pipeline_parameter="run_results")

        # Link inputs
        self.add_link("output_directory->spreproc.output_directory")
        self.add_link("output_directory->tpreproc.output_directory")
        self.add_link("output_directory->analysis.output_directory")
        self.add_link("output_directory->results.output_directory")
        self.add_link("matlab_paths->tpreproc.matlab_paths")
        self.add_link("matlab_paths->analysis.matlab_paths")
        self.add_link("matlab_paths->results.matlab_paths")

        # Link manager
        self.add_link("manager.functional_paths->"
                      "spreproc.functional_paths")
        self.add_link("manager.anatomical_paths->"
                     "spreproc.anatomical_paths")
        self.add_link("manager.functional_paths->"
                      "setup.functional_paths")
        self.add_link("manager.anatomical_paths->"
                     "setup.anatomical_paths")

        # Link spreproc
        self.add_link("spreproc.normalized->"
                  "do_spatial_preproc.YES_switch_normalized")
        self.add_link("spreproc.spreproc_functional_images->"
                  "do_spatial_preproc.YES_switch_spreproc_functional_images")
        self.add_link("spreproc.spreproc_anatomical_images->"
                  "do_spatial_preproc.YES_switch_spreproc_anatomical_images")
        self.add_link("spreproc.Grey_masks->"
                  "do_spatial_preproc.YES_switch_Grey_masks")
        self.add_link("spreproc.White_masks->"
                  "do_spatial_preproc.YES_switch_White_masks")
        self.add_link("spreproc.CSF_masks->"
                  "do_spatial_preproc.YES_switch_CSF_masks")
        self.add_link("spreproc.realignment_covariate_files->"
                  "do_spatial_preproc.YES_switch_realignment_covariate_files")
        self.add_link("spreproc.realignment_covariate_name->"
                  "do_spatial_preproc.YES_switch_realignment_covariate_name")
        self.add_link("spreproc.single_condition_name->"
                  "do_spatial_preproc.YES_switch_single_condition_name")
        self.add_link("spreproc.single_condition_onset->"
                  "do_spatial_preproc.YES_switch_single_condition_onset")
        self.add_link("spreproc.single_condition_duration->"
                  "do_spatial_preproc.YES_switch_single_condition_duration")

        # Link switch
        self.add_link("do_spatial_preproc.normalized->"
                    "setup.normalized")
        self.add_link("do_spatial_preproc.spreproc_functional_images->"
                    "setup.functionals_from_spreproc")
        self.add_link("do_spatial_preproc.spreproc_anatomical_images->"
                    "setup.anatomicals_from_spreproc")
        self.add_link("do_spatial_preproc.Grey_masks->"
                    "setup.masks_Grey_files")
        self.add_link("do_spatial_preproc.realignment_covariate_files->"
                    "setup.covariates_files")
        self.add_link("do_spatial_preproc.realignment_covariate_name->"
                    "setup.covariates_names")
        self.add_link("do_spatial_preproc.single_condition_name->"
                    "setup.conditions_names")
        self.add_link("do_spatial_preproc.single_condition_onset->"
                    "setup.conditions_onsets")
        self.add_link("do_spatial_preproc.single_condition_duration->"
                    "setup.conditions_durations")

        # Link setup
        self.add_link("setup.conn_batch->tpreproc.batch_header")

        # Link tpreproc
        self.add_link("tpreproc.conn_batch->analysis.batch_header")

        # Link analysis
        self.add_link("analysis.conn_batch->results.batch_header")

        # Export outputs
        self.export_parameter("setup", "conn_batch",
                              pipeline_parameter="conn_batch_setup")
        self.export_parameter("tpreproc", "conn_batch",
                              pipeline_parameter="conn_batch_tpreproc")
        self.export_parameter("analysis", "conn_batch",
                              pipeline_parameter="conn_batch_analysis")
        self.export_parameter("results", "conn_batch",
                              pipeline_parameter="conn_batch_results")
                            
        self.node_position = {"analysis": (1153.1, -47.1),
                              "do_spatial_preproc": (446.9, -19.5),
                              "inputs": (-245.4, 337.9),
                              "manager": (83.1, 6.4),
                              "outputs": (1465.2, 136.8),
                              "results": (1338.8, 604.4),
                              "setup": (726.8, 264.7),
                              "spreproc": (288.9, 610.3),
                              "tpreproc": (1037.9, 607.2)}

##############################################################
#                     Pilot
##############################################################

def pilot(working_dir='/volatile/new/salma/', **kwargs):
    """
    ====
    Conn
    ====

    .. topic:: Objective

        Wrapping of the functional connectivity toolbox CONN 
        (https://www.nitrc.org/projects/conn/). Parallelization 

    Import
    ------

    First we load the function that enables us to access the toy datasets
    """
    from caps.toy_datasets import get_sample_data
    import numpy
    
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
    Load the classes to configure the manager and the different steps of the 
    functional connectivity pipeline
    """
    from caps.functional_connectivity.conn import Conn
    
    
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
    toy_dataset = get_sample_data("conn")

    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(toy_dataset.anatomicals, toy_dataset.functionals)

    """
    Will return:

    .. code-block:: python

        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

    We can see that the image has been found in a local directory

    Data Location
    -------------
    Now we give the data location and the prefixes of the images as input 
    parameters for the manager:
    * the path to the parent directory for all the subjects subdirectories, 
    * the name of the functional and anatomical directories 
    * the prefixes of the functional and anatomical images to include. 

    The following tree is assumed:
    
    .. code-block:: python

        manager.data_path
        |---manager.subjects[0]
        |    |---manager.functional_dir_name (folder or recursive folders)
        |    |    |---manager.raw_functional_prefixes[0]
        |    |    |
        |    |    |---manager.raw_functional_prefixes[-1]
        |    |    :
        |    |    :...other possible folders or files
        |    |
        |    |---manager.anatomical_dir_name (folder or recursive folders)
        |    |    |---manager.raw_anatomical_prefix
        |    |    :
        |    |    :...other possible files
        |    |
        |    :...other possible folders or files
        |
        |---manager.subjects[-1]
        |    |---manager.functional_dir_name
        |    |    |---manager.raw_functional_prefixes[0]
        |    |    :
        |    |    |---manager.raw_functional_prefixes[-1]
        |    |    :
        |    |---manager.anatomical_dir_name
        |    |    |---manager.raw_anatomical_prefix
        |    |    :
        |    :
        |
        :...other possible folders or files     
    """
    conn_pipeline = Conn()

    conn_pipeline.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    conn_pipeline.functional_dir_name = "func"
    conn_pipeline.anatomical_dir_name = "anat"
    conn_pipeline.sp_functional_prefixes = ["swralfo*.nii"]
    conn_pipeline.sp_anatomical_prefix = "wmmprage_a*.nii"
    conn_pipeline.Grey_masks_prefix = "mwc1mprage_a*.nii"
    conn_pipeline.White_masks_prefix = "mwc2mprage_a*.nii"
    conn_pipeline.CSF_masks_prefix = "mwc3mprage_a*.nii"
    conn_pipeline.covariates_names = ["Realignment"]
    conn_pipeline.covariates_prefixes = [["rp_alfo*.txt"]]
    conn_pipeline.conditions_names = ["Session"]
    conn_pipeline.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(1)] for nsub in xrange(3)] for ncond in range(1)]  # TODO: move it to manager?
    conn_pipeline.conditions_durations = [[[numpy.nan if nsess != ncond else 
    numpy.inf for nsess in range(1)] for nsub in xrange(1)]for ncond in range(1)] # TODO: move it to manager?

    """
    You can run a complete or a partial spatial preprocessing pipeline on the
    data, or simply skip this step if your data has been already spatially
    preprocessed.
    """
    conn_pipeline.raw_functional_prefixes = ["lfo*.nii"]
    conn_pipeline.raw_anatomical_prefix = "mprage_a*.nii"
    conn_pipeline.steps = ["segmentation", "realignment", "coregistration",
                      "normalization", "smoothing"]
    """
    Set the parameters for the Setup step
    """
    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"

    """
    Set the parameters for the Analysis step
    """
    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.functionals = manager.spreproc_functional_images
    setup.anatomicals = manager.spreproc_anatomical_images
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in xrange(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in xrange(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"
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
    conn_working_dir = os.path.join(working_dir, "conn")
    # ensure_is_dir(preproc_working_dir)
    default_config = SortedDictionary(
        ("output_directory", conn_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    # study.run(conn_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print "\nOUTPUTS\n"
    for trait_name, trait_value in conn_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

    """
    .. note::
        Since only the motion and eddy corrections has been selected,
        the *unwrapped_phase_file* and *susceptibility_corrected_file*
        are not specified.
        Thus the *corrected_file* output contains the motion-eddy corrected
        image.
    """

if __name__ == "__main__":
    pilot()
