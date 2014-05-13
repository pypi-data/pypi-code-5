#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import dicom as dicomtk

#from dicom.values import converters, convert_UN
import time
import sys
import euaims_tools
import dicom_tools
import os
import anon_additional
from caps.dicom_converter.base.tools import (ensure_is_dir,
                                             progress_bar)

#try:
from traits.api import String, Dict, Directory, File
#except ImportError:
#    from enthought.traits.api import (String, List, Directory,
#                                      Bool, Dictionary, File)

from capsul.process import Process
from capsul.pipeline import Pipeline

##############################################################
#        Dicom anonymizer Tool Processes
##############################################################


class InputDataManager(Process):
    """ Generate psc2 and pathes for processing. Select not
    already processed packages

    Lists all packages from PSC1 folders
    Gets already processed packages from register
    Outputs new packages to process
    """

    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("log_path", Directory(
                                    optional=False,
                                    output=False,
                                    desc="path to root log folder"))
        self.add_trait("root_dir", Directory(
                                    output=False,
                                    optional=False,
                                    desc="path to general PSC1s fodler"))
        # Outputs
        self.add_trait("meta_infos", Dict(
                        optional=False,
                        output=True,
                        desc="dictionnary meta_infos[<psc1>]:<package_path>"))
        self.add_trait("log", String(
                            optional=False,
                            output=True,
                            desc="generate log string to write"))

    def _run_process(self):

        # generate batch log
        logger = "Scanning dicom folders for de-identification\n"

        # List processed packages
        processed_psc1_list = []
        state_log = os.path.join(self.log_path, "state/pre-processed.txt")
        buff = open(state_log)
        lines = buff.readlines()
        buff.close()
        for line in lines:
            processed_psc1_list.append(line.replace("\n", ""))

        logger += "{0} packages already processed\n".format(
                                                    len(processed_psc1_list))
        # Generate list of PSC1 to process with their pathes:
        buff = {}
        for centres in os.listdir(self.root_dir):
            for packages in os.listdir(os.path.join(self.root_dir, centres)):
                psc1 = packages[:9]
                if not psc1 in processed_psc1_list:
                    buff[psc1] = os.path.join(self.root_dir, centres, packages)
        self.meta_infos = buff
        logger += ("{0} new packages to process through de-identification,\n"
                "processing now...\n".format(len(buff)))
        self.log = logger
    run = property(_run_process)


