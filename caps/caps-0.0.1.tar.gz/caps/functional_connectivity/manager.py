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

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, List, Directory, Str, Int, Enum, Float,
                            Dict, Any)
except ImportError:
    from enthought.traits.api import (File, List, Directory, Str, Int, Enum,
                                      Float, Dict, Any)

# Capsul import
from capsul.process import Process


##############################################################
#         InputDataManager process definition
##############################################################

class InputDataManager(Process):
    """ Input data manager
    """

    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("data_path", Directory(
                        _Undefined(),
                        optional=False,
                        output=False,
                        desc="the path to all subject datasets"))
        self.add_trait("subjects", List(Directory(),
                        [],
                        optional=True,
                        output=False,
                        desc="selection of specific subject directories. "
                        "If unspecified, all present subdirectories in the "
                        "data path are included"))
        self.add_trait("functional_dir_name", Str(
                        optional=False,
                        output=False,
                        desc="the functional directory name"))
        self.add_trait("anatomical_dir_name", Str(
                        optional=False,
                        output=False,
                        desc="the anatomical directory name"))

        # Outputs
        self.add_trait("functional_paths", List(Directory(),
                        optional=False,
                        output=True,
                        desc="paths to all subjects functional directories"))
        self.add_trait("anatomical_paths", List(Directory(),
                        optional=False,
                        output=True,
                        desc="paths to all subjects anatomical directories"))

    def _run_process(self):
        """ Method to execute the process.
        """
        # Define default values for some traits
        if not self.subjects:
            self.subjects = [x for x in os.listdir(self.data_path)
                               if os.path.isdir(os.path.join(
                               self.data_path, x))]

        # Paths to functional and anatomical folders
        self.functional_paths = [os.path.join(
        self.data_path, subject, self.functional_dir_name) for subject in
        self.subjects]
        self.anatomical_paths = [os.path.join(
        self.data_path, subject, self.anatomical_dir_name) for subject in
        self.subjects]