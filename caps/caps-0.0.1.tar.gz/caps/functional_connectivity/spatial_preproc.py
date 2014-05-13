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
import glob

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, List, Directory, Str, Int, Enum, Float,
                            Dict, Any)
except ImportError:
    from enthought.traits.api import (File, List, Directory, Str, Int, Enum,
                                      Float, Dict, Any)
# Numpy import
import numpy

# Caps import
from matlab_utils import ConnProcess, join_functionals, join_anatomicals


class SpatialPreproc(ConnProcess):
    """ Spatial fMRI preproc with CONN (realignment/slicetiming/ "
    "coregistration/segmentation/normalization/smoothing) and initialization"
    "of conn_* project
    """
    jobname = "New"

    def __init__(self):
        super(SpatialPreproc, self).__init__()

        # Inputs without fields
        self.add_trait("raw_functional_prefixes", List(Str(),
                        optional=False,
                        output=False,
                        desc="the prefixes of the raw functional images"
                             "associated to the sessions to include"))
        self.add_trait("raw_anatomical_prefix", Str(
                        optional=False,
                        output=False,
                        desc="the prefix of the raw anatomical images"))
        self.add_trait("functional_paths", List(Directory(),
                        optional=False,
                        output=False,
                        desc="paths to all subjects functional directories"))
        self.add_trait("anatomical_paths", List(Directory(),
                        optional=False,
                        output=False,
                        desc="paths to all subjects anatomical directories"))

        # Inputs
        self.add_trait("nessions", Int(
            _Undefined(),
            optional=True,
            output=False,
            desc="Number of sessions"))
        self.add_trait("nsubjects", Int(
            _Undefined(),
            optional=True,
            output=False,
            desc="Number of subjects"))
        self.add_trait("steps", List(Str(),
            ["segmentation", "slicetiming", "realignment", "coregistration",
             "normalization", "smoothing"],
            optional=False,
            output=False,
            field="steps",
            desc=("spatial preprocessing steps. Default to all steps: "
                  "['segmentation','slicetiming', "
                  "'realignment','coregistration','normalization', "
                  "'smoothing']")))
        self.add_trait("raw_functional_images", List(List(List(File())),
            optional=False,
            output=False,
            field="functionals",
            desc="the functional files to spatially preprocess"))
        self.add_trait("raw_anatomical_images", List(File(),
            optional=False,
            output=False,
            field="structurals",
            desc="the anatomical files to spatially preprocess"))
        self.add_trait("t_r", Float(
            _Undefined(),
            optional=False,
            output=False,
            field="RT",
            desc="Repetition time (seconds) [2]"))
        self.add_trait("smoothing_fwhm", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="FWHM",
            desc="Smoothing factor (mm) [8]"))
        self.add_trait("voxel_size", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="VOX",
            desc="target voxel size (mm) [2]"))
        self.add_trait("slice_order", Any( # TODO correct bug with numpy arrays
            _Undefined(),
            optional=True,
            output=False,
            field="sliceorder",
            desc="(option for slicetiming step) acquisition order (vector of "
                 "indexes; 1=first slice in image)"))
        self.add_trait("template_structural", File(
            optional=True,
            output=False,
            field="template_structural",
            desc="anatomical template file for approximate coregistration "
                 "[spm/template/T1.nii]"))
        self.add_trait("template_functional", File(
            optional=True,
            output=False,
            field="template_functional",
            desc="functional template file for normalization "
                 "[spm/template/EPI.nii]"))

        # Outputs
        self.add_trait("normalized", Int(
            _Undefined(),
            optional=True,
            output=True,
            desc="1/0 are the spatially preprocessed images normalized or not"))
        self.add_trait("spreproc_functional_images", List(List(List(File())),
            output=True,
            desc="spatially preprocessed functionale images"))
        self.add_trait("spreproc_anatomical_images", List(File(),
            output=True,
            desc="spatially preprocessed anatomical images"))
        self.add_trait("Grey_masks", List(File(),
            output=True,
            optional=True,
            desc="the spatially preprocessed Grey masks, output of"
            "segmentation step"))
        self.add_trait("White_masks", List(File(),
            output=True,
            optional=True,
            desc="the spatially preprocessed White masks, output of"
            "segmentation step"))
        self.add_trait("CSF_masks", List(File(),
            output=True,
            optional=True,
            desc="the spatially preprocessed CSF masks, output of"
            "segmentation step"))
        self.add_trait("realignment_covariate_files", List(List(List(File())),
            output=True,
            optional=True,
            desc="the realignment parameters files output of"
            "realignment step"))
        self.add_trait("realignment_covariate_name", List(Str(),
            optional=True,
            output=True,
            desc="name of the realignment covariate"))
        self.add_trait("single_condition_name", List(Str(),
            optional=True,
            output=True,
            desc="one single condition named 'Session' set to model the "
                 "entire session data"))
        self.add_trait("single_condition_onset", List(List(List(Float())),
            optional=True,
            output=True,
            desc="onset 0.0 for the single condition"))
        self.add_trait("single_condition_duration", List(List(List(Float())),
            optional=True,
            output=True,
            desc="duration inf for the single condition"))