class DicomDeIdentifier(Process):
    """  Dicom de-identification and checks

    save dicom files in "Images" fodler (bulk mode)
    Split dicoms among standard-named serie folder
    Check serie completion : number of files should be equal to
    number of slices
    """
    def __init__(self):
        super(DicomDeIdentifier, self).__init__()

        # Inputs
        self.add_trait("converter_path", File(
                                    output=False,
                                    optional=False,
                                    desc="path to converting table"))
        self.add_trait("out_dir_root", Directory(
                                        output=False,
                                        optional=False,
                                        desc="output folder root"))
        self.add_trait("log_files", Directory(
                                        output=False,
                                        optional=False,
                                    desc="path to root log folder"))
        self.add_trait("meta_infos", Dict(
                                    exists=True,
                                    optional=False,
                                desc="dictionnary meta_infos[<psc1>]:"
                                                            "<package_path>"))

        # Outputs
        self.add_trait("log", String(
                            optional=False,
                            output=True,
                            desc="generate log string to write"))

    def _run_process(self):

        # Get converter
        converter_to_psc2 = euaims_tools.get_converter_to_psc2(
                                                        self.converter_path)
        gen = ""
        log = ""

        for psc1 in self.meta_infos:
            flag_error = False

            # Loggers information
            # Open package-related logfile
            # Get centre for each package
            centre = euaims_tools.get_centre_from_psc1(psc1)
            logfile = open(os.path.join(self.log_files, centre,
                "{0}.log".format(os.path.basename(self.meta_infos[psc1]))),
                                                                        "a")

            log += "*" * 40 + "\n"
            log += "**** Dicoms de-identification procedure ****\n"
            log += "Date: {0}, Time: {1}\n".format(time.strftime("%x"),
                                                        time.strftime("%X"))
            log += "*" * 40 + "\n\n"
            gen += "Processing package {0}\n".format(
                                    os.path.basename(self.meta_infos[psc1]))

            # proceed to de-identification
            sequences_path = os.path.join(self.meta_infos[psc1], "Images")

            for cnt, sequences in enumerate(os.listdir(sequences_path)):
                # Dicoms in sub-folders
                if os.path.isdir(os.path.join(sequences_path, sequences)):
                    dicoms = os.listdir(os.path.join(sequences_path,
                                                                 sequences))
                    tot = len(dicoms)
                    for count, dicom in enumerate(dicoms):
                        progress_bar(float(count + 1) / tot)
                        try:
                            # De-identification
                            dataset = dicomtk.read_file(os.path.join(
                                        sequences_path, sequences, dicom))
                            fileName = "{0}_{1}".format(cnt, count)
                            new_uid = converter_to_psc2[psc1]

                            output = dicom_tools.anonymize_dicom(
                                                    dataset,
                                                    fileName,
                                                    new_uid=new_uid,
                    remove_curves=self.remove_curves,
                    remove_overlays=self.remove_overlays,
                    use_sop_instance_uid=self.use_sop_instance_uid)

                             # Write de-identificated dicoms
                            if "First" in os.path.basename(
                                                        self.meta_infos[psc1]):
                                dicom_out_folder = os.path.join(
                                self.out_dir_root, centre,
                                        "{0}_First".format(new_uid), "Images")
                            else:
                                dicom_out_folder = os.path.join(
                                self.out_dir_root, centre,
                                        "{0}_Second".format(new_uid), "Images")
                            euaims_tools.create_tree(dicom_out_folder)
                            savePath = os.path.join(dicom_out_folder,
                                                "{0}.dcm".format(output[1]))
                            dataset = output[0]
                            dataset.save_as(savePath)
                        except:
                            flag_error = True
                            gen += ("Unexpected error while processing:\n"
                                    "{0}\n".format(os.path.join(sequences_path,
                                                              sequences,
                                                              dicom)))
                            gen += "{0}\n".format(sys.exc_info())
                            log += ("Unexpected error while processing:\n"
                                    "{0}\n\n".format(os.path.join(
                                                            sequences_path,
                                                              sequences,
                                                              dicom)))
                            log += "{0}\n".format(sys.exc_info())
                            break
                # Dicoms in bulk
                else:
                    total = len(os.listdir(sequences_path))
                    progress_bar(float(cnt + 1) / total)
                    try:
                        # De-identification
                        dataset = dicomtk.read_file(os.path.join(
                                            sequences_path, sequences))
                        fileName = cnt
                        new_uid = converter_to_psc2[psc1]

                        output = dicom_tools.anonymize_dicom(
                                                dataset,
                                                fileName,
                                                new_uid=new_uid,
                remove_curves=self.remove_curves,
                remove_private_tags=self.remove_private_tags,
                remove_overlays=self.remove_overlays,
                fill_public_diffusion_tags=self.fill_public_diffusion_tags,
                use_sop_instance_uid=self.use_sop_instance_uid)

                         # Write de-identificated dicoms
                        if "First" in os.path.basename(self.meta_infos[psc1]):
                            dicom_out_folder = os.path.join(
                            self.out_dir_root, centre,
                                    "{0}_First".format(new_uid), "Images")
                        else:
                            dicom_out_folder = os.path.join(
                            self.out_dir_root, centre,
                                    "{0}_Second".format(new_uid), "Images")
                        euaims_tools.create_tree(dicom_out_folder)
                        savePath = os.path.join(dicom_out_folder,
                                            "{0}.dcm".format(output[1]))
                        dataset = output[0]
                        dataset.save_as(savePath)
                    except:
                        flag_error = True
                        gen += ("Unexpected error while processing:\n"
                                "{0}\n".format(os.path.join(sequences_path,
                                                          sequences)))
                        gen += "{0}\n".format(sys.exc_info())
                        log += ("Unexpected error while processing:\n"
                                "{0}\n\n".format(os.path.join(sequences_path,
                                                          sequences)))
                        log += "{0}\n".format(sys.exc_info())
                        break

            # Normalize sequences
            log += ("Splitting dicom files in sequence"
                                                " folders now ...\n")
            gen += ("Splitting dicom files in sequence"
                                                " folders now ...\n")
            out = euaims_tools.normalize_sequences(dicom_out_folder)
            log += "{0}\n".format(out)
            gen += "{0}\n".format(out)

            log += ("Checking for a missing slice ...\n")
            gen += ("Checking for a missing slice ...\n")

            out = euaims_tools.Check_missing_slice(dicom_out_folder)

            log += "{0}\n".format(out)
            gen += "{0}\n".format(out)

            if not flag_error:
                gen += "Dicoms successfully de-identificated !\n"
                gen += "PSC2-encoded dicoms stored in {0}\n".format(
                                                            dicom_out_folder)
                log += "Dicoms successfully de-identificated !\n"
                log += "PSC2-encoded dicoms stored in {0}\n\n".format(
                                                            dicom_out_folder)
            logfile.write(log)
            logfile.close()
            self.log = gen
    run = property(_run_process)


