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
import logging

# Capsul import
from capsul.pipeline import Pipeline
from capsul.process import Process

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (List, Bool, File, Int, Str, Float, Directory, Either)
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import (List, Bool, File, Int, Str,
                                      Float, Directory, Either)
# Pypreprocess import
try:
    from pypreprocess.nipype_preproc_spm_utils import do_subject_preproc
    from pypreprocess.subject_data import SubjectData
except:
    logging.error("Can't import 'pypreprocess' properly. Please investigate.")


##############################################################
#                       Process definition
##############################################################

class SPMSubjectPreprocessing(Process):
    """ Preprocessing fMRI data for a single subject with SPM.
    """

    def __init__(self):
        """ Initialize the SPMSubjectPreprocessing class
        """
        # Inheritance
        super(SPMSubjectPreprocessing, self).__init__()

        # Inputs
        self.add_trait("func_file", Either(
            File(), List(File()),
            _Undefined(),
            optional=False,
            output=False,
            desc="Path to the functional image(s)"))
        self.add_trait("anat_file", File(
            _Undefined(),
            exists=True,
            optional=False,
            output=False,
            desc="Path to the anatomical image"))
        self.add_trait("output_directory", Directory(
            os.getcwd(),
            exists=True,
            optional=True,
            output=False,
            desc="Path to the output directory"))
        self.add_trait("slice_time", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, then the functional data will be correction for "
                  "slice timing distortions.")))
        self.add_trait("realign", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, then the functional data will be realigned to "
                  "correct for head-motion.")))
        self.add_trait("coregister", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, the functional and anatomical "
                  "images will be corregistered. If this "
                  "not set, and anatomical image is defined, it is assumed "
                  "that functional and anatomical images have already "
                  "been coregistered.")))
        self.add_trait("coreg_anat_to_func", Bool(
            False,
            optional=True,
            output=False,
            desc=("If set, then functional data will be the reference "
                  "during coregistration. By default the anatomical data "
                  "if the reference, to ensure a precise registration "
                  "(since anatomical data has finer resolution)")))
        self.add_trait("segment", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, then the subject's anatomical image will be "
                  "segmented to produce GM, WM, and CSF compartments "
                  "(useful for both indirect normalization (intra-subject) "
                  "or DARTEL (inter-subject) alike")))
        self.add_trait("normalize", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, then the subject_data (functional and anatomical) "
                  "will be warped into MNI space")))
        self.add_trait("fwhm", Either(List(Float()), Float(),
            _Undefined(),
            optional=False,
            output=False,
            desc=("FWHM for smoothing the functional data. "
                  "If normalize is set, then this parameter is based to "
                  "spm.Normalize, else spm.Smooth is used to explicitly smooth "
                  "the functional data.")))
        self.add_trait("repetition_time", Float(
            0,
            optional=False,
            output=False,
            desc=("The repetition time of the functional iamge acquisition "
                  "sequence.")))
        self.add_trait("slice_order", List(Int(),
            optional=False,
            output=False,
            desc=("The acquistion order of each slice of the functional iamge.")))
        self.add_trait("use_smart_caching", Bool(
            True,
            optional=True,
            output=False,
            desc=("If set, then use nipype smart-caching.")))

        # Ouputs
        self.add_trait("slice_time_corrected_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The functional slice time corrected image(s)."))
        self.add_trait("realign_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The functional realigned image(s) (head-motion correction)."))
        self.add_trait("transformation_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The functional realigned transformation parameters."))
        self.add_trait("mean_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The functional realigned mean image."))

        self.add_trait("coregister_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The coregister image(s)."))
        self.add_trait("segment_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc=""))
        self.add_trait("normalize_func_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The normalize file(s)"))
        self.add_trait("normalize_anat_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The normalize file(s)"))
        self.add_trait("smooth_normalize_func_file", Either(
            File(), List(File()),
            _Undefined(),
            output=True,
            desc="The normalize and smoothed functional file(s)"))


    def _run_process(self):
        """ Execution of the SPMSubjectPreprocessing class
        """
        # Create the data structure
        subject_data = SubjectData(
            func=self.func_file,
            anat=self.anat_file,
            subject_id="sub001",
            output_dir=self.output_directory)

        # Call the preprocessing function
        do_subject_preproc(
            subject_data, deleteorient=False, slice_timing=self.slice_time,
            slice_order=self.slice_order, interleaved=False, refslice=1,
            TR=self.repetition_time, TA=None, slice_timing_software="spm",
            realign=self.realign, realign_reslice=False, register_to_mean=True,
            realign_software="spm", coregister=self.coregister,
            coregister_reslice=False, coreg_anat_to_func=self.coreg_anat_to_func,
            coregister_software="spm", segment=self.segment,
            normalize=self.normalize, dartel=False,
            fwhm=self.fwhm, anat_fwhm=0., func_write_voxel_sizes=None,
            anat_write_voxel_sizes=None, hardlink_output=True, report=False,
            cv_tc=False, caching=self.use_smart_caching)

        # Get the resulting images
        for interface_name, result_name, trait_name in [
            ("slice_timing", "timecorrected_files", "slice_time_corrected_file"),
            ("realign", "realigned_files", "realign_file"),
            ("realign", "realignment_parameters", "transformation_file"),
            ("realign", "mean_image", "mean_file"),
            ("coreg", "coregistered_files", "coregister_file"),
            ("normalize_func", "normalized_files", "normalize_func_file"),
            ("normalize_anat", "normalized_files", "normalize_anat_file"),
            ("smooth", "smoothed_files", "smooth_normalize_func_file")]:

            if interface_name in subject_data.nipype_results:

                outputs = []
                interface_results = subject_data.nipype_results[
                    interface_name]
                if not isinstance(interface_results, list):
                    interface_results = [interface_results]
                for interface_result in interface_results:
                    if interface_name == "smooth":
                        interface_result = interface_result["func"]
                    outputs.append(
                        getattr(interface_result.outputs, result_name))

                if len(outputs) == 1:
                    setattr(self, trait_name, outputs[0])
                else:
                    setattr(self, trait_name, outputs)


