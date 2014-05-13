#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

try:
    from traits.api import File, Float, Int, List, Any, Str, Directory, Either
except ImportError:
    from enthought.traits.api import (File, Float, Int, List, Any, Str, Directory,
                                     Either)

import sys
import os
from capsul.process import Process
from capsul.pipeline import Pipeline

import numpy
import nibabel

from nsap.use_cases.fmri.utils import get_nb_slices, save_cutom_timings
from caps.preclinic_functional.spm_utility import ungzip_image, gzip_image

##############################################################
#         Slice Timing Tool Processes
##############################################################


class InputDataManager(Process):
    """ Process that enables us to get image informations:
    * the repetition time
    * the slice times
    * the number of slices
    And format the fonctional input image accordingly to the switch value.
    """
    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("fmri_image", File(optional=False))
        self.add_trait("slicing_type", Str(optional=False))
        self.add_trait("force_repetition_time", Float(optional=True))
        self.add_trait("force_slice_times", List(Int(), optional=True))

        # Outputs
        self.add_trait("repetition_time", Float(optional=False, output=True))
        self.add_trait("acquisition_time", Float(optional=False, output=True))
        self.add_trait("slice_times", List(Int(), optional=False, output=True))
        self.add_trait("number_of_slices", Int(optional=False, output=True))
        self.add_trait("out_fmri_image", Any(optional=False, output=True))

    def _run_process(self):
        """ Ececute this Process
        """
        # Load the image and get its header
        nii = nibabel.load(self.fmri_image)
        header = nii.get_header()

        # Get image information from header if necessary
        if not self.force_repetition_time or not self.force_slice_times:
            try:
                self.number_of_slices = header.get_n_slices()
                slice_duration = header.get_slice_duration()
                slice_times = numpy.asarray(header.get_slice_times())
            except:
                raise Exception("SliceTiming pipeline fails to import"
                                "functional nifti image "
                                "properly!\n\n{1}".format(sys.exc_info()))
        else:
            self.number_of_slices = get_nb_slices(self.fmri_image)

        # Fill the repetition time
        if not self.force_repetition_time:
            self.repetition_time = (slice_duration * self.number_of_slices
                                    / 1000.)  # seconds
        else:
            self.repetition_time = self.force_repetition_time

        # Fill the slice times
        if not self.force_slice_times:
            self.slice_times = numpy.round(slice_times /
                                           slice_duration).astype(int)
        else:
            self.slice_times = self.force_slice_times

        # Compute time acquisition
        self.acquisition_time = self.repetition_time * (1. - 1. / 40.)

        # Reorganize the output image accordingly to the
        # selected slicing algorithm
        if self.slicing_type == "spm":
            spm_image = ungzip_image(self.fmri_image, self.output_directory)
            self.out_fmri_image = [spm_image, ]
            self.slice_times = [x + 1 for x in self.slice_times]
        elif self.slicing_type in ["fsl", "none"]:
            self.out_fmri_image = self.fmri_image
        else:
            raise Exception("Uknown slicing option"
                            "'{0}'".format(self.slicing_type))

    run = property(_run_process)


class OutputDataManager(Process):
    """ Process that format the fonctional slice time corrected image
    accordingly to the switch value.
    """
    def __init__(self):
        super(OutputDataManager, self).__init__()

        # Inputs
        self.add_trait("unformated_fmri_result", Any(optional=False))
        self.add_trait("slicing_type", Str(optional=False))

        # Outputs
        self.add_trait("time_corrected_fmri_image",
                       File(optional=False, output=True))

    def _run_process(self):
        if self.slicing_type == "spm":
            self.time_corrected_fmri_image = gzip_image(
                self.unformated_fmri_result[0], self.output_directory)
        elif self.slicing_type in ["fsl", "none"]:
            self.time_corrected_fmri_image = self.unformated_fmri_result
        else:
            raise Exception("Uknown slicing option"
                            "'{0}'".format(self.slicing_type))

    run = property(_run_process)


class FSLSaveCustomTimings(Process):
    """ Process to save the cutom timings on disk
    """
    def __init__(self):
        super(FSLSaveCustomTimings, self).__init__()

        # Inputs
        self.add_trait("slice_times", List(Int(), optional=False))

        # Outputs
        self.add_trait("slice_times_file", File(optional=False, output=True))

    def _run_process(self):
        # Type conversion
        custom_timings = numpy.asarray(
            self.slice_times).astype(numpy.single)
        # Express slice_times as fractions of TR
        custom_timings = custom_timings / numpy.max(custom_timings)
        # In FSL slice timing, an existing file is expected
        self.slice_times_file = save_cutom_timings(
            custom_timings=custom_timings,
            out_folder=self.output_directory)[0]

    run = property(_run_process)


##############################################################
#         Slice Timing Pipeline Definition
##############################################################

