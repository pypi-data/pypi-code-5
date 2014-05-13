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
    from traits.api import (List, Any, Int, Either)
except ImportError:
    from enthought.traits.api import (List, Any, Int, Either)

# Capsul import
from capsul.process import Process
from capsul.pipeline import Pipeline


##############################################################
#                   Select Process Definition
##############################################################

class ApplyXfm(Pipeline):
    """ Wraps FSL command flirt
    ApplyXfm is used to apply an existing tranform to an image
    and enables the creation of a QC snap.
    """

    def pipeline_definition(self):

        # Create Processes
        self.add_process("fsl_app_transform", "nipype.interfaces.fsl.ApplyXfm",
                         make_optional=["terminal_output"])
        self.add_process("snap", "caps.quality_control.snapshots.SnapView")

        # Change node type
        self.nodes["snap"].node_type = "view_node"

        # Export Inputs
        self.export_parameter("fsl_app_transform", "in_file",
                              pipeline_parameter="moving_image")
        self.export_parameter("fsl_app_transform", "reference",
                              pipeline_parameter="reference_image")
        self.export_parameter("fsl_app_transform", "in_matrix_file")

        # Link input
        self.add_link("reference_image->snap.edges_image")

        # Link fsl_app_transform
        self.add_link("fsl_app_transform._out_file->snap.input_image")

        # Export Outputs
        self.export_parameter("fsl_app_transform", "_out_file",
                              pipeline_parameter="register_image")

        # FSL ApplyXfm algorithms parameters
        self.nodes["fsl_app_transform"].process.apply_xfm = True
       
        # Set node positions
        self.node_position = {
            "fsl_app_transform": (71.0, 65.0),
            "inputs": (-133.8, 180.2),
            "outputs": (270.8, 320.0),
            "snap": (265.8, 65.6)}


##############################################################
#                   Select Process Definition
##############################################################

class Select(Process):
    """Basic interface class to select specific elements from a list
    """

    def __init__(self):
        """ Initialize Select class
        """
        super(Select, self).__init__()

        # Inputs
        self.add_trait("inlist", List(Any(),
            optional=False,
            desc="list of values to choose from"))
        self.add_trait("index", Either(Int(), List(Int()),
            _Undefined(),
            optional=False,
            desc="indices of values to choose"))

        # Outputs
        self.add_trait("outelements", List(Any(),
            output=True,
            desc="list of selected values"))
        self.add_trait("outelement", Any(
            output=True,
            desc="selected value"))

    def _run_process(self):
        """ Select execution code
        """
        indices = self.index
        if not isinstance(indices, list):
            indices = [indices]
        out = numpy.asarray(self.inlist)[numpy.asarray(self.index)].tolist()
        if not isinstance(out, list):
            self.outelement = out
            out = [out]
        self.outelements = out
