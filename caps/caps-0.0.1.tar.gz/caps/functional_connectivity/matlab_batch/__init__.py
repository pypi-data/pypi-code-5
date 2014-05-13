#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Get the CONN matlab batches.
"""

import os

THIS_DIR = os.path.dirname(__file__)

CONN_BATCHES = {
    'individual_connectivity': os.path.join(THIS_DIR, "myConn_analysis.m"),
    'temporal_preproc': os.path.join(THIS_DIR, "myConn_preproc.m"),
    'group_connectivity': os.path.join(THIS_DIR, "myConn_results.m"),
}


def get_batch(name):
    """ Get he CONN matlab batches

    Parameters
    ----------
    name : str
        which conn batch - one of :

        ``individual_connectivity`` - Firl level connectivity analysis,
        ``temporal_preproc`` - Temporal fMRI preprocessings,
        ``group_connectivity`` - Second level connectivity analysis,

    Returns
    -------
    batch : str
        the path to the desired CONN batch.
    """
    batch = CONN_BATCHES.get(name)

    if batch is None:
        raise Exception('No batch found for option {0}: {1}'.format(name,
                         batch))
    return batch


if __name__ == "__main__":
    print get_batch(name='individual_connectivity')

