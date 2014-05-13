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
#      Second Order Tensor Estimation Pipeline Definition
##############################################################

class SecondOrderTensorEstimation(Pipeline):
    """ Second Order Tensor Estimation
    
    .. hidden-technical-block::
        :label: [+show/hide tensor modelisation]
        :starthidden: True

        .. include:: source/_static/technical_documentation/diffusion_tensor.txt


    Fit the diffusion tensor model using two strategies:

    * :ref:`Ordinary least suquare fit
      <caps.diffusion_estimation.tensor_estimation.LSTensorEstimation>`
      (fast)
    * :ref:`Quartic decomposition based fit
      <caps.diffusion_estimation.tensor_estimation.QUARTICTensorEstimation>`
      (return positive semi definite tensors)

    Get :ref:`tensor scalar invariant properties
    <caps.diffusion_estimation.tensor_scalars.SecondOrderScalarParameters>`:
    the fractional anisotropy,
    the mean diffusivity and
    the Westion shapes coefficients.
    """

    def pipeline_definition(self):
        """ SecondOrderTensorEstimation pipeline definition
        """

        # Create Processes
        self.add_process("ols_fit", "caps.diffusion_estimation."
                         "tensor_estimation.LSTensorEstimation",
                         make_optional=["model_order", "estimate_odf"])
        self.add_process("quartic_fit", "caps.diffusion_estimation."
                         "tensor_estimation.QUARTICTensorEstimation",
                         make_optional=["model_order", "estimate_odf"])
        self.add_process("decomposition", "caps.diffusion_estimation."
                         "tensor_utils.DecomposeSecondOrderTensor")
        self.add_process("scalars", "caps.diffusion_estimation."
                         "tensor_scalars.SecondOrderScalarParameters")

        # Create switches
        self.add_switch("select_fit", ["ols", "quartic"],
                        ["tensor_file", ])
        # Export Inputs
        self.export_parameter("ols_fit", "dwi_file")
        self.export_parameter("ols_fit", "bvals_file")
        self.export_parameter("ols_fit", "bvecs_file")
        self.export_parameter("ols_fit", "mask_file")
        self.export_parameter("quartic_fit", "reference_file")

        # Link input
        self.add_link("dwi_file->quartic_fit.dwi_file")
        self.add_link("bvals_file->quartic_fit.bvals_file")
        self.add_link("bvecs_file->quartic_fit.bvecs_file")
        self.add_link("mask_file->quartic_fit.mask_file")

        # Link ols_fit
        self.add_link("ols_fit.tensor_file->"
                      "select_fit.ols_switch_tensor_file")

        # Link quartic_fit
        self.add_link("quartic_fit.tensor_file->"
                      "select_fit.quartic_switch_tensor_file")

        # Link select_fit switch
        self.add_link("select_fit.tensor_file->decomposition.tensor_file")

        # Link decomposition
        self.add_link("decomposition.eigen_values_file->"
                      "scalars.eigenvalues_file")

        # Export Outputs
        self.export_parameter("select_fit", "tensor_file")
        self.export_parameter("decomposition", "eigen_values_file")
        self.export_parameter("decomposition", "eigen_vectors_file")
        self.export_parameter("scalars", "fractional_anisotropy_file")
        self.export_parameter("scalars", "mean_diffusivity_file")
        self.export_parameter("scalars", "linearity_file")
        self.export_parameter("scalars", "planarity_file")
        self.export_parameter("scalars", "sphericity_file")

        # DecomposeSecondOrderTensor algorithm parameters
        self.nodes["ols_fit"].process.model_order = 2
        self.nodes["ols_fit"].process.model_name = "tensor"
        self.nodes["ols_fit"].process.estimate_odf = False

        # QUARTICTensorEstimation algorithm parameters
        self.nodes["quartic_fit"].process.model_order = 2
        self.nodes["quartic_fit"].process.model_name = "tensor"
        self.nodes["quartic_fit"].process.number_of_workers = -1
        self.nodes["quartic_fit"].process.estimate_odf = False

        # DecomposeSecondOrderTensor algorithm parameters
        self.nodes["decomposition"].process.eigenvecs_basename = "eigenvecs"
        self.nodes["decomposition"].process.eigenvals_basename = "eigenvals"
        self.nodes["decomposition"].process.number_of_workers = -1

        # SecondOrderScalarParameters algorithm parameters
        self.nodes["scalars"].process.fa_basename = "fa"
        self.nodes["scalars"].process.md_basename = "md"


##############################################################
#      Fourth Order Tensor Estimation Pipeline Definition
##############################################################

