#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import numpy

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, List, Directory, Str, Int, Enum, Float,
                            Dict, Any)
except ImportError:
    from enthought.traits.api import (File, List, Directory, Str, Int, Enum,
                                      Float, Dict, Any)

# Caps import
from matlab_utils import (ConnProcess, join_functionals, join_anatomicals,
                          join_covariates)

##############################################################
#         Setup process definition
##############################################################


class Setup(ConnProcess):
    """ Conn setup
    """
    jobname = "Setup"

    def __init__(self):
        super(Setup, self).__init__()

        # Inputs without fields
        # Paths
        self.add_trait("functionals_from_spreproc", List(List(List(File())),
            optional=False,
            output=False,  # TODO replace by direct link from spreproc to functionals
            desc="the spatially preprocessed functional files, output from "
                 "conn spatial preprocessing pipiline"))
        self.add_trait("anatomicals_from_spreproc", List(File(),
            optional=False,
            output=False,  # TODO replace by direct link from spreproc to anatomicals
            desc="the spatially preprocessed anatomical files, output from "
                 "conn spatial preproc pipiline"))
        self.add_trait("functional_paths", List(Directory(),
                        optional=False,
                        output=False,
                        desc="paths to all subjects functional directories"))
        self.add_trait("anatomical_paths", List(Directory(),
                        optional=False,
                        output=False,
                        desc="paths to all subjects anatomical directories"))
        # Prefixes
        self.add_trait("sp_functional_prefixes", List(Str(),
                        optional=False,
                        output=False,
                        desc="the prefixes of the spatially preprocessed "
                        "functional images associated to the sessions "
                        "to include"))
        self.add_trait("sp_anatomical_prefix", Str(
                        optional=False,
                        output=False,
                        desc="the prefix of the spatially preprocessed "
                        "anatomical images"))
        self.add_trait("Grey_masks_prefix", Str(
                        optional=True,
                        output=False,
                        desc="the prefix of spatially preprocessed "
                        "Grey masks"))
        self.add_trait("White_masks_prefix", Str(
                        optional=True,
                        output=False,
                        desc="the prefix of spatially preprocessed "
                        "White masks"))
        self.add_trait("CSF_masks_prefix", Str(
                        optional=True,
                        output=False,
                        desc="the prefix of spatially preprocessed "
                        "CSF masks"))
        self.add_trait("covariates_prefixes", List(List(Str()),
                        optional=True,
                        output=False,
                        desc="the prefixes of covariates files for all "
                        "sessions, of length number of covariates"))

        # Inputs with fields
        # Generic
        self.add_trait("isnew", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="isnew",
            desc="1/0 is this a new conn project [0]"))
        self.add_trait("done", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="done",
            desc=("1/0, [0]. 0: only edits project fields (do not run Setup"
                  "->'Done'); 1: run Setup->'Done'")))
        self.add_trait("overwrite", Enum(
            ["Yes", "No"],
            optional=True,
            output=False,
            field="overwrite",
            desc="overwrite existing results if they exist ['Yes']"))
        self.add_trait("nsubjects", Int(
            optional=False,
            output=False,
            field="nsubjects",
            desc="Number of subjects"))
        self.add_trait("functionals", List(List(List(File())),
            optional=False,
            output=False,
            field="functionals",
            desc="the functional files"))
        self.add_trait("anatomicals", List(File(),
            optional=False,
            output=False,
            field="structurals",
            desc="the anatomical files"))
        self.add_trait("normalized", Int( # TODO deal with this field, see conn
            _Undefined(),
            optional=True,
            output=False,
            desc="1/0 are the spatially preprocessed images normalized"
            "or not"))
        self.add_trait("t_r", Float(
            _Undefined(),
            optional=True,
            output=False,
            field="RT",
            desc="Repetition time (seconds) [2]"))
        self.add_trait("analysis", Any(
            _Undefined(),
            optional=True,
            output=False,
            field="analysis",
            desc=("Vector of index to analysis types (1: ROI-to-ROI; 2: "
                  "Seed-to-voxel; 3: Voxel-to-voxel) [1,2]")))

        # Masks
        self.add_trait("masks_White_files", List(File(),
            optional=True,
            output=False,
            field="masks.White.files",
            desc=("white matter mask volume file [defaults to White mask "
                  "extracted from structural volume]")))
        self.add_trait("masks_White_dimensions", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="masks.White.dimensions",
            desc=("Number of PCA components extracted from "
                             "the white matter [16]")))
        self.add_trait("masks_Grey_files", List(File(),
                optional=True,
                output=False,
                field="masks.Grey.files",
                desc=("grey matter mask volume file [defaults to "
                     "Grey mask extracted from structural volume]")))
        self.add_trait("masks_Grey_dimensions", Int(
                        _Undefined(),
                        optional=True,
                        output=False,
                        field="masks.Grey.dimensions",
                        desc=("Number of PCA components extracted from "
                             "the grey matter [1]")))
        self.add_trait("masks_CSF_files", List(File(),
                optional=True,
                output=False,
                field="masks.CSF.files",
                desc=("CSF mask volume file [defaults to "
                     "CSF mask extracted from structural volume]")))
        self.add_trait("masks_CSF_dimensions", Int(
                        _Undefined(),
                        optional=True,
                        output=False,
                        field="masks.CSF.dimensions",
                        desc=("Number of PCA components extracted from "
                             "the csf matter [16]")))

        # ROIs
        self.add_trait("rois_files", List(File(),
            optional=True,
            output=False,
            field="rois.files",
            desc="List of ROIs files"))  # TODO correct conn_batch.m to include default ROIs
        self.add_trait("rois_names", List(Str(),
                        optional=True,
                        output=False,
                        field="rois.names",
                        desc="ROIs names, default to ROIs files"))
        self.add_trait("rois_dimensions", List(Str(),
            optional=True,
            output=False,
            field="rois.dimensions",
            desc=("number of dimensions characterizing each ROI activation. "
                  "(1 represents only the mean BOLD activity within the ROI; "
                  "2 and above includes additional PCA [1]")))
        self.add_trait("rois_mask", List(Int(),
                        optional=True,
                        output=False,
                        field="rois.mask",
                        desc="Mask with Grey Matter [0]"))  # TODO either trait 
                        # int (0,1) or list of int of size len names
        self.add_trait("rois_multiplelabels", List(Int(),
                        optional=True,
                        output=False,
                        field="rois.multiplelabels",
                        desc="Multiple ROIs, default to 1 for .nii or .img "
                        "ROI files if associated .txt or .csv or .xls "
                        "files exist"))
        self.add_trait("rois_regresscovariates", List(Int(),
                        optional=False,
                        output=False,
                        field="rois.regresscovariates",
                        desc="Regress out covariates, default to 1 for more "
                        "than one dimension extracted"))

        # Conditions
        self.add_trait("conditions_names", List(Str(),
                        optional=False,
                        output=False,
                        field="conditions.names",
                        desc="Conditon names"))
        self.add_trait("conditions_onsets", List(List(List(Float())),
                        optional=False,
                        output=False,
                        field="conditions.onsets",
                        desc="Conditon onsets"))
        self.add_trait("conditions_durations", List(List(List(Float())),
                        optional=False,
                        output=False,
                        field="conditions.durations",
                        desc="Conditon durations"))

        # Covariates
        self.add_trait("covariates_names", List(Str(),
                        optional=True,
                        output=False,
                        field="covariates.names",
                        desc="covariates names"))
        self.add_trait("covariates_files", List(List(List(File())),
                        optional=True,
                        output=False,
                        field="covariates.files",
                        desc="covariates files"))

        # Output
        self.add_trait("nconditions", Int(
                        optional=False,
                        output=False,
                        desc="number of conditons"))
        self.add_trait("setup_dict", Dict(
                        optional=False,
                        output=True,
                        desc="dictionary with all conn setup parameters"))

    def _anatomicals_changed(self, old_trait_value, new_trait_value):
        """ Event to setup the the number of subject
        """
        self.nsubjects = len(new_trait_value)

    def _conditions_names_changed(self, old_trait_value, new_trait_value):
        """ Event to setup the the number of conditions
        """
        self.nconditions = len(new_trait_value)

    def _functional_paths_changed(self, old_trait_value, new_trait_value):
        """ Event to define the functionals and covariates paths
        """
        if not isinstance(self.sp_functional_prefixes, _Undefined):
            self.functionals = join_functionals(new_trait_value,
                                        self.sp_functional_prefixes)
            self.functionals_from_spreproc.optional = True

        if not isinstance(self.covariates_prefixes, _Undefined):
            self.covariates_files = join_covariates(
            new_trait_value, self.covariates_prefixes)

    def _functionals_from_spreproc_changed(self, old_trait_value,
                                           new_trait_value):
        """ Event to alow functional prefixes to be optional and define
        functionals
        """
        if isinstance(self.sp_functional_prefixes, _Undefined):
            self.sp_functional_prefixes.optional = True
            self.functionals = new_trait_value

    def _sp_functional_prefixes_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.functional_paths, _Undefined):
            self.functionals = join_functionals(self.functional_paths,
                                                new_trait_value)
            self.functionals_from_spreproc.optional = True

    def _covariates_prefixes_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.functional_paths, _Undefined):
            self.covariates_files = join_covariates(self.functional_paths,
                                                new_trait_value)
            
    def _anatomical_paths_changed(self, old_trait_value, new_trait_value):
        """ Event to define the anatomicals and the masks paths
        """
        # Anatomicals
        if not isinstance(self.sp_anatomical_prefix, _Undefined):
            self.anatomicals = join_anatomicals(new_trait_value,
                                        self.sp_anatomical_prefix)
            self.anatomicals_from_spreproc.optional = True

        # Masks
        if not isinstance(self.Grey_masks_prefix, _Undefined):
            self.masks_Grey_files = join_anatomicals(
            new_trait_value, self.Grey_masks_prefix)

        if not isinstance(self.White_masks_prefix, _Undefined):
            self.masks_White_files = join_anatomicals(
            self.anatomical_paths, self.White_masks_prefix)

        if not isinstance(self.CSF_masks_prefix, _Undefined):
            self.masks_CSF_files = join_anatomicals(
            self.anatomical_paths, self.CSF_masks_prefix)


    def _anatomicals_from_spreproc_changed(self, old_trait_value,
                                           new_trait_value):
        """ Event to alow functional prefixes to be optional and define
        functionals
        """
        if isinstance(self.sp_anatomical_prefix, _Undefined):
            self.sp_anatomical_prefix.optional = True
            self.anatomicals = new_trait_value

    def _sp_anatomical_prefix_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.anatomical_paths, _Undefined):
            self.anatomicals = join_anatomicals(self.anatomical_paths,
                                                new_trait_value)
            self.functionals_from_spreproc.optional = True

    def _Grey_masks_prefix_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.anatomical_paths, _Undefined):
            self.masks_Grey_files = join_anatomicals(
            self.anatomical_paths, new_trait_value)

    def _White_masks_prefix_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.anatomical_paths, _Undefined):
            self.masks_White_files = join_anatomicals(
            self.anatomical_paths, new_trait_value)

    def _CSF_masks_prefix_changed(self, old_trait_value,
                                           new_trait_value):
        if not isinstance(self.anatomical_paths, _Undefined):
            self.masks_CSF_files = join_anatomicals(
            self.anatomical_paths, new_trait_value)

    def _run_process(self):
        """ Method to acess the Matlab script of the CONN module.
        """
        # Force some default parameters to be added in the batch
        if isinstance(self.isnew, _Undefined):
            self.isnew = 1

        if isinstance(self.done, _Undefined):
            self.done = 1

        return self.run()