class SliceTiming(Pipeline):

    def pipeline_definition(self):
        """Slice Timing Pipeline.
        Definition of the slice timing pipeline. Three options are available.
        You can perform the slice timing with:
        * SPM
        * FSL
        * or do not perform this step (for instance if the TR is short).

        Parameters
        ----------
        fmri_image: str or list of str (mandatory)
            The functional image that need to be corrected for slice timing.
        select_slicing: enum (default spm)
            Options are {spm, fsl, none}.
            Switch between the algorithm you want to use.
        force_repetition_time: float (optional)
            The time between slice acquisitions of the functional sequence.
            If not specified, the repetition_time is searched in the fmri_image
            header.
        force_slice_times: list of int (optional)
            The acquisiton slice order.
            If not specified, the slice_times is searched in the fmri_image
            header.

        Returns
        -------
        time_corrected_fmri_image: str or list of str
            Slice time corrected image.
        number_of_slices: int
            number of slices in a functional volume.
        repetition_time: float
            The time between slice acquisitions of the functional sequence.
        acquisition_time: float
            The time of slice acquisition of the functional sequence.
        slice_times: list of int or str
            The acquisiton slice order.
        """
        # Create processes
        self.add_process("in_data_manager",
                         "caps.preclinic_functional.slice_timing.InputDataManager")
        self.add_process("spm_slice_timing",
                         "nipype.interfaces.spm.SliceTiming",
                         make_optional=["ref_slice"])
        self.add_process("save_timing",
                         "caps.preclinic_functional.slice_timing.FSLSaveCustomTimings")
        self.add_process("fsl_slice_timing",
                         "nipype.interfaces.fsl.SliceTimer",
                         make_optional=["terminal_output"])
        self.add_process("out_data_manager",
                         "caps.preclinic_functional.slice_timing.OutputDataManager")
        # Create a Switch
        self.add_switch('select_slicing',
                        ['fsl', 'spm', 'none'],
                        ['time_corrected_fmri_image', ])

        # Export inputs
        self.export_parameter("in_data_manager", "fmri_image")
        self.export_parameter("in_data_manager", "force_repetition_time")
        self.export_parameter("in_data_manager", "force_slice_times")

        # Link input DataManager
        self.add_link("select_slicing->in_data_manager.slicing_type")

        # Link SPM
        self.add_link("in_data_manager.out_fmri_image->"
                      "spm_slice_timing.in_files")
        self.add_link("in_data_manager.number_of_slices->"
                      "spm_slice_timing.num_slices")
        self.add_link("in_data_manager.repetition_time->"
                      "spm_slice_timing.time_repetition")
        self.add_link("in_data_manager.acquisition_time->"
                      "spm_slice_timing.time_acquisition")
        self.add_link("in_data_manager.slice_times->"
                      "spm_slice_timing.slice_order")

        # Link FSL
        self.add_link("in_data_manager.out_fmri_image->"
                      "fsl_slice_timing.in_file")
        self.add_link("in_data_manager.slice_times->save_timing.slice_times")
        self.add_link("in_data_manager.repetition_time->"
                      "fsl_slice_timing.time_repetition")
        self.add_link("save_timing.slice_times_file->"
                      "fsl_slice_timing.custom_timings")

        # Link Switch
        self.add_link("in_data_manager.out_fmri_image->"
                      "select_slicing.none_switch_time_corrected_fmri_image")
        self.add_link("spm_slice_timing._timecorrected_files->"
                      "select_slicing.spm_switch_time_corrected_fmri_image")
        self.add_link("fsl_slice_timing._slice_time_corrected_file->"
                      "select_slicing.fsl_switch_time_corrected_fmri_image")

        # Link output DataManager
        self.add_link("select_slicing->out_data_manager.slicing_type")
        self.add_link("select_slicing.time_corrected_fmri_image->"
                      "out_data_manager.unformated_fmri_result")

        # Export outputs
        self.export_parameter("in_data_manager", "number_of_slices",
                              is_enabled=False)
        self.export_parameter("in_data_manager", "repetition_time",
                              is_enabled=False)
        self.export_parameter("in_data_manager", "acquisition_time",
                              is_enabled=False)
        self.export_parameter("in_data_manager", "slice_times",
                              is_enabled=False)
        self.export_parameter("out_data_manager", "time_corrected_fmri_image",
                              is_enabled=False)

        # SPM algorithm parameters
        self.nodes["spm_slice_timing"].process.ref_slice = 1
        self.nodes["spm_slice_timing"].process.out_prefix = "a"

        # FSL algorithm parameters
        self.nodes["fsl_slice_timing"].process.output_type = "NIFTI_GZ"
        self.nodes["fsl_slice_timing"].process.slice_direction = 3


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/casper",
          slicing_option="none",
          **kwargs):
    """ Slice Timing Tool
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary
    from nsap.lib.base import ensure_is_dir

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")

    # Create
    st_pipeline = SliceTiming()

    # Print Input Spec
    print st_pipeline.get_input_spec()

    # Initialize SliceTiming pipeline
    st_pipeline.fmri_image = toy_dataset.fmri
    st_pipeline.select_slicing = slicing_option
    st_pipeline.force_repetition_time = toy_dataset.TR
    st_pipeline.force_slice_times = list(range(40))

    # Execute the pipeline
    st_working_dir = os.path.join(working_dir, "slice_timing")
    ensure_is_dir(st_working_dir)
    default_config = SortedDictionary(
        ("output_directory", st_working_dir),
        ("fsl_config", "/etc/fsl/4.1/fsl.sh"),
        ("use_fsl", True),
        ("spm_directory", "/i2bm/local/spm8"),
        ("matlab_exec", "/neurospin/local/bin/matlab"),
        ("spm_exec_cmd", "/i2bm/local/bin/spm8"),
        ("use_spm_mcr", False),
        ("use_smart_caching", True),
        ("generate_logging", True)
    )
    study = StudyConfig(default_config)
    study.run(st_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in st_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot(slicing_option="spm")
