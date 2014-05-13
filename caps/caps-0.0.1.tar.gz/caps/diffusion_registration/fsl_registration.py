#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Capsul import
from capsul.pipeline import Pipeline


##############################################################
#           FSL NL Registration Pipeline Definition
##############################################################

class FSLRegistration(Pipeline):
    """ FSL non linear registration to a template
    """

    def pipeline_definition(self):
        """ FSLRegistration pipeline definition
        """

        # Create Processes
        self.add_process("affine", "nipype.interfaces.fsl.FLIRT",
                         make_optional=["terminal_output"])
        self.add_process("nl", "nipype.interfaces.fsl.FNIRT",
                         make_optional=["terminal_output"])
        self.add_process("warp", "nipype.interfaces.fsl.ApplyWarp",
                         make_optional=["terminal_output"])
        self.add_process("local_affine", "caps.diffusion_registration."
                         "reorientation.LocalAffineTransformation")
        self.add_process("decomposition", "caps.diffusion_estimation."
                         "tensor_utils.DecomposeSecondOrderTensor",
                         make_optional=["mask_file"])
        self.add_process("reorientation", "caps.diffusion_registration."
                         "reorientation.SecondOrderTensorReorientation")

        # Init enum first
        self.nodes["nl"].process.config_file = "T1_2_MNI152_2mm"

        # Export Inputs
        self.export_parameter("affine", "in_file",
                              pipeline_parameter="fa_file")
        self.export_parameter("affine", "reference",
                              pipeline_parameter="target_file")
        self.export_parameter("affine", "in_weight",
                              pipeline_parameter="mask_file")
        self.export_parameter("nl", "config_file")
        self.export_parameter("warp", "in_file",
                              pipeline_parameter="tensor_file")

        # Link input
        self.add_link("fa_file->nl.in_file")
        self.add_link("target_file->nl.ref_file")
        self.add_link("target_file->warp.ref_file")

        # Link affine
        self.add_link("affine._out_matrix_file->nl.affine_file")

        # Link nl
        self.add_link("nl._field_file->warp.field_file")
        self.add_link("nl._field_file->local_affine.field_file")

        # Link warp
        self.add_link("warp._out_file->decomposition.tensor_file")

        # Link local affine
        self.add_link("local_affine.local_affine_transform_file->"
                      "reorientation.local_affine_transform_file")

        # Link decomposition
        self.add_link("decomposition.eigen_values_file->"
                      "reorientation.eigenvals_file")
        self.add_link("decomposition.eigen_vectors_file->"
                      "reorientation.eigenvecs_file")

        # Export output
        self.export_parameter("nl", "_fieldcoeff_file",
                              pipeline_parameter="fieldcoeff_file")
        self.export_parameter("nl", "_warped_file",
                              pipeline_parameter="fa_warped_file")
        self.export_parameter("nl", "_field_file",
                              pipeline_parameter="field_file")
        self.export_parameter("warp", "_out_file",
                              pipeline_parameter="tensor_warped_file")

        # FLIRT algorithm parameters
        self.nodes["affine"].process.dof = 12
        self.nodes["affine"].process.cosr = "corratio"

        # FNIRT algorithm parameters
        self.nodes["nl"].process.fieldcoeff_file = True
        self.nodes["nl"].process.field_file = True

        # LocalAffineTransformation algorithm parameters
        (self.nodes["local_affine"].process.
            local_affine_transform_name) = "local_affine_transform"

        # DecomposeSecondOrderTensor algorithm parameters
        self.nodes["decomposition"].process.eigenvecs_basename = "eigenvecs"
        self.nodes["decomposition"].process.eigenvals_basename = "eigenvals"
        self.nodes["decomposition"].process.number_of_workers = -1

        # SecondOrderTensorReorientation algorithm parameters
        self.nodes["reorientation"].process.reorientation_strategy = "ppd"
        (self.nodes["reorientation"].process.
            reoriented_tensor_name) = "reoriented_tensor"


##############################################################
#                            Pilot
##############################################################

def pilot():
    """
    ==================
    FSL FA Registation
    ==================

    .. topic:: Objective

        We propose here to register a fractional anisotropy image to a
        reference template and to apply the resulting deformation field
        to the tensor image.

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
    from nsap.lib.base import ensure_is_dir

    """
    We need some generic python modules
    """
    import os

    """
    From caps we need the pipeline that will enable use to register the
    tensor field.
    """
    from caps.diffusion_registration.fsl_registration import FSLRegistration

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`

    We first define the current working directory
    """
    working_dir = "/volatile/nsap/caps"
    registration_working_dir = os.path.join(working_dir,
                                            "diffusion_registration")
    ensure_is_dir(registration_working_dir)

    """
    And then define the study configuration.
    """
    default_config = SortedDictionary(
        ("output_directory", registration_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)

    """
    Load the toy dataset
    --------------------

    We want to perform a second order tensor fit on a diffusion sequence data.
    To do so, we use the *get_sample_data* function to load the diffusion
    dataset and the taget template.

    .. seealso::

        For a complete description of the *get_sample_data* function, see the
        :ref:`Toy Datasets documentation <toy_datasets_guide>`
    """
    diffusion_dataset = get_sample_data("dwi")
    target_dataset = get_sample_data("fa_1mm")

    """
    The *diffusion_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(diffusion_dataset.dwi, diffusion_dataset.bvals,
          diffusion_dataset.bvecs)

    """
    Will return:

    .. code-block:: python

        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

    We can see that the image has been found in a local directory

    The *target_dataset* is an Enum structure with some specific
    elements of interest *template*, *nl_config* that contain the fa
    diffusion template and the fsl fnirt configuration file.
    """
    print(target_dataset.template, target_dataset.nl_config)

    """
    Will return:

    .. code-block:: python

        /usr/share/fsl/4.1/data/standard/FMRIB58_FA_1mm.nii.gz
        /usr/share/fsl/4.1/etc/flirtsch/FA_2_FMRIB58_1mm.cnf

    We can see that the information has been found in the fsl directory.

    Processing definition
    ---------------------

    Now we need to define the processing steps that will perform the tensor
    registration.
    """
    registration_pipeline = FSLRegistration()

    """
    It is possible to access the pipeline input specification.
    """
    print(registration_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        fa_file: ['File']
        target_file: ['File']
        mask_file: ['File']
        config_file: ['Enum', 'File']

    We can now tune the pipeline parameters.
    """
    registration_pipeline.fa_file = diffusion_dataset.fa
    registration_pipeline.target_file = target_dataset.template
    registration_pipeline.mask_file = diffusion_dataset.mask
    registration_pipeline.config_file = target_dataset.nl_config
    registration_pipeline.tensor_file = diffusion_dataset.tensor

    """
    The pipeline is now ready to be run
    """
    study.run(registration_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print("\nOUTPUTS\n")
    outputs = registration_pipeline.get_outputs()
    for trait_name, trait_value in outputs.iteritems():
        print("{0}: {1}".format(trait_name, trait_value))

    """
    Will return:

    .. code-block:: python

        OUTPUTS

    """


if __name__ == '__main__':
    pilot()