# TODO if field new is defined, the functional and anatomical fields of the setup step must not be entered

    def _steps_changed(self, old_trait_value, new_trait_value):
        """ Event to force mandatory traits to be non optional
        """
        if "slice timing" in new_trait_value:
            self.slice_order.optional = False

        if "coregistration" in new_trait_value or "normalization" in \
        new_trait_value:
            self.voxel_size.optional = False

        if "smoothing" in new_trait_value:
            self.smoothing_fwhm.optional = False
            
    def _raw_functional_images_changed(self, old_trait_value, new_trait_value):
        """ Event to set the number of sessions and subjects
        """
        self.nsessions = len(new_trait_value)
        self.nsubjects = len(new_trait_value[0])

        
    def _run_process(self):
        """ Method to acess the Matlab script of the CONN module.
        """
        # Remove the conn_study .mat file and directory
        if os.path.isfile(self.mat_filename):
            os.remove(self.mat_filename)

        conn_directory = os.path.join(self.output_directory,
                                      os.path.splitext(self.mat_filename)[0])
        if os.path.isdir(conn_directory):
            for subdir in os.listdir(conn_directory):
                if subdir in ["data", "results"]:
                    rm_nonempty_dir(os.path.join(conn_directory, subdir))

        # Paths to images
        self.raw_functional_images = join_functionals(
        self.functional_paths, self.raw_functional_prefixes)
        self.raw_anatomical_images = join_anatomicals(
        self.anatomical_paths, self.raw_anatomical_prefix)

            

        # Read the prefixes of spatially preprocessed data from .mat file
        spreproc_matfile = os.path.join(
        self.output_directory, "connsetup_wizard_job1.mat")
        try:
            prefixes = self._load_conn_parameters(spreproc_matfile)["prefix"]
            for prefix in prefixes:
                prefix = str(prefix)
                if prefix == "[]":
                    prefix = ""
        except IOError:
            raise IOError("Unable to read variable 'prefix' form file {0}, "
            "something went wrong with spatial preprocessing".format(
            spreproc_matfile))

        # Form the paths to spatially preprocessed data
        func_prefix = str(prefixes[0])
        anat_prefix = str(prefixes[1])
        mask_prefix = str(prefixes[2])
        if "coregistration" in self.steps and \
        not "normalization" in self.steps:
            self.normalized = 1
        else:
            self.normalized = 0

        self.spreproc_functional_images = [[[func_prefix + \
        os.path.split(path)[0] for path in sublist2] for sublist2 in sublist1]
        for sublist1 in self.raw_functional_images]
        self.anatomical_images = [anat_prefix + path for path in
        self.raw_anatomical_images]

        if "segmentation" in self.steps:
            self.Grey_masks = [mask_prefix + "c1" + path for path in
            self.raw_anatomical_images]
            self.White_masks = [mask_prefix + "c2" + path for path in
            self.raw_anatomical_images]
            self.CSF_masks = [mask_prefix + "c3" + path for path in
            self.raw_anatomical_images]

        if "realignment" in self.steps:
            self.realignment_covariate_files = [[["rp_" + func_prefix + \
            os.path.splitext(os.path.split(path)[0])[0] + ".txt"
            for path in sublist2] for sublist2 in sublist1]
            for sublist1 in self.raw_functional_images]
            self.realignment_covariate_name = ["realignment"]
        self.nsubjects = len(self.raw_functional_images)
        self.nsessions = len(self.raw_functional_images[0])            
        self.single_condition_name = ["Session"]
        self.single_condition_onset = [[[0.0 for nsess in 
        xrange(self.nsessions)] for nsub in xrange(self.nsubjects)] for ncond in xrange(1)]
        self.single_condition_duration = [[[numpy.inf for nsess in 
        xrange(self.nsessions)] for nsub in xrange(self.nsubjects)] for ncond in xrange(1)]
        
# TODO use in spreproc output traits

 #           self.realignment_files = self.join_functionals(
 #           [prefix + os.path.splitext(run)[0] + extension for run in
 #           self.functional_prefixes])
        # TODO sanity checks


        return self.run()


def rm_nonempty_dir(dir_path):
    """ Removes a non empty directory.

    Parameters
    ==========
    dir_path: str
        path to the directory to remove
    """
    if not os.path.isdir(dir_path):
        raise OSError("Not a directory: " + dir_path)

    contents = glob.glob(os.path.join(dir_path, "*"))
    for content in contents:
        if os.path.isdir(content):
            rm_nonempty_dir(content)
        else:
            os.remove(content)

    os.rmdir(dir_path)


if __name__ == '__main__':

    from setup import InputDataManager

    manager = InputDataManager()
    manager.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    manager.functional_dir_name = "func"
    manager.anatomical_dir_name = "anat"
    manager()

    # Spatial preproc step
    spreproc = SpatialPreproc()
    spreproc.output_directory = "/volatile/new/salma/test_NSAP_NYU"
    spreproc.matlab_paths = ["/i2bm/local/spm8-5236",
                             "/volatile/new/salma/conn"]
    spreproc.matlab_cmd = "/neurospin/local/bin/matlab"
    spreproc.raw_functional_prefixes = ["lfo*.nii"]
    spreproc.raw_anatomical_prefix = "mprage_a*.nii"
    spreproc.functional_paths = manager.functional_paths
    spreproc.anatomical_paths = manager.anatomical_paths
    spreproc.steps = ["segmentation", "realignment", "coregistration",
                      "normalization", "smoothing"]
    # TODO add spreproc.slice_order = np.arange(1,40)
    spreproc.execute_mfile = False
    runtime = spreproc._run_process()
    print runtime[0]
    print runtime[1]
    print runtime[2]
    print spreproc.mlabcmdline