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


class TemporalPreproc(ConnProcess):
    """ Temporal fMRI preproc with CONN
    """
    jobname = "Preprocessing"

    def __init__(self):
        super(TemporalPreproc, self).__init__()

        self.add_trait("done", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="done",
            desc=("1/0, [0]. 0: only edits project fields (do not run "
                  "Preproc->'Done'); 1: run Preproc->'Done'")))
        self.add_trait("overwrite", Enum(
            ["Yes", "No"],
            optional=True,
            output=False,
            field="overwrite",
            desc="overwrite existing results if they exist ['Yes']"))
        self.add_trait("filter", List(
            Float(),
            optional=True,
            output=False,
            field="filter",
            desc=("frequency filter (band-pass values, in Hz) [0.008,0.09]")))
        self.add_trait("detrending", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="detrending",
            desc=("1/0: BOLD times-series detrending [1] ")))
        self.add_trait("despiking", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="despiking",
            desc=("1/0: temporal despiking with a hyperbolic tangent "
                  "squashing function [1] ")))
        self.add_trait("confounds_names", List(
            Str(),
            optional=True,
            output=False,
            field="confounds names",
            desc=("confounds names can be: 'Grey Matter', 'White Matter', "
                  "'CSF',any ROI name, any covariate name, or 'Effect of \*' "
                  "where \* represents any condition name. Default to 'White "
                  "Matter','CSF' and all covariates names")))
        self.add_trait("confounds_dimensions", List(
            Int(),
            optional=True,
            output=False,
            field="confounds dimensions",
            desc=(" number of confound dimensions [defaults to using all "
                  "dimensions available for each confound variable]")))
        self.add_trait("confounds_deriv", List(
            Int(),
            optional=True,
            output=False,
            field="confounds derivatives",
            desc=("number of derivatives for each dimension [0]")))

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
    setup.matlab_paths = [
        "/i2bm/local/spm8-5236/volatile/new/salma/conn"]
    setup.matlab_cmd = "/neurospin/local/bin/matlab"
    setup.output_directory = "/volatile/new/salma/test_NSAP_NYU_NOspreproc"
    setup.sp_functional_prefixes = ["swralfo*.nii"]
    setup.sp_anatomical_prefix = "wmmprage_a*.nii"
    setup.Grey_masks_prefix = "mwc1mprage_a*.nii"
    setup.White_masks_prefix = "mwc2mprage_a*.nii"
    setup.CSF_masks_prefix = "mwc3mprage_a*.nii"
    setup.functional_paths = manager.functional_paths
    setup.anatomical_paths = manager.anatomical_paths
    setup.covariates_names = ["Realignment"]
    setup.covariates_prefixes = [["rp_alfo*.txt"]]
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "Yes"
    setup.isnew = 1
    setup.execute_mfile = False

    # Temporal preproc step
    tpreproc = TemporalPreproc()
    tpreproc.output_directory = setup.output_directory
    tpreproc.matlab_paths = setup.matlab_paths
    tpreproc.matlab_cmd = setup.matlab_cmd
    tpreproc.batch_header = setup.batch
    tpreproc.execute_mfile = True
    tpreproc.done = 1
    runtime = tpreproc._run_process()
    print runtime[0]
    print runtime[1]
    print runtime[2]
    print tpreproc.mlabcmdline

