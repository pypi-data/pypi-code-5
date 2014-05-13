#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, List, Directory, Str, Int, Enum, Float,
                            Dict, Any)
except ImportError:
    from enthought.traits.api import (File, List, Directory, Str, Int, Enum,
                                      Float, Dict, Any)

# Caps import
from matlab_utils import ConnProcess


class Results(ConnProcess):
    """ Second-lvel analyses with CONN
    """
    jobname = "Results"

    def __init__(self):
        super(Results, self).__init__()

        self.add_trait("done", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="done",
            desc=("1/0, [0]. 0: only edits Results fields (do not run "
                  "Results->'Done'); 1: run Results->'Done'")))
        self.add_trait("overwrite", Enum(
            ["Yes", "No"],
            optional=True,
            output=False,
            field="overwrite",
            desc="overwrite existing results if they exist ['Yes']"))

        # PERFORMS FIRST-LEVEL ANALYSES (ROI-to-ROI and seed-to-voxel)
        self.add_trait("analysis_number", List(Int(),
            optional=True,
            output=False,
            field="analysis_number",
            desc=("sequential indexes identifying each set of independent "
                  "analyses (set this variable to 0 to identify "
                  "voxel-to-voxel analyses) [1] ")))
        self.add_trait("foldername", Directory(
            optional=True,
            output=False,
            field="foldername",
            desc=("folder to store the results ")))
        self.add_trait("between_subjects_effect_names", List(Str(),
            optional=True,
            output=False,
            field="between_subjects.effect_names",
            desc=("second-level effect names ")))
        self.add_trait("between_subjects_contrast", List(Float(),
            optional=True,
            output=False,
            field="between_subjects.contrast",
            desc=("between_subjects contrast vector (same size as "
                  "between_subjects_effect_names) ")))
        self.add_trait("between_conditions_effect_names", List(Str(),
            optional=True,
            output=False,
            field="between_conditions.effect_names",
            desc=("condition names (as in Setup.conditions.names) [defaults "
                  "to multiple analyses, one per condition]. ")))
        self.add_trait("between_conditions_contrast", List(Float(),
            optional=True,
            output=False,
            field="between_conditions.contrast",
            desc=("between_conditions contrast vector (same size as "
                  "between_conditions_effect_names) ")))
        self.add_trait("between_sources_effect_names", List(Str(),
            optional=True,
            output=False,
            field="between_sources.effect_names",
            desc=("sources names. (as in Analysis.regressors, typically "
                  "appended with _1_1; generally they are appended with "
                  "_N_M -where N is an index ranging from 1 to 1+derivative "
                  "order, and M is an index ranging from 1 to the number of "
                  "dimensions specified for each ROI; for example "
                  "ROINAME_2_3 corresponds to the first derivative of the "
                  "third PCA component extracted from the roi ROINAME) "
                  "[defaults to multiple analyses, one per source]. ")))
        self.add_trait("between_sources_contrast", List(Float(),
            optional=True,
            output=False,
            field="between_sources.contrast",
            desc=("between_sources contrast vector (same size as "
                  "between_sources_effect_names) ")))

    def _run_process(self):
        """ Method to acess the Matlab script of the CONN module.
        """
        # Force some default parameters to be added in the batch
        if isinstance(self.done, _Undefined):
            self.done = 0

        return self.run()


if __name__ == '__main__':

    from manager import InputDataManager
    from spatial_preproc import SpatialPreproc
    from setup import Setup
    from temporal_preproc import TemporalPreproc
    from analysis import Analysis
    import numpy

    manager = InputDataManager()
    manager.data_path = "/volatile/new/salma/NYU_TRT_session1a/"
    manager.functional_dir_name = "func"
    manager.anatomical_dir_name = "anat"
    manager()

    spreproc = SpatialPreproc()
    spreproc.execute_mfile = False

    # Setup step
    setup = Setup()
    setup.batch_header = spreproc.batch
    setup.matlab_paths = ["/i2bm/local/spm8-5236",
                            "/volatile/new/salma/conn"]
    setup.output_directory = "/volatile/new/salma/test_NSAP_NYU_NOspreproc"
    setup.functional_paths = manager.functional_paths
    setup.anatomical_paths = manager.anatomical_paths
    setup.sp_functional_prefixes = ["swralfo*.nii"]
    setup.sp_anatomical_prefix = "wmmprage_a*.nii"
    setup.Grey_masks_prefix = "mwc1mprage_a*.nii"
    setup.White_masks_prefix = "mwc2mprage_a*.nii"
    setup.CSF_masks_prefix = "mwc3mprage_a*.nii"
    setup.covariates_names = ["Realignment"]
    setup.covariates_prefixes = [["rp_alfo*.txt"]]
    setup.conditions_names = ["Condition1"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "Yes"
    setup.done = 1
    setup.isnew = 1
    setup.execute_mfile = False

    # Temporal preproc step
    tpreproc = TemporalPreproc()
    tpreproc.batch_header = setup.batch
    tpreproc.execute_mfile = False
    tpreproc.overwrite = "Yes"
    tpreproc.done = 1

    # Analysis
    analysis = Analysis()
    analysis.batch_header = tpreproc.batch
    analysis.execute_mfile = False
    analysis.overwrite = "Yes"
    analysis.done = 1

    # Results
    results = Results()
    results.matlab_paths = setup.matlab_paths
    results.batch_header = analysis.batch
    results.output_directory = setup.output_directory
    results.execute_mfile = True
    results.done = 1
    runtime = results._run_process()
    print runtime[0]
    print runtime[1]
    print runtime[2]
    print results.mlabcmdline