class AddDeidentifier(Process):
    """ De-identification of additional Data (one method for each center)

    Raise warning if unknown additional files is encountered
    """
    def __init__(self):
        super(AddDeidentifier, self).__init__()

        # Inputs
        self.add_trait("converter_path", File(
                                    output=False,
                                    optional=False,
                                    desc="path to converting table"))
        self.add_trait("out_dir_root", Directory(
                                        output=False,
                                        optional=False,
                                        desc="output folder root"))
        self.add_trait("log_files", Directory(
                                        output=False,
                                        optional=False,
                                    desc="path to root log folder"))
        self.add_trait("meta_infos", Dict(
                                    exists=True,
                                    optional=False,
                                desc="dictionnary meta_infos[<psc1>]:"
                                                            "<package_path>"))

        # Outputs
        self.add_trait("log", String(
                            optional=False,
                            output=True,
                            desc="generate log string to write"))

    def _run_process(self):
        # Get converter
        converter_to_psc2 = euaims_tools.get_converter_to_psc2(
                                                        self.converter_path)
        gen = ""
        log = ""
        for psc1 in self.meta_infos:
            psc2 = converter_to_psc2[psc1]

            # Loggers information
            # Open package-related logfile
            # Get centre for each package
            centre = euaims_tools.get_centre_from_psc1(psc1)
            logfile = open(os.path.join(self.log_files, centre,
                "{0}.log".format(os.path.basename(self.meta_infos[psc1]))),
                                                                        "a")

            log += "*" * 40 + "\n"
            log += "**** Additional files de-identification procedure ****\n"
            log += "Date: {0}, Time: {1}\n".format(time.strftime("%x"),
                                                        time.strftime("%X"))
            log += "*" * 40 + "\n\n"
            gen += "Processing package {0}\n".format(
                                    os.path.basename(self.meta_infos[psc1]))

            # proceed to de-identification
            files_path = os.path.join(self.meta_infos[psc1],
                                                          "AdditionalData")
            if "First" in os.path.basename(self.meta_infos[psc1]):
                add_out_folder = os.path.join(
                self.out_dir_root, centre,
                        "{0}_First".format(psc2), "AdditionalData")
            else:
                add_out_folder = os.path.join(
                self.out_dir_root, centre,
                        "{0}_Second".format(psc2), "AdditionalData")
            euaims_tools.create_tree(add_out_folder)
            try:
                if centre == "LONDON":
                    for additional_file in os.listdir(files_path):
                        # Get file extension
                        out_name = additional_file.replace(psc1, psc2)
                        out_path_root = add_out_folder
                        if additional_file.split(".")[-1] == "log":
                            in_path = os.path.join(files_path, additional_file)
                            out_path = os.path.join(out_path_root, out_name)
                            anon_additional.deIdent_London_log(in_path,
                                                               out_path, psc2)
                        elif additional_file.split(".")[-1] == "txt":
                            in_path = os.path.join(files_path, additional_file)
                            out_path = os.path.join(out_path_root, out_name)
                            anon_additional.deIdent_London_txt(in_path,
                                                               out_path, psc2)
                        else:
                            log += ("WARNING, unknown file: {0} of package {1}"
                                "from {2}\n".format(additional_file,
                                            self.meta_infos[psc1]), centre)
                            gen += ("WARNING, unknown file: {0} of package {1}"
                                "from {2}\n".format(additional_file,
                                            self.meta_infos[psc1]), centre)
            except:
                log += ("Error while processing additional"
                                "files of {0}".format(self.meta_infos[psc1]))
                gen += ("Error while processing additional"
                                "files of {0}".format(self.meta_infos[psc1]))
                log += "{0}\n".format(sys.exc_info())
                gen += "{0}\n".format(sys.exc_info())
                logfile.write(log)
                logfile.close()
                continue

            # Log file completion
            gen += "Additional files successfully de-identificated !\n"
            gen += "PSC2-encoded package stored in {0}\n".format(
                                                        add_out_folder)
            log += "Additional files successfully de-identificated !\n"
            log += "PSC2-encoded package stored in {0}\n\n".format(
                                                        add_out_folder)
            logfile.write(log)
            logfile.close()

            # Add package in pre-processed list
            state_log = os.path.join(self.log_files, "state/pre-processed.txt")
            state_file = open(state_log, "a")
            state_file.write("{0}\n".format(psc1))
            state_file.close()

        self.log = gen

    run = property(_run_process)