##############################################################
#                       Pipeline definition
##############################################################

class SubjectPreprocessing(Pipeline):
    """ Preprocessing fMRI data for a single subject.
    """

    def pipeline_definition(self):
        """ Pipeline definition
        """

        # Create Processes
        self.add_process("preproc", "caps.functional_preproc."
                         "pypreprocess_fmri_preproc.SPMSubjectPreprocessing")

        # Export input
        self.export_parameter("preproc", "slice_time")
        self.export_parameter("preproc", "realign")
        self.export_parameter("preproc", "coregister")
        self.export_parameter("preproc", "normalize")
        self.export_parameter("preproc", "segment")
        self.export_parameter("preproc", "coreg_anat_to_func")

        # Node positions
        self.node_position = {
            "inputs": (-150.0, 119.0),
            "outputs": (381.0, 223.0),
            "preproc": (111.0, 76.0)}


##############################################################
#                            Pilot
##############################################################

def pilot():
    r"""
    ==================================
    Functional Spatial Preprocessings
    ==================================

    .. topic:: Objective

        We propose here to spatialy correct functional images using
        PyPreProcess (SPM).

    Import
    ------

    First we load the function that enables us to access the toy datasets:
    """
    from caps.toy_datasets import get_sample_data

    """
    From capsul we then load the class to configure the study we want to
    perform:
    """
    from capsul.study_config import StudyConfig

    """
    Here two utility tools are loaded. The first one enables the creation
    of ordered dictionary and the second ensure that a directory exists.
    Note that the directory will be created if necessary.
    """
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    """
    We need some generic python modules:
    """
    import os
    import numpy

    """
    From caps we need the pipeline that will enable use to do the functional
    spatial preprocessings:
    """
    from caps.functional_preproc.pypreprocess_fmri_preproc import (
        SPMSubjectPreprocessing)

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`

    We first define the current working directory:
    """
    working_dir = "/volatile/nsap/caps"
    preproc_working_dir = os.path.join(working_dir, "functional_preroc")
    ensure_is_dir(preproc_working_dir)

    """
    And then define the study configuration:
    """
    default_config = SortedDictionary(
        ("output_directory", preproc_working_dir),
        ("spm_directory", "/i2bm/local/spm8-5236"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", False),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)

    """
    Load the toy dataset
    --------------------

    We want to perform a second order tensor fit on a diffusion sequence data.
    To do so, we use the *get_sample_data* function to load the
    dataset:

    .. seealso::

        For a complete description of the *get_sample_data* function, see the
        :ref:`Toy Datasets documentation <toy_datasets_guide>`
    """
    toy_dataset = get_sample_data("localizer")

    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *fmri*, *anat*, *TR* that contains
    the nifti functional image, the nifti anatomical image,
    and the repetition time respectively.
    """
    timings = list(range(1, 41))
    print(toy_dataset.fmri, toy_dataset.anat, toy_dataset.TR, timings)

    """
    Processing definition
    ---------------------

    Now we need to define the processing step that will perform the
    functional spatial preprocessings:
    """
    preproc_pipeline = SPMSubjectPreprocessing()

    """
    It is possible to access the pipeline input specifications:
    """
    print(preproc_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        func_file: ['File']
        anat_file: ['File']
        output_directory: ['Directory']
        slice_time: ['Bool']
        realign: ['Bool']
        coregister: ['Bool']
        coreg_anat_to_func: ['Bool']
        segment: ['Bool']
        normalize: ['Bool']
        fwhm: ['List_Float', 'Float', 'TraitInstance']
        repetition_tile: ['Float']
        slice_order: ['List_Int']

    We can now tune the pipeline parameters:
    """
    preproc_pipeline.func_file = toy_dataset.fmri
    preproc_pipeline.anat_file = toy_dataset.anat
    preproc_pipeline.repetition_time = toy_dataset.TR
    preproc_pipeline.slice_order = timings
    preproc_pipeline.fwhm = [5, 5, 5]
    preproc_pipeline.coreg_anat_to_func = False

    """
    Before running the pipeline, you need to select the spatial preproc that
    will be performed:
    """
    preproc_pipeline.slice_time = True
    preproc_pipeline.realign = True
    preproc_pipeline.coregister = True
    preproc_pipeline.segment = True
    preproc_pipeline.normalize = True

    """
    You can also specify that you want to activate nipype smart-caching
    """
    preproc_pipeline.use_smart_caching = True

    """
    The pipeline is now ready to be run
    """
    study.run(preproc_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print("\nOUTPUTS\n")
    for trait_name, trait_value in preproc_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))


if __name__ == "__main__":
    SPMSubjectPreprocessing()
    pilot()
