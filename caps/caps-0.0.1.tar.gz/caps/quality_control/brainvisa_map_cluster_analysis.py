#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2014
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import shutil
import os
import sys
import logging
import glob
import subprocess
import numpy as np

# Misc import
from caps.toy_datasets import get_sample_data

# Capsul import
from capsul.pipeline import Pipeline
from capsul.process import Process

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (File, Float, Int, Tuple, String, Any, Directory,
                            Bool)
except ImportError:
    from enthought.traits.trait_base import _Undefined
    from enthought.traits.api import (File, Float, Int, Tuple, String, Any,
                                      Bool, Directory)

# Qt import
try:
    from PyQt4 import QtGui
except:
    logging.error("Qt not installed: the mdodule may not work properly, "
                  "please investigate")

# Soma import
try:
    from soma import aims
except Exception, e:
    logging.error("Soma not installed")

# Anatomist import
try:
    # needed here in oder to be compliant with AIMS
    import anatomist.api as anatomist
except:
    logging.error("Anatomist no installed: the mdodule may not work properly, "
                  "please investigate")


##############################################################
#              Vizualisation Process Definition
##############################################################

class MeshClusterRendering(Process):
    """ Vizualization of signed stattistic map or weigths.
    """

    def __init__(self):
        # Inheritance
        super(MeshClusterRendering, self).__init__()

        # Inputs
        self.add_trait("mesh_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="mesh file of interest"))
        self.add_trait("texture_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="an image from which to extract texture (for the mesh file)"))
        self.add_trait("white_mesh_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="a mesh file of the underlying neuroanatomy"))
        self.add_trait("anat_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="an image of the underlying neuroanatomy"))

    def _run_process(self):
        # create application
        app = QtGui.QApplication(sys.argv)

        # instance of anatomist
        a = anatomist.Anatomist()

        # load objects
        a_mesh = a.loadObject(self.mesh_file)
        a_wm_mesh = a.loadObject(self.white_mesh_file)
        a_texture = a.loadObject(self.texture_file)
        a_anat = a.loadObject(self.anat_file)

        # mesh option
        material = a.Material(diffuse=[0.8, 0.8, 0.8, 0.7])
        a_wm_mesh.setMaterial(material)

        # change palette
        palette_file = get_sample_data("brainvisa_palette").edouard
        bv_rgb_dir = os.path.join(os.environ["HOME"], ".anatomist", "rgb")
        if not os.path.isdir(bv_rgb_dir):
            os.makedirs(bv_rgb_dir)
        bv_rgb_file = os.path.join(bv_rgb_dir,
                                   os.path.basename(palette_file))
        if not os.path.isfile(bv_rgb_file):
            shutil.copyfile(palette_file, bv_rgb_file)
        palette = a.getPalette("palette_signed_values_blackcenter")
        a_texture.setPalette(palette, minVal=-10, maxVal=10,
                             absoluteMode=True)

        # view object
        block = a.createWindowsBlock(1)
        w1 = a.createWindow("3D", block=block)
        w2 = a.createWindow("3D", block=block)

        # fusion 3D
        fusion3d = a.fusionObjects([a_mesh, a_texture], "Fusion3DMethod")
        w1.addObjects([fusion3d, a_wm_mesh])
        a.execute("Fusion3DParams", object=fusion3d, step=0.1, depth=5.,
                  sumbethod="max", method="line_internal")

        # fusion 2D
        fusion2d = a.fusionObjects([a_anat, a_texture], "Fusion2DMethod")
        a.execute("Fusion2DMethod", object=fusion2d)

        # change 2D fusion settings
        a.execute("TexturingParams", texture_index=1, objects=[fusion2d, ],
                  mode="linear_A_if_B_black", rate=0.1)

        # fusion cut mesh
        fusionmesh = a.fusionObjects([a_wm_mesh, fusion2d],
                                     "FusionCutMeshMethod")
        fusionmesh.addInWindows(w2)
        a.execute("FusionCutMeshMethod", object=fusionmesh)

        # start loop
        sys.exit(app.exec_())


##############################################################
#              Processing Process Definition
##############################################################

class MapToMesh(Process):

    def __init__(self):
        # Inheritance
        super(MapToMesh, self).__init__()

        # Inputs
        self.add_trait("wmap_file", File(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="Input map volume"))
        self.add_trait("thresh_size", Int(
            _Undefined(),
            optional=False,
            output=False,
            exists=True,
            desc="Threshold, in voxels nb, between small and big clusters"))
        self.add_trait("thresh_neg_bound", Any(
            optional=False,
            output=False,
            exists=True,
            desc="Negative bound threshold (lower, upper)"))
        self.add_trait("thresh_pos_bound", Any(
            optional=False,
            output=False,
            exists=True,
            desc="Positivee bound threshold (lower, upper)"))
        self.add_trait("output_directory", Directory(
            os.getcwd(),
            exist=True,
            output=False,
            desc="output directory"))

        # Outputs
        self.add_trait("cluster_mask_file", File(
            _Undefined(),
            output=True,
            desc="Cluster mask file"))
        self.add_trait("mesh_file", File(
            _Undefined(),
            output=True,
            desc="Mesh file"))
        self.add_trait("connected_components", File(
            _Undefined(),
            output=True,
            desc="Connected components"))
        self.add_trait("cluster_file", File(
            _Undefined(),
            output=True,
            desc="Cluster file"))

    def _run_process(self):
        # get connected components
        # Get binary mask
        vol = aims.read(self.wmap_file)
        data = np.asarray(vol)
        thresh_neg_low, thresh_neg_high = self.thresh_neg_bound
        thresh_pos_low, thresh_pos_high = self.thresh_pos_bound
        data[(data < thresh_neg_low) | (data > thresh_pos_high) |
             (data > thresh_neg_high) & (data < thresh_pos_low)] = 0
        data[np.where(data != 0)] = 1

        self.cluster_mask_file = os.path.join(self.output_directory,
                                              "clusters_mask.nii.gz")
        aims.write(vol, self.cluster_mask_file)

        self.connected_components = os.path.join(
            self.output_directory, "connected_components.nii.gz")
        cmd = ["AimsConnectComp", "-i", self.cluster_mask_file, "-o",
               self.connected_components, "-c", "26", "-t", "S16",
               "-s", str(self.thresh_size)]
        subprocess.call(cmd)

        # apply mask to map
        self.cluster_file = os.path.join(
            self.output_directory, "clusters.nii.gz")
        cmd = ["AimsMask", "-i", self.wmap_file, "-o",
               self.cluster_file, "-m", self.connected_components]
        subprocess.call(cmd)

        # mesh connected components
        """ Mesh connected components.
        """
        self.mesh_prefix = os.path.join(self.output_directory, "clusters")
        self.mesh_file = self.mesh_prefix + ".mesh"
        cmd = ["AimsMesh", "-i", self.connected_components, "-o",
               self.mesh_file, "--smooth", "True", "--smoothIt", "30"]
        subprocess.call(cmd)

        self.mesh_file = os.path.join(self.output_directory, "clusters.mesh")
        tmp_mesh = glob.glob(self.mesh_prefix + "_*.mesh")
        tmp_minf = glob.glob(self.mesh_prefix + "*.minf")
        cmd = ["AimsZCat", "-i"]
        cmd.extend(tmp_mesh)
        cmd.extend(["-o", self.mesh_file])
        subprocess.call(cmd)

        for fname in tmp_mesh:
            os.remove(fname)
        for fname in tmp_minf:
            os.remove(fname)


##############################################################
#                       Pipeline definition
##############################################################

class MapClusterAnalysis(Pipeline):
    """ Visulaize a weight map

    Steps are:
    * Extract and Mesh Clusters in a standard space
    * Register the reference to the target image
    and aplly the affine transformation to the map image.
    * Vizualization of signed stattistic map or weigths
    """
    def pipeline_definition(self):

        # Create Processes
        self.add_process("map_to_mesh", "caps.quality_control."
                         "brainvisa_map_cluster_analysis.MapToMesh")
        self.add_process("fsl_affine", "nipype.interfaces.fsl.FLIRT",
                         make_optional=["terminal_output"])
        self.add_process("fsl_affine_app", "caps.utils.misc.ApplyXfm")
        self.add_process("mesh_cluster_rendering", "caps.quality_control."
                         "brainvisa_map_cluster_analysis.MeshClusterRendering")

        # Change node type
        self.nodes["mesh_cluster_rendering"].node_type = "view_node"

        # Export Inputs
        self.export_parameter("map_to_mesh", "thresh_size")
        self.export_parameter("map_to_mesh", "thresh_neg_bound")
        self.export_parameter("map_to_mesh", "thresh_pos_bound")
        self.export_parameter("fsl_affine", "in_file",
                              pipeline_parameter="moving_image")
        self.export_parameter("fsl_affine", "reference",
                              pipeline_parameter="reference_image")
        self.export_parameter("fsl_affine_app", "moving_image",
                              pipeline_parameter="map_image")
        self.export_parameter("mesh_cluster_rendering", "white_mesh_file")

        # Link input
        self.add_link("reference_image->fsl_affine_app.reference_image")
        self.add_link("reference_image->mesh_cluster_rendering.anat_file")

        # Link ApplyXfm
        self.add_link("fsl_affine._out_matrix_file->"
                      "fsl_affine_app.in_matrix_file")
        self.add_link("fsl_affine_app.register_image->"
                      "map_to_mesh.wmap_file")

        # Link MeshClusterRendering
        self.add_link("map_to_mesh.mesh_file->"
                      "mesh_cluster_rendering.mesh_file")
        self.add_link("map_to_mesh.cluster_file->"
                      "mesh_cluster_rendering.texture_file")

        # FSL Flirt algorithms parameters
        self.nodes["fsl_affine"].process.dof = 12
        self.nodes["fsl_affine"].process.cost = "normmi"

        # Export Outputs
        self.export_parameter("map_to_mesh", "cluster_mask_file")
        self.export_parameter("map_to_mesh", "mesh_file")
        self.export_parameter("map_to_mesh", "connected_components")
        self.export_parameter("map_to_mesh", "cluster_file")
        self.export_parameter("fsl_affine_app", "register_image",
                              pipeline_parameter="register_map_image")
        self.export_parameter("fsl_affine", "_out_file",
                              pipeline_parameter="register_ref_image")

        # Pipeline parameters
        # try to set the reference image (need fsl resource)
        try:
            self.reference_image = get_sample_data("mni_1mm").brain
            self.white_mesh_file = get_sample_data("mni_1mm").mesh
        except:
            logging.error("FSL resources are not available from your "
                          "computer.")

        # ToRemove
        try:
            self.map_image = get_sample_data("tpm").wm
            self.thresh_size = 10
            self.thresh_neg_bound = (-np.inf, -3)
            self.thresh_pos_bound = (0.8, np.inf)
            self.moving_image = get_sample_data("tpm").gm
        except:
            pass

        # Set node positions
        self.node_position = {
            "fsl_affine": (81.9, -398.8),
            "fsl_affine_app": (285.5, -401.5),
            "inputs": (-137.2, -141.4),
            "map_to_mesh": (325.6, -42.1),
            "mesh_cluster_rendering": (571.2, -337.6),
            "outputs": (663.6, -118.1)}


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
        Mesh Clusters in MNI space.

    Import
    ------

    First we load the function that enables us to access the toy datasets
    """
    import subprocess

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
    wmap = get_sample_data("tpm").wm
    reference = get_sample_data("tpm").gm
    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(wmap, reference)

    """
    Will return:

    .. code-block:: python

        /i2bm/local/spm8-5236/tpm/white.nii
        /i2bm/local/spm8-5236/tpm/grey.nii
        /usr/share/fsl/4.1/data/standard/MNI152_T1_1mm_brain.nii.gz

    We can see that the image has been found in a local directory

    Processing definition
    ---------------------

    Now we need to define the processing step that will perform the diffusion
    preprocessings.
    """
    map_cluster_analysis_pipeline = MapClusterAnalysis()

    """
    It is possible to access the pipeline input specification.
    """
    print(map_cluster_analysis_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

            map_image: ['String']
            thresh_size: ['Int']
            thresh_neg_bound: ['Tuple']
            thresh_pos_bound: ['Tuple']
            reference_image: ['File']
            target_image: ['File']
            anat_file: ['String']
            white_mesh_file: ['String']


    We can now tune the pipeline parameters.
    We first set the input dwi file:
    """
    map_cluster_analysis_pipeline.map_image = wmap
    map_cluster_analysis_pipeline.thresh_size = 10
    map_cluster_analysis_pipeline.thresh_neg_bound = (-np.inf, -3)
    map_cluster_analysis_pipeline.thresh_pos_bound = (0.8, np.inf)
    map_cluster_analysis_pipeline.reference_image = reference
    """
    Study Configuration
    -------------------

    The pipeline is now set up and ready to be executed.
    For a complete description of a study execution, see the
    :ref:`Study Configuration description <study_configuration_guide>`
    """
    brain_working_dir = os.path.join(working_dir, "brain")
    ensure_is_dir(brain_working_dir)
    default_config = SortedDictionary(
        ("output_directory", brain_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(map_cluster_analysis_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print "\nOUTPUTS\n"
    for trait_name, trait_value in \
                    map_cluster_analysis_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)

    """
    .. note::
        Since only the motion and eddy corrections has been selected,
        the *unwrapped_phase_file* and *susceptibility_corrected_file*
        are not specified.
        Thus the *corrected_file* output contains the motion-eddy corrected
        image.

    Vizualisation
    -------------
    """
    viewer_node = map_cluster_analysis_pipeline.nodes["mesh_cluster_rendering"]
    viewer_process = viewer_node.process
    for plug_name, plug in viewer_node.plugs.iteritems():
        if plug_name in ["nodes_activation", "selection_changed"]:
            continue
        # since it is a viewer node we normally have only inputs
        for (source_node_name, source_plug_name, source_node,
            source_plug, weak_link) in plug.links_from:

            source_plug_value = getattr(source_node.process,
                                        source_plug_name)
            source_trait = source_node.process.trait(source_plug_name)
            setattr(viewer_process, plug_name, source_plug_value)
    subprocess.Popen(viewer_process.get_commandline())


if __name__ == '__main__':
    pilot()