if __name__ == '__main__':

    from spatial_preproc import SpatialPreproc
    from manager import InputDataManager

    manager = InputDataManager()
    manager.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    manager.functional_dir_name = "func"
    manager.anatomical_dir_name = "anat"
    manager()

    spreproc = SpatialPreproc()
    spreproc.output_directory = "/volatile/new/salma/test_NSAP_NYU_NOspreproc"
    spreproc.matlab_paths = ["/i2bm/local/spm8-5236",
                             "/volatile/new/salma/conn"]

#    spreproc.functionals = manager.raw_functional_images
#    spreproc.anatomicals = manager.raw_anatomical_images
    spreproc.execute_mfile = False

    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.matlab_cmd = "/neurospin/local/bin/matlab"
    setup.matlab_paths = spreproc.matlab_paths
    setup.output_directory = spreproc.output_directory
    setup.sp_functional_prefixes = ["swralfo*.nii"]
    setup.sp_anatomical_prefix = "wmmprage_a*.nii"
    setup.Grey_masks_prefix = "mwc1mprage_a*.nii"
    setup.White_masks_prefix = "mwc2mprage_a*.nii"
    setup.CSF_masks_prefix = "mwc3mprage_a*.nii"
    setup.functional_paths = manager.functional_paths
    setup.anatomical_paths = manager.anatomical_paths
    setup.covariates_names = ["Realignment"]
    setup.covariates_prefixes = [["rp_alfo*.txt"]] # 1 covariate, 2 sessions
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.execute_mfile = True
    runtime = setup._run_process()
    print runtime[0]
    print runtime[1]
    print runtime[2]
    print setup.mlabcmdline