class LoggerWritter(Process):
    """ Get all log string from different boxes and write them in batch
    logfiles
    """
    def __init__(self):
        super(LoggerWritter, self).__init__()

        # Inputs
        self.add_trait("dicom_log", String(
                                    exists=True,
                                    optional=False,
                                desc="log string from dicom-deidentifier box"))

        self.add_trait("Additional_log", String(
                                    exists=True,
                                    optional=False,
                                desc="log string from add-deidentifier box"))
        self.add_trait("batch_log_loc", String(
                                    exists=True,
                                    optional=False,
                                    desc="path to root log folder"))
        self.add_trait("in_manager_log", String(
                                    exists=True,
                                    optional=False,
                                desc="log string from input_manager box"))
        # Outputs
        self.add_trait("out_print", String(
                            exists=True,
                            optional=False,
                            output=True,
                            desc="print output"))

    def _run_process(self):
        today = time.strftime("%Y%m%d")
        log_file = open(os.path.join(self.batch_log_loc,
                                     "batch/de_identification",
                                     '{0}-{1}.log'.format(today,
                                        time.strftime("%X"))), "w")
        log_file.write(self.in_manager_log)
        log_file.write(self.dicom_log)
        log_file.write(self.Additional_log)

        log_file.close()

        self.out_print = (self.in_manager_log +
                            self.dicom_log +
                            self.Additional_log)

    run = property(_run_process)
##############################################################
#         Dicom De-Identifier Pipeline Definition
##############################################################


