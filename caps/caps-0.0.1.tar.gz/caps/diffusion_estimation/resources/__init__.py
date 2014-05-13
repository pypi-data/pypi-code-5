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


def get_sphere(name="symmetric321"):
    """ Function that return the path of resources for tensor estimation
    """
    if name == "symmetric321":
        return os.path.join(os.path.dirname(__file__), "gradient.txt")
    else:
        raise Exception("Uknown resource {0}".format(name))