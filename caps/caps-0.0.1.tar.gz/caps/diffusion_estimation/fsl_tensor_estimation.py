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
#         Brain Extraction Pipeline Definition
##############################################################

class FSLTensorEstimation(Pipeline):
    """ FSL Second Order Tensor Estimation

    Fit the diffusion tensor model using FSL DTIFit. For more details on this
    method, see the `DTIFit Documentation.
    <http://fsl.fmrib.ox.ac.uk/fsl/fsl4.0/fdt/fdt_dtifit.html>`_
    """

    def pipeline_definition(self):
        """ FSLTensorEstimation pipeline definition
        """

        # Create Processes
        self.add_process("fit", "nipype.interfaces.fsl.DTIFit",
                         make_optional=["terminal_output"])

        # Export Inputs
        self.export_parameter("fit", "dwi", pipeline_parameter="dw_image")
        self.export_parameter("fit", "bvals")
        self.export_parameter("fit", "bvecs")
        self.export_parameter("fit", "mask")

        # Export Outputs
        self.export_parameter("fit", "_tensor", pipeline_parameter="tensor")
        self.export_parameter("fit", "_FA",
                              pipeline_parameter="fractional_anisotropy")
        self.export_parameter("fit", "_MD",
                              pipeline_parameter="mean_diffusivity")

        # DTIFit algorithm parameters
        self.nodes["fit"].process.base_name = "dti"
        self.nodes["fit"].process.save_tensor = True


##############################################################
#                            Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/caps", **kwargs):
    """
    ==================================
    FSL Second Order Tensor Estimation
    ==================================

    .. link-to-block:: caps.diffusion_estimation.fsl_tensor_estimation.
                       FSLTensorEstimation
        :label: API
        :right-side: True

    .. topic:: Objective

        We propose here to estimate a second order tensor model from
        a diffusion sequence.

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
    Finally we need some generic python modules
    """
    import os

    """
    From caps we need the pipeline that will enable use to extract a brain
    mask and to fit the tensor model.
    """
    from caps.diffusion_preproc.bet import dBET
    from caps.diffusion_estimation.fsl_tensor_estimation import (
        FSLTensorEstimation)

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`
    """
    fit_working_dir = os.path.join(working_dir, "diffusion_fsl_fit")
    ensure_is_dir(fit_working_dir)
    default_config = SortedDictionary(
        ("output_directory", fit_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)

    """
    Load the toy dataset
    --------------------

    We want to perform DTIFit on a diffusion sequence.
    To do so, we use the *get_sample_data* function to load this
    dataset.

    .. seealso::

        For a complete description of the *get_sample_data* function, see the
        :ref:`Toy Datasets documentation <toy_datasets_guide>`
    """
    toy_dataset = get_sample_data("dwi")

    """
    The *toy_dataset* is an Enum structure with some specific
    elements of interest *dwi*, *bvals*, *bvecs* that contain the nifti
    diffusion image ,the b-values and the b-vectors respectively.
    """
    print(toy_dataset.dwi, toy_dataset.bvals, toy_dataset.bvecs)

    """
    Will return:

    .. code-block:: python

        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.nii
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bval
        /home/ag239446/git/nsap-src/nsap/data/DTI30s010.bvec

    We can see that the image has been found in a local directory

    Processing definition
    ---------------------

    Now we need to define the processing steps that will perform the tensor
    fit. To do so, we first need to extract the brain mask based on the b=0
    reference image. For a complete tutorial on how to use this pipeline,
    see the :ref:`dBET Tutorial. <example_caps.diffusion_preproc.bet.pilot>`
    """
    bet_pipeline = dBET()
    bet_pipeline.dw_image = toy_dataset.dwi
    bet_pipeline.bvals = toy_dataset.bvals
    study.run(bet_pipeline)

    """
    We then define the tensor fit processing step
    """
    fit_pipeline = FSLTensorEstimation()

    """
    It is possible to access the pipeline input specification.
    """
    print(fit_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        dw_image: ['File']
        bvals: ['File']
        bvecs: ['File']
        mask: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi informations:
    """
    fit_pipeline.dw_image = toy_dataset.dwi
    fit_pipeline.bvals = toy_dataset.bvals
    fit_pipeline.bvecs = toy_dataset.bvecs

    """
    And pipe the brain mask
    """
    fit_pipeline.mask = bet_pipeline.bet_mask_file

    """
    The pipeline is now ready to be run
    """
    study.run(fit_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print("\nOUTPUTS\n")
    for trait_name, trait_value in fit_pipeline.get_outputs().iteritems():
        print("{0}: {1}".format(trait_name, trait_value))

    """
    Will return:

    .. code-block:: python

        OUTPUTS

        mean_diffusivity: /volatile/nsap/caps/diffusion_fsl_fit/1-dtifit/
        dti_MD.nii.gz
        tensor: /volatile/nsap/caps/diffusion_fsl_fit/1-dtifit/
        dti_tensor.nii.gz
        fractional_anisotropy: /volatile/nsap/caps/diffusion_fsl_fit/
        1-dtifit/dti_FA.nii.gz
    """


if __name__ == '__main__':
    pilot()