class Anonymiser(Pipeline):
    """ Anonymization pipeline for EU-AIMS project

    create de-identified dicom, PSC2 transcoding +  check sequence completion
    """
    def pipeline_definition(self):

        # Create processes
        self.add_process("in_data_manager",
                "caps.dicom_converter.dicom_deidentifier_v2.InputDataManager")
        self.add_process("dicom_deidentifier",
                "caps.dicom_converter.dicom_deidentifier_v2.DicomDeIdentifier")
        self.add_process("add_deidentifier",
                "caps.dicom_converter.dicom_deidentifier_v2.AddDeidentifier")
        self.add_process("logger_writter",
                "caps.dicom_converter.dicom_deidentifier_v2.LoggerWritter")

        # Export inputs
        self.export_parameter("dicom_deidentifier", "converter_path")
        self.export_parameter("dicom_deidentifier", "out_dir_root")
        self.export_parameter("dicom_deidentifier", "log_files")
        self.add_link("out_dir_root->add_deidentifier.out_dir_root")
        self.add_link("log_files->add_deidentifier.log_files")
        self.add_link("log_files->in_data_manager.log_path")
        self.add_link("log_files->logger_writter.batch_log_loc")
        self.add_link("converter_path->add_deidentifier.converter_path")
        self.export_parameter("in_data_manager", "root_dir")

        # Link input DataManager
        self.add_link("in_data_manager.meta_infos->"
                      "dicom_deidentifier.meta_infos")
        self.add_link("in_data_manager.meta_infos->"
                      "add_deidentifier.meta_infos")
        self.add_link("in_data_manager.log->"
                      "logger_writter.in_manager_log")

        # Link dicom_deidentifier
        self.add_link("dicom_deidentifier.log->"
                        "logger_writter.dicom_log")

        # Link add_deidentifier
        self.add_link("add_deidentifier.log->"
                        "logger_writter.Additional_log")

        # Export outputs
        self.export_parameter("logger_writter", "out_print")

        #set default parameters:
        self.nodes["dicom_deidentifier"].process.remove_curves = True
        self.nodes["dicom_deidentifier"].process.remove_private_tags = False
        self.nodes["dicom_deidentifier"].process.remove_overlays = True
        self.nodes["dicom_deidentifier"].process.use_sop_instance_uid = False
        self.nodes["dicom_deidentifier"].process.no_dicom_marker = False

##############################################################
#                     Pilot
##############################################################


def pilot(working_dir="/volatile/nsap/casper",
          **kwargs):
    """
    Packages De-identifier tool for EU-AIMS project

    .. topic:: Objective

        This pipeline is an essential part of pre-processing.
        It processes the data in 4 steps:
        Start: Raw PSC1 data acquired from DAC (unzipped)
        1) read and anonymize dicoms, write new PSC2-encoded dicoms
        in output folder (template matching), all dicoms in "Images" fodler
        2) Detect different series, compute standard name, create and fill
        serie folders in "Images"
        3) Check serie completion: all slices must be here in order to
        compute a nice nifti file
        4) write logs corresponding to this procedure
        End: PSC2 encoded package, ready for nifti generation and exposition

    Import
    ------

    load the class to configure the study we want to
    perform
    """
    from capsul.study_config import StudyConfig

    """
    Here two utility tools are loaded. It enables the creation
    of ordered dictionary
    """
    from capsul.utils.sorted_dictionary import SortedDictionary

    """
    We then define the Anonymiser
    """
    Anonymizer_pipeline = Anonymiser()

    """
    It is possible to access the pipeline input specification.
    """
    print(Anonymizer_pipeline.get_input_spec())

    """
    Will return the input parameters the user can set:

    .. code-block:: python

        INPUT SPECIFICATIONS

        converter_path: ['String']
        out_dir_root: ['String']
        log_files: ['String']
        root_dir: ['String']

    We can now tune the pipeline parameters.
    """
    # Initialize pipeline
    Anonymizer_pipeline.converter_path = "/neurospin/eu-aims/extra_info/PSC_and_centers/PSC1#PSC2.txt"
    Anonymizer_pipeline.out_dir_root = "/volatile/TEST/PSC2"
    Anonymizer_pipeline.log_files = "/volatile/TEST/LOGS"
    Anonymizer_pipeline.root_dir = "/volatile/TEST/PSC1"

    ensure_is_dir(os.path.join(working_dir, "de_identifier"))

    """
    Study Configuration
    -------------------

    For a complete description of a study configuration, see the
    :ref:`Study Configuration description <study_configuration_guide>`
    """
    default_config = SortedDictionary(
        ("output_directory", os.path.join(working_dir, "de_identifier")),
        ("use_smart_caching", False),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)

    """
    The pipeline is now ready to be run
    """
    study.run(Anonymizer_pipeline)

    """
    Results
    -------

    Finally, we print the pipeline outputs
    """
    print "\nOUTPUTS\n"
    for trait_name, trait_value in Anonymizer_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()