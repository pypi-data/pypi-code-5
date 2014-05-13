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


class Analysis(ConnProcess):
    """ First-level analyses with CONN
    """
    jobname = "Analysis"

    def __init__(self):
        super(Analysis, self).__init__()

        self.add_trait("done", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="done",
            desc=("1/0, [0]. 0: only edits Analysis fields (do not run "
                  "Analysis->'Done'); 1: run Analysis->'Done'")))
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
        self.add_trait("measure", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="measure",
            desc=("ROI-to-ROI and seed-to-voxel connectivity measure used, "
                  "1 = 'correlation (bivariate)', "
                  "2 = 'correlation (semipartial)', "
                  "3 = 'regression (bivariate)', "
                  "4 = 'regression (multivariate)'; [1] ")))
        self.add_trait("weight", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="weight",
            desc=("ROI-to-ROI and seed-to-voxel within-condition weight, "
                  "1 = 'none', 2 = 'hrf', 3 = 'hanning'; [2] ")))
        self.add_trait("type", Int(
            _Undefined(),
            optional=True,
            output=False,
            field="type",
            desc=("ROI-to-ROI and seed-to-voxel analysis type, "
                  "1 = 'ROI-to-ROI', 2 = 'Seed-to-Voxel', 3 = 'all'; [3] ")))
        self.add_trait("sources_names", List(Str(),
            optional=True,
            output=False,
            field="sources.names",
            desc=("ROI-to-ROI and seed-to-voxel sources names (seeds) for "
                  "connectivity analyses - "
                  "these correspond to a subset of ROI file names in "
                  "the ROI folder (if this variable does not exist the "
                  "toolbox will perform the analyses for all of the ROI "
                  "files imported in the Setup step which are not defined "
                  "as confounds in the Preprocessing step) ")))
        self.add_trait("sources_dimensions", List(Int(),
            optional=True,
            output=False,
            field="sources.dimensions",
            desc=("ROI-to-ROI and seed-to-voxel number of source "
                  "dimensions [1] ")))
        self.add_trait("sources_derivatives", List(Int(),
            optional=True,
            output=False,
            field="sources.deriv",
            desc=("number of derivatives for each dimension [0] ")))

        # PERFORMS FIRST-LEVEL ANALYSES (voxel-to-voxel)
        self.add_trait("measures_names", List(Str(),
            optional=True,
            output=False,
            field="",
            desc=("voxel-to-voxel measure names. Possible measure names are "
                  "'connectome-MVPA', "
                  "'IntegratedLocalCorrelation', 'RadialCorrelationContrast' "
                  "'IntrinsicConnectivityContrast', 'RadalSimilarityContrast'"
                  "(if this variable does not exist the toolbox will perform "
                  "the analyses for all of the default voxel-to-voxel "
                  "measures) ")))
        self.add_trait("measures_type", List(Int(),
            optional=True,
            output=False,
            field="measures.type",
            desc=("voxel-to-voxel measure type"
                  "0:local measures; 1: global measures [1] ")))
        self.add_trait("measures_kernelsupport", List(Int(),
            optional=True,
            output=False,
            field="measures.kernelsupport",
            desc=("voxel-to-voxel kernel support"
                  "local support (FWHM) of smoothing kernel [12] ")))
        self.add_trait("measures_kernelshape", List(Int(),
            optional=True,
            output=False,
            field="measures.kernelshape",
            desc=("voxel-to-voxel kernel shape "
                  "(0: gaussian; 1: gradient; 2: laplacian) [1]")))
        self.add_trait("measures_dimensions", List(Int(),
            optional=True,
            output=False,
            field="measures.dimensions",
            desc=("voxel-to-voxel number of SVD dimensions to "
                  "retain (dimensionality reduction) [16]")))
        # TODO fields dimensions_in and dimensions_out are set to default
        # values in
        # batch mode and with user choice in interface mode

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
    setup.matlab_paths = ["/i2bm/local/spm8-5236",
                        "/volatile/new/salma/conn"]
    setup.matlab_cmd = "/neurospin/local/bin/matlab"
    setup.output_directory = "/volatile/new/salma/test_NSAP_NYU_NOspreproc"
    setup.functional_paths = manager.functional_paths
    setup.anatomical_paths = manager.anatomical_paths
    setup.sp_functional_prefixes = ["swralfo*.nii"]
    setup.sp_anatomical_prefix = "wmmprage_a*.nii"
    setup.Grey_masks_prefix = "mwc1mprage_a*.nii"
    setup.White_masks_prefix = "mwc2mprage_a*.nii"
    setup.CSF_masks_prefix = "mwc3mprage_a*.nii"
    setup.covariates_names = ["Realignment"]
    setup.covariates_prefixes = [["rp_alfo*.txt", "rp_lfo*.txt"]]
    setup.conditions_names = ["Session"]
    setup.conditions_onsets = [[[numpy.nan if nsess != ncond else 0
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )] for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.conditions_durations = [[[numpy.nan if nsess != ncond else numpy.inf
    for nsess in range(setup.nconditions)] for nsub in xrange(setup.nsubjects
    )]for ncond in range(setup.nconditions)] # TODO: move it to manager?
    setup.overwrite = "No"
    setup.execute_mfile = False

    # Temporal preproc step
    tpreproc = TemporalPreproc()
    tpreproc.batch_header = setup.batch
    tpreproc.execute_mfile = False
    tpreproc.overwrite = "No"
    tpreproc.done = 1
    
    # Analysis step
    analysis = Analysis()
    analysis.output_directory = setup.output_directory
    analysis.matlab_paths = analysis.matlab_paths
    analysis.batch_header = tpreproc.batch
    analysis.matlab_cmd = setup.matlab_cmd
    analysis.execute_mfile = False
    runtime = analysis._run_process()
    print runtime[0]
    print runtime[1]
    print runtime[2]
    print analysis.mlabcmdline