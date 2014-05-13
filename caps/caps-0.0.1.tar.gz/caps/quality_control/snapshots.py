#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2014
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import numpy
import os
import tempfile
import shutil
import nibabel
import sys

# Capsul import
from capsul.pipeline import Pipeline
from capsul.process import Process
from capsul.process import get_process_instance
from capsul.apps_qt.qt_backend import QtGui

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import File, Float, Int, Directory, String
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import File, Float, Int, Directory, String


##############################################################
#                   Process definition 
##############################################################

class MultiSnapshot(Process):
    """
    Slice a Volume

    Generate an image with merge sagittal, axial, and coronal slices.
    """

    def __init__(self):
        # Inheritance
        super(MultiSnapshot, self).__init__()

         # Inputs
        self.add_trait("in_file", File(
           _Undefined(),
           optional=False,
           output=False,
           exists=True,
           desc="volume to treat"))
        self.add_trait("lower_bound", Float(
            _Undefined(),
            optional=False,
            output=False,
            desc="the lower bound slice fraction"))
        self.add_trait("upper_bound", Float(
            _Undefined(),
            optional=False,
            output=False,
            desc="the upper bound slice fraction"))
        self.add_trait("nb_steps", Int(
            _Undefined(),
            optional=False,
            output=False,
            desc="desired number of snapshots"))
        self.add_trait("output_dir", Directory(
            os.getcwd(),
            optional=True,
            output=False,
            exists=True,
            desc="output directory"))
        self.add_trait("target", File(
            _Undefined(),
            optional=True,
            output=False,
            exists=True,
            desc="the location of the target image to display edge overlay."))

        # Outputs
        self.add_trait("image_out", String(exists=True,
            output=True,
            desc="path of the png resulting image"))

    def _run_process(self):

        # generate slice cut options
        options = []
        line_cuts = ['%.2f' % j for j in
                     numpy.linspace(self.lower_bound,
                                    self.upper_bound,
                                    self.nb_steps)]
        for plane in ["x", "y", "z"]:
            plane_options = [(plane, i) for i in line_cuts]
            options.extend(plane_options)

        # Create rigid registration object
        slicer_instance = get_process_instance("caps.quality_control."
                                               "fsl_interface.Slicer")
        append_instance = get_process_instance("caps.quality_control."
                                               "fsl_interface.PngAppend")

        # generate temp folder
        tmp = "/volatile/nsap/caps/snap"#tempfile.mkdtemp()
        # get volume shape
        nii = nibabel.load(self.in_file)
        shape = nii.shape

        # instance parameters
        slicer_instance.set_output_directory(tmp)
        append_instance.set_output_directory(tmp)
        slicer_instance.label_slices = True
        if self.target:
            slicer_instance.image_edges = self.target
        slicer_instance.in_file = self.in_file
        slices = []

        # hacks
        slicer_instance.single_slice = "y"
        append_instance.merge = "merge_vertically"
        
        for option in options:
            # fraction to index
            if option[0] == "x":
                slice_index = int(float(option[1]) * shape[0])
            if option[0] == "y":
                slice_index = int(float(option[1]) * shape[1])
            if option[0] == "z":
                slice_index = int(float(option[1]) * shape[2])

            # generate output file name
            suffix = "fsl-slicer{0}-{1}.png".format(*option)
            cslice = os.path.join(tmp, suffix)
            # open(cslice, 'a').close()

            slicer_instance.single_slice = option[0]
            slicer_instance.slice_number = slice_index
            slicer_instance.out_file = cslice
            print "-*", slicer_instance._nipype_interface.inputs.out_file
            
            # print cslice
            slicer_instance._run_process()
            slices.append(cslice)

        # generate one .png file per cut plane
        plane_png = []

        for plane in ["x", "y", "z"]:
            # generate output file name
            row_slice = os.path.join(tmp,
                                     "fsl-pngappend-row-{0}.png".format(plane))

            # sort slices and merge
            plane_slices = [slice for slice in slices if plane in slice]
            # instance parameters
            append_instance.merge = "merge_horizontally"
            append_instance.in_file = plane_slices
            append_instance.out_file = row_slice

            append_instance._run_process()

            # slices.append(row_slice)
            plane_png.append(row_slice)

        # concatenate row .png files
        snap = os.path.join(tmp, "fsl-pngappend.png")

        append_instance.merge = "merge_vertically"
        append_instance.in_file = plane_png
        append_instance.out_file = snap

        append_instance._run_process()


##############################################################
#              Vizualisation Process Definition
##############################################################

class SnapView(Process):
    """ Generate a widget with mid sagittal, axial, and coronal
    slices.
    """
    def __init__(self):
        """ SnapView class inititialization
        """
        # Inheritance
        super(SnapView, self).__init__()
        
        # Inputs
        self.add_trait("edges_image", File(
            _Undefined(),
            optional=True,
            exists=True,
            output=False,
            desc="An image with edges superposed to the input image"))
        self.add_trait("input_image", File(
            _Undefined(),
            optional=False,
            exists=True,
            output=False,
            desc="An image to snap"))
     
    def _run_process(self):
        """ SnapView execution code
        """
        # Create a FSL slicer object
        slicer = get_process_instance(
            "caps.quality_control.fsl_interface.Slicer")

        # Create a tmp directory to store the result
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
            
        # Setup slicer
        slicer.set_output_directory(os.path.dirname(tmp_file.name))
        slicer.label_slices = True
        slicer.middle_slices = True
        slicer.out_file = tmp_file.name
        slicer.image_edges = self.edges_image
        slicer.in_file = self.input_image
        
        # Execute process
        slicer._run_process()
        
        # Create the widget and application
        app = QtGui.QApplication(sys.argv)
        view = ImageViewer(tmp_file.name)
        view.show()
        
        # Start loop
        sys.exit(app.exec_())


class ImageViewer(QtGui.QWidget):
    """ Create a viewer for 2D image
    """
    def __init__(self, image_path):
        """ Initialize ImageViewer class
        
        Parameters
        ----------
        image_path: str
            the path to the image we want to display
        """
        # Inheritance
        super(ImageViewer, self).__init__()
        
        # Create viewer
        layout = QtGui.QVBoxLayout( self )
        self.label =QtGui.QLabel()
        layout.addWidget(self.label)
        
        # Load ans set image
        pixmap = QtGui.QPixmap(image_path) #  .scaledToHeight( 600 )
        self.label.setPixmap(pixmap)


##############################################################
#                   Pipeline definition 
##############################################################

class Snap(Pipeline):
    """
    Slice a Volume

    Generate an image with merge sagittal, axial, and coronal slices.
    """
    def pipeline_definition(self):

        # Create Processes
        self.add_process("slicer_multi",
                         "caps.quality_control.snapshots.MultiSnapshot")

        self.add_process("slicer", "nipype.interfaces.fsl.utils.Slicer",
                         make_optional=["terminal_output"])
        # Create Switch
        self.add_switch("select_qc", ["MULTI", "SCA"], "out_file")

        # FSL Slicer algorithm parameters
        self.nodes["slicer"].process.label_slices = True
        self.nodes["slicer"].process.middle_slices = True

        # Link Switch
        self.add_link("slicer._out_file->"
                      "select_qc.SCA_switch_out_file")
        self.add_link("slicer_multi.image_out->"
                      "select_qc.MULTI_switch_out_file")

        # Export Inputs
        self.export_parameter("slicer", "image_edges",
                              pipeline_parameter="edges_image")
        self.export_parameter("slicer", "in_file",
                              pipeline_parameter="input_image")
        self.add_link("input_image->slicer_multi.in_file")
        self.add_link("edges_image->slicer_multi.target")
        self.export_parameter("slicer_multi", "lower_bound")
        self.export_parameter("slicer_multi", "upper_bound")
        self.export_parameter("slicer_multi", "nb_steps")

        # Export Outputs
        self.export_parameter("select_qc", "out_file",
                              pipeline_parameter="image_out")


##############################################################
#                            Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/caps"):
    """
    ============================
    FSL diffusion preprocessings
    ============================

    .. topic:: Objective

        We propose to make a quality control of a diffusion sequence:
        Simple snapshot (SCA)
        Multi snapshot, more complete (MULTI)

    Import
    ------

    First we load the function that enables us to access the toy datasets
    """
    from caps.toy_datasets import get_sample_data

    """
    From capsul we then load the class to configure the study we want to
    perform
    """
    from capsul.study_config import StudyConfig

    """
    Here two utility tools are loaded. The first one enables the creation
    of ordered dictionary and the second ensure that a directory exist.
    Note that the directory will be created if necessary.
    """
    from capsul.utils.sorted_dictionary import SortedDictionary
    from caps.dicom_converter.base.tools import ensure_is_dir

    """
    Load the toy dataset
    --------------------

    We want to perform Snap on a diffusion sequence.
    To do so, we use the *get_sample_data* function to load this
    dataset.

    .. seealso::

        For a complete description of the *get_sample_data* function, see the
        :ref:`Toy Datasets documentation <toy_datasets_guide>`
    """
    toy_dataset = get_sample_data("mni_2mm")

    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(toy_dataset.mni, toy_dataset.mask)

    """
    Will return:

    .. code-block:: python

        /home/.../git/nsap-src/nsap/data/DTI30s010.nii
        /home/.../git/nsap-src/nsap/data/DTI30s010.bval
        /home/.../git/nsap-src/nsap/data/DTI30s010.bvec

    We can see that the image has been found in a local directory

    Processing definition
    ---------------------

    Now we need to define the processing step that will perform the diffusion
    preprocessings.
    """
    snap_pipeline = Snap()

    """
    It is possible to access the pipeline input specification.
    """
    print(snap_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        switch_mode: ['Enum']
        lower_bound: ['Float']
        upper_bound: ['Float']
        nb_steps: ['Int']
        output_dir: ['Directory']
        target: ['File']
        edges_image: ['File']
        input_image: ['File']


    We activate the multi snap path
    """
    snap_pipeline.switch_QC = "MULTI"

    """

    We can now tune the pipeline parameters.
    We first set the input dwi file:
    """

    snap_pipeline.input_image = toy_dataset.mni
    snap_pipeline.lower_bound = 0.15
    snap_pipeline.upper_bound = 0.85
    snap_pipeline.nb_steps = 6
    snap_pipeline.edges_image = toy_dataset.mask
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`
    """
    snap_working_dir = os.path.join(working_dir, "snap")
    ensure_is_dir(snap_working_dir)
    default_config = SortedDictionary(
        ("output_directory", snap_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(snap_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                        snap_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

    """
    .. note::
        Since only the motion and eddy corrections has been selected,
        the *unwrapped_phase_file* and *susceptibility_corrected_file*
        are not specified.
        Thus the *corrected_file* output contains the motion-eddy corrected
        image.
    """

if __name__ == '__main__':
    pilot()