class FourthOrderTensorEstimation(Pipeline):
    """ Fourth Order Tensor Estimation

    Fit the diffusion tensor model using an ordinary least suquare procedure
    or a quartic decomposition.

    Note that the adc or the orientation distribution function can be
    modeled.
    """

    def pipeline_definition(self):
        """ FourthOrderTensorEstimation pipeline definition
        """

        # Create Processes
        self.add_process("ols_fit", "caps.diffusion_estimation."
                         "tensor_estimation.LSTensorEstimation",
                         make_optional=["model_order"])
        self.add_process("quartic_fit", "caps.diffusion_estimation."
                         "tensor_estimation.QUARTICTensorEstimation",
                         make_optional=["model_order"])
        self.add_process("scalars", "caps.diffusion_estimation."
                         "tensor_scalars.FourthOrderScalarParameters")

        # Create switches
        self.add_switch("select_fit", ["ols", "quartic"],
                        ["tensor_file", ])
        # Export Inputs
        self.export_parameter("ols_fit", "dwi_file")
        self.export_parameter("ols_fit", "bvals_file")
        self.export_parameter("ols_fit", "bvecs_file")
        self.export_parameter("ols_fit", "mask_file")
        self.export_parameter("ols_fit", "estimate_odf")
        self.export_parameter("quartic_fit", "reference_file")

        # Link input
        self.add_link("estimate_odf->quartic_fit.estimate_odf")
        self.add_link("mask_file->scalars.mask_file")
        self.add_link("dwi_file->quartic_fit.dwi_file")
        self.add_link("bvals_file->quartic_fit.bvals_file")
        self.add_link("bvecs_file->quartic_fit.bvecs_file")
        self.add_link("mask_file->quartic_fit.mask_file")

        # Link ols_fit
        self.add_link("ols_fit.tensor_file->"
                      "select_fit.ols_switch_tensor_file")

        # Link quartic_fit
        self.add_link("quartic_fit.tensor_file->"
                      "select_fit.quartic_switch_tensor_file")

        # Link select_fit switch
        self.add_link("select_fit.tensor_file->scalars.tensor_file")

        # Export Outputs
        self.export_parameter("select_fit", "tensor_file")
        self.export_parameter("scalars", "generalized_anisotropy_file")
        self.export_parameter("scalars", "mean_diffusivity_file")

        # DecomposeSecondOrderTensor algorithm parameters
        self.nodes["ols_fit"].process.model_order = 4
        self.nodes["ols_fit"].process.model_name = "tensor"
        self.nodes["ols_fit"].process.estimate_odf = False

        # QUARTICTensorEstimation algorithm parameters
        self.nodes["quartic_fit"].process.model_order = 4
        self.nodes["quartic_fit"].process.model_name = "tensor"
        self.nodes["quartic_fit"].process.number_of_workers = -1
        self.nodes["quartic_fit"].process.estimate_odf = False

        # FourthOrderScalarParameters algorithm parameters
        self.nodes["scalars"].process.ga_basename = "ga"
        self.nodes["scalars"].process.md_basename = "md"


##############################################################
#                            Pilot
##############################################################

