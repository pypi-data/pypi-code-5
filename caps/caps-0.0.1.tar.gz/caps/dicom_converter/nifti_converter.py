#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import dicom
import os
import nibabel
import tarfile
from nsap.lib.base import utils as tool
from nsap.lib.io import pydicom_series as dicom_tool

try:
    from traits.api import File, String, List, Directory, Bool
    from traits.trait_base import _Undefined
except ImportError:
    from enthought.traits.api import File, String, List, Directory, Bool

from capsul.process import Process
from capsul.pipeline import Pipeline

##############################################################
#         Nifti_converter Tool Processes
##############################################################


class InputDataManager(Process):
    """
    list dicom files in input folder, check format.
    """
    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("dicom_dir", Directory(optional=False))

        # Outputs
        self.add_trait("dicom_dir_first_dcm_file",
                       File(optional=False, output=True))

    def _run_process(self):
        # List valid dicoms images
        dicom_files = []
        for dcm in os.listdir(self.dicom_dir):
            if os.path.isfile(os.path.join(self.dicom_dir, dcm)):
                try:
                    dicom.read_file(os.path.join(self.dicom_dir, dcm))
                    dicom_files.append(os.path.join(self.dicom_dir, dcm))
                except:
                    continue
        self.dicom_dir_first_dcm_file = dicom_files[0]

    run = property(_run_process)


class NiftiHeaderFiller(Process):
    """ change nifti header
    """
    def __init__(self):
        super(NiftiHeaderFiller, self).__init__()

        # Inputs
        self.add_trait("dicom_files_location", File(optional=True))
        self.add_trait("fill_header", Bool(optional=True))
        self.add_trait("nifti_gz_file_list", List(File(), optional=False))

        # Outputs
        self.add_trait("filled_nifti_gz_file", File(optional=False,
                                                    output=True))

    def _run_process(self):
        self.filled_nifti_gz_file = _Undefined()
        if self.fill_header == True:
            nifti_gz_file = self.nifti_gz_file_list[0]
            #get informtion from dicom files
            (repetition_time, acquisition_order) = dicom_tool.dicom_meta(
                                os.path.dirname(self.dicom_files_location))
            #fill nifti header
            out_folder = add_meta_to_nii(nifti_gz_file, repetition_time,
                            acquisition_order, prefix="filled")
            self.filled_nifti_gz_file = os.path.join(out_folder,
                                            os.path.basename(nifti_gz_file))

    run = property(_run_process)

##############################################################
#         Nifti converter Pipeline Definition
##############################################################


class Converter_nifti(Pipeline):
    """ Coregistration Pipeline.
   Convert dicom files to nifti files
    """
    def pipeline_definition(self):

        # Create processes
        self.add_process("in_data_manager",
                         "caps.dicom_converter.nifti_converter.InputDataManager")
        self.add_process("nifti_converter",
                         "nipype.interfaces.dcm2nii.Dcm2nii")
        self.add_process("nifti_header_filler",
                         "caps.dicom_converter.nifti_converter.NiftiHeaderFiller")
                         
        # Export inputs
        self.export_parameter("in_data_manager", "dicom_dir")
        self.export_parameter("nifti_header_filler", "fill_header")
        
        # Link input DataManager
        self.add_link("in_data_manager.dicom_dir_first_dcm_file->"
                      "nifti_converter.source_names")
        self.add_link("in_data_manager.dicom_dir_first_dcm_file->"
                      "nifti_header_filler.dicom_files_location")
                      
        # Link nifti converter
        self.add_link("nifti_converter._converted_files->"
                      "nifti_header_filler.nifti_gz_file_list")
                      
        # Export outputs
        self.export_parameter("nifti_converter", "_converted_files",
                              pipeline_parameter="nifti_gz_file")
        self.export_parameter("nifti_header_filler", "filled_nifti_gz_file")
        self.export_parameter("nifti_converter", "_bvals")
        self.export_parameter("nifti_converter", "_bvecs")
       
        # dcm2nii algorithm parameters
        self.nodes["nifti_converter"].process.nii_output = True
        self.nodes["nifti_converter"].process.gzip_output = True
        self.nodes["nifti_converter"].process.anonymize = True
        self.nodes["nifti_converter"].process.reorient = False
        self.nodes["nifti_converter"].process.reorient_and_crop = False

        #  NiftiHeaderFiller algorithm parameters
        self.fill_header = True


def add_meta_to_nii(images, repetition_time,
                        acquisition_order, prefix="filled"):

    """ `Add slice duration and acquisition times to nifit header`
    **Parameters:**
        * images : list : a list of images.
        * repetition_time : float : the repetition time in ms.
        * acquisition_order : list : the slice order.
    **Outputs:**
        * outputs : list : modified images at the same location with
          the defined prefix.
    """
    # save metadata in nifti1
    for image in images:
        nii = nibabel.load(image)

        if isinstance(nii, nibabel.nifti1.Nifti1Image):
            dir_name = os.path.dirname(image)

            destination = os.path.join(os.path.dirname(dir_name),
                                       prefix + "_" + dir_name)
            tool.ensure_is_dir(destination)

            #Fill header
            header = nii.get_header()

            # slice_duration: Time for 1 slice
            header.set_dim_info(slice=2)
            nb_slices = header.get_n_slices()
            header.set_slice_duration(repetition_time / nb_slices)

            # dim_info: MRI slice ordering
            # slice_code: Slice timing order (set to None)
            acquisition_order *= header.get_slice_duration()
            times = acquisition_order.tolist()
            header.set_slice_times(times)

            # update image and save
            nii.update_header()
            nibabel.save(nii, os.path.join(destination,
                                           os.path.basename(image)))

        else:
            raise Exception("Only Nifti1 image are supported, "
                            "got: {0}".format(type(nii)))
        return destination

##############################################################
#                     Pilot
##############################################################


def pilot(working_dir="/volatile/nsap/casper",
          **kwargs):
    """ Coregistration Tool
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from soma.study_config import StudyConfig
    from soma.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.anatdcm

    # Create
    nifti_converter_pipeline = Converter_nifti()

    # Print Input Spec
    #print coreg_pipeline.get_input_spec()

    #untar archive
    converter_working_dir = os.path.join(working_dir, "converter")
    ensure_is_dir(converter_working_dir)

    tar_open = tarfile.open(toy_dataset.anatdcm)
    tar_open.extractall(path=os.path.join(converter_working_dir,
                                          "input_data"))
    tar_open.close()

    #get dicom dir
    dicom_dir = os.listdir(os.path.join(converter_working_dir, "input_data"))
    dicom_dir = dicom_dir[0]

    # Initialize pipeline
    nifti_converter_pipeline.dicom_dir = os.path.join(converter_working_dir,
                                                      "input_data", dicom_dir)
    nifti_converter_pipeline.fill_header = False

    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", converter_working_dir),
        ("use_smart_caching", True),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(nifti_converter_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in nifti_converter_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()