def pilot_second_order():
    """
    ==================================
    Second Order Tensor Estimation
    ==================================

    .. link-to-block:: caps.diffusion_estimation.py_tensor_estimation.
                       SecondOrderTensorEstimation
        :label: API
        :right-side: True

    .. topic:: Objective

        We propose here to estimate a second order tensor model from
        a diffusion sequence with two different strategies:

        1) the first strategy do not guarantee the positive definitness of
        the estimated tensors (we call this method OLS for Ordinary
        Least Square).

        2) the second one enables the estimation of semi-definite
        positive tensors (the quartic method).

    Introduction
    ------------

    Diffusion-Weighted Magnetic Resonance imaging (DW-MRI) provides a
    unique probe to characterize the microstructure of materials.
    DTI (Diffusion Tensor Imaging) measures the diffusion properties of
    water molecules, and provides a physical description of the water
    motion anisotropic behavior using a tensor representation. An excellent
    introduction to DW-MRI is available in [1]_.

    Diffusion tensors are usually estimated by solving this equation using
    a standard :ref:`least squares procedure
    <caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation>`.
    Since this procedure does not guarantee the positive definiteness of
    the tensors, negative eigenvalues are often set to an arbitrary small
    positive value.

    To overcome this limitation some authors directly estimate
    positive-semi-definite tensors using a
    :ref:`quartic decomposition with a non negative least quare procedure
    <caps.diffusion_estimation.py_tensor_estimation.SecondOrderTensorEstimation>`.

    Import
    ------

    First we load the function that enables us to access the toy datasets:
    """
    from caps.toy_datasets import get_sample_data

    """
    From capsul we then load the class to configure the study we want to
    perform:
    """
    from capsul.study_config import StudyConfig

    """
    Here two utility tools are loaded. The first one enables the creation
    of ordered dictionary and the second ensure that a directory exists.
    Note that the directory will be created if necessary.
    """
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    """
    We need some generic python modules:
    """
    import os

    """
    From caps we need the pipeline that will enable use to estimate the
    tensor model and the one necessary to extract the brain from a
    diffusion sequence:
    """
    from caps.diffusion_preproc.bet import dBET
    from caps.diffusion_estimation.py_tensor_estimation import (
        SecondOrderTensorEstimation)

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`

    We first define the current working directory:
    """
    working_dir = "/volatile/nsap/caps"
    fit_working_dir = os.path.join(working_dir, "diffusion_py_fit_second")
    ensure_is_dir(fit_working_dir)

    """
    And then define the study configuration:
    """
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

    We want to perform a second order tensor fit on a diffusion sequence data.
    To do so, we use the *get_sample_data* function to load the
    dataset:

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
    fit_pipeline = SecondOrderTensorEstimation()

    """
    It is possible to access the pipeline input specifications:
    """
    print(fit_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        dwi_file: ['File']
        bvals_file: ['File']
        bvecs_file: ['File']
        mask_file: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi informations:
    """
    fit_pipeline.dwi_file = toy_dataset.dwi
    fit_pipeline.bvals_file = toy_dataset.bvals
    fit_pipeline.bvecs_file = toy_dataset.bvecs

    """
    And pipe the brain mask and reference image
    """
    fit_pipeline.mask_file = bet_pipeline.bet_mask_file
    fit_pipeline.reference_file = bet_pipeline.outelements[0]

    """
    Before running the pipeline, you need to select the fitting method you
    want to use.
    The *ols* strategy is fast but estimated tensor may not be relevant.
    The *quartic* strategy is quite slow but the expected diffusivity
    coefficients are >=0.
    In pratice, for good SNR, the difference is small in anatomical
    structures.
    """
    fit_pipeline.select_fit = "ols"

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
    **References**

    .. [1] Mori, S., 2007. Introduction to Diffusion Tensor Imaging.
           Elsevier.
    """


def pilot_fourth_order():
    """
    ==================================
    Fourth Order Tensor Estimation
    ==================================

    .. link-to-block:: caps.diffusion_estimation.py_tensor_estimation.
                       FourthOrderTensorEstimation
        :label: API
        :right-side: True

    .. topic:: Objective

        We propose here to estimate a fourth order tensor model from
        a diffusion sequence with two different strategies.
        The first strategy do not guarantee the positive definitness of
        the estimated tensor (we call this method OLS for ordinary
        least square). The second one enables us to estimate semi-definite
        positive tensors (the quartic method).
        In both cases wa can model either the adc or the odf

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
    From caps we need the pipeline that will enable use to estimate the
    tensor model.
    """
    from caps.diffusion_preproc.bet import dBET
    from caps.diffusion_estimation.py_tensor_estimation import (
        FourthOrderTensorEstimation)

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`

    We first define the current working directory
    """
    working_dir = "/volatile/nsap/caps"
    fit_working_dir = os.path.join(working_dir, "diffusion_py_fit_fourth")
    ensure_is_dir(fit_working_dir)

    """
    And then define the study configuration.
    """
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

    We want to perform a second order tensor fit on a diffusion sequence data.
    To do so, we use the *get_sample_data* function to load the
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
    fit_pipeline = FourthOrderTensorEstimation()

    """
    It is possible to access the pipeline input specification.
    """
    print(fit_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        dwi_file: ['File']
        bvals_file: ['File']
        bvecs_file: ['File']
        mask_file: ['File']

    We can now tune the pipeline parameters.
    We first set the input dwi informations:
    """
    fit_pipeline.select_fit = "quartic"  # ToDo
    fit_pipeline.dwi_file = toy_dataset.dwi
    fit_pipeline.bvals_file = toy_dataset.bvals
    fit_pipeline.bvecs_file = toy_dataset.bvecs

    """
    And pipe the brain mask and reference image
    """
    fit_pipeline.mask_file = bet_pipeline.bet_mask_file
    fit_pipeline.reference_file = bet_pipeline.outelements[0]

    """
    Before running the pipeline, you need to select the fitting method you
    want to use.
    The ols strategy is fast but estimated tensor may not be relevant.
    The quartic strategy is quite slow but the expected diffusivity
    coefficients are >=0.
    In pratice, for good SNR, the difference is small in anatomical
    structures.
    """
    fit_pipeline.estimate_odf = False
    # fit_pipeline.select_fit = "quartic"

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

        mean_diffusivity_file: /volatile/nsap/caps/diffusion_py_fit_fourth/
        2-fourthorderscalarparameters/md.nii.gz
        generalized_anisotropy_file: /volatile/nsap/caps/
        diffusion_py_fit_fourth/2-fourthorderscalarparameters/ga.nii.gz
        tensor_file: /volatile/nsap/caps/diffusion_py_fit_fourth/
        1-lstensorestimation/tensor.nii.gz
    """

if __name__ == '__main__':
    pilot_second_order()
    #pilot_fourth_order()
