#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import dicom
#from dicom.values import converters, convert_UN
from caps.dicom_converter.base.csa2 import parse_csa
import numpy
import os
from caps.dicom_converter.base.tools import (ensure_is_dir,
                                             progress_bar,
                                             cleanup,
                                             decode,
                                             save_dict_in_json)

try:
    from traits.api import String, List, Directory, Bool
except ImportError:
    from enthought.traits.api import String, List, Directory, Bool

from capsul.process import Process
from capsul.pipeline import Pipeline

##############################################################
#        Dicom anonymizer Tool Processes
##############################################################


class InputDataManager(Process):
    """
    list dicom files in input folder, check format and PSC transcoding
    return a list of dicom files
    inputs: PSC1 patient code
    dicom folder
    """

    def __init__(self):
        super(InputDataManager, self).__init__()

        # Inputs
        self.add_trait("dicom_dir", Directory(optional=False))
        self.add_trait("psc1", String(optional=False))
        self.add_trait("no_dicom_marker", Bool(optional=True))

        # Outputs
        self.add_trait("dicom_list",
                       List(optional=False, output=True))
        self.add_trait("psc2", String(optional=False, output=True))

    def _run_process(self):
        #get conversion table
        import csv
        psc_table = csv.reader(
            open("/neurospin/imagen/src/scripts/psc_tools/psc2psc.csv", "rb"))
        converter = {}
        psc_table.next()
        for row in psc_table:
            psc = row[0].split("=")
            converter[psc[0]] = psc[2]

        # List valid dicoms images
        dicom_list = []
        if self.psc1 in converter:
            self.psc2 = converter[self.psc1]
        else:
            raise NameError("Unknown PSC1")

        print "LOADING DATASETS"
        tot = float(len(os.listdir(self.dicom_dir)))
        for cnt, dcm in enumerate(os.listdir(self.dicom_dir)):
            if os.path.isfile(os.path.join(self.dicom_dir, dcm)):
                try:
                    ds = dicom.read_file(os.path.join(self.dicom_dir, dcm),
                                    force=self.no_dicom_marker,)
                    fileName = "IMAGEN_{0}_{1}.dcm".format(self.psc2, cnt)
                    dicom_list.append((ds, fileName))
                except:
                    print "not a dicom file : " + os.path.join(
                                                        self.dicom_dir, dcm)
                    print "this file will be ignored"

            else:
                raise NameError("not a file : " + os.path.join(
                                                    self.dicom_dir, dcm) +
                                    " only folder with dicom files accepted")
            progress_bar(float(len(dicom_list)) / tot)
        self.dicom_list = dicom_list
    run = property(_run_process)


class DeIdentifier(Process):
    """
    Dicom de-identification process.
    inputs : list of dicom datasets to anonymize
    de-identification parameters
    generate fileName for each dicom
    """
    def __init__(self):
        super(DeIdentifier, self).__init__()

        # Inputs
        self.add_trait("in_dicom_list", List(optional=False))
        self.add_trait("new_uid", String(optional=False))
        self.add_trait("remove_curves", Bool(optional=True))
        self.add_trait("remove_private_tags", Bool(optional=True))
        self.add_trait("remove_overlays", Bool(optional=True))
        self.add_trait("fill_public_diffusion_tags", Bool(optional=True))
        self.add_trait("use_sop_instance_uid", Bool(optional=True))

        # Outputs
        self.add_trait("anonymized_files", List(optional=False,
                                                    output=True))
        self.add_trait("de_identification_footprints", List(optional=True,
                                                            output=True))

    def _run_process(self):
        anonymized_files = []
        de_identification_footprints = []
        print ""
        print "DE-IDENTIFICATION PROGRESS"
        tot = float(len(self.in_dicom_list))
        for cnt, entry in enumerate(self.in_dicom_list):
            progress_bar(float(cnt + 1) / tot)
            dataset = entry[0]
            filename = entry[1]
            ano_list = anonymize_dicom(dataset, filename,
                self.new_uid,
                fill_public_diffusion_tags=self.fill_public_diffusion_tags,
                remove_curves=self.remove_curves,
                remove_private_tags=self.remove_private_tags,
                remove_overlays=self.remove_overlays,
                use_sop_instance_uid=self.use_sop_instance_uid)
            anonymized_files.append((ano_list[0], ano_list[1]))
            de_identification_footprints.append(ano_list[2])
        self.anonymized_files = anonymized_files
        self.de_identification_footprints = de_identification_footprints
    run = property(_run_process)


class DicomWriter(Process):
    """
    Dicom serie spliter : write datasets as dicom files in separated serie
    folders
    inputs : list of dicom datasets to write
    root folder to fill
    """
    def __init__(self):
        super(DicomWriter, self).__init__()

        # Inputs
        self.add_trait("de_identification_footprints", List([], optional=True))
        self.add_trait("psc2", String(optional=False))
        self.add_trait("root_folder", String(optional=False))
        self.add_trait("save_de_identification_footprints",
                                                       Bool(optional=True))
        self.add_trait("split_series", Bool(optional=False))
        self.add_trait("in_datasets", List(optional=False))

        # Outputs
        self.add_trait("out_folder", String(optional=False,
                                                    output=True))

    def _run_process(self):
        #separate datasets and their names:
        self.out_folder = os.path.join(self.root_folder, self.psc2)
        ensure_is_dir(self.out_folder)
        print ""
        print "WRITING DICOMS"
        filenames = []
        if self.split_series:
            datasets = []
            for cnt, entry in enumerate(self.in_datasets):
                datasets.append(entry[0])
                filenames.append(entry[1])
            split_series(datasets, filenames, self.out_folder)
        else:
            tot = float(len(self.in_datasets))
            for cnt, entry in enumerate(self.in_datasets):
                progress_bar(float(cnt + 1) / tot)
                dataset = entry[0]
                filename = entry[1]
                filenames.append(filename)
                savePath = os.path.join(self.out_folder, filename)
                dataset.save_as(savePath)

        ensure_is_dir(os.path.join(self.root_folder, "LOGS"))
        write_footprints(self.de_identification_footprints,
                         filenames,
                         os.path.join(self.root_folder, "LOGS"),
                        auth=self.save_de_identification_footprints)

    run = property(_run_process)


##############################################################
#         Dicom De-Identifier Pipeline Definition
##############################################################


class Dicom_anonymiser(Pipeline):
    """ Anonymization pipeline
    create de-identified dicom and PSC2 transcoding
    """
    def pipeline_definition(self):

        # Create processes
        self.add_process("in_data_manager",
                "caps.dicom_converter.dicom_deidentifier.InputDataManager")
        self.add_process("de_identifier",
                "caps.dicom_converter.dicom_deidentifier.DeIdentifier")
        self.add_process("dicom_writer",
                "caps.dicom_converter.dicom_deidentifier.DicomWriter")

        #Create switches
        self.add_switch('select_ano', ['ano', 'none'], ['dicom_ano_out', ])

        # Export inputs
        self.export_parameter("in_data_manager", "dicom_dir")
        self.export_parameter("in_data_manager", "psc1")
        self.export_parameter("in_data_manager", "no_dicom_marker")
        self.export_parameter("de_identifier", "remove_curves")
        self.export_parameter("de_identifier", "remove_private_tags")
        self.export_parameter("de_identifier", "remove_overlays")
        self.export_parameter("de_identifier", "fill_public_diffusion_tags")
        self.export_parameter("de_identifier", "use_sop_instance_uid")
        self.export_parameter("dicom_writer", "root_folder")
        self.export_parameter("dicom_writer",
                                      "save_de_identification_footprints")
        self.export_parameter("dicom_writer", "split_series")

        # Link input DataManager
        self.add_link("in_data_manager.dicom_list->"
                      "de_identifier.in_dicom_list")
        self.add_link("in_data_manager.psc2->"
                      "de_identifier.new_uid")

        #Link anonymize switch
        self.add_link("in_data_manager.dicom_list->"
                      "select_ano.none_switch_dicom_ano_out")
        self.add_link("de_identifier.anonymized_files->"
                        "select_ano.ano_switch_dicom_ano_out")

        #link dicom_writer
        self.add_link("select_ano.dicom_ano_out->"
                        "dicom_writer.in_datasets")
        self.add_link("in_data_manager.psc2->"
                        "dicom_writer.psc2")
        self.add_link("de_identifier.de_identification_footprints->"
                        "dicom_writer.de_identification_footprints")

        # Export outputs
        self.export_parameter("dicom_writer", "out_folder")

        #set default parameters:
        self.nodes["de_identifier"].process.remove_curves = True
        self.nodes["de_identifier"].process.remove_private_tags = True
        self.nodes["de_identifier"].process.remove_overlays = True
        self.nodes["de_identifier"].process.fill_public_diffusion_tags = True
        self.nodes["de_identifier"].process.use_sop_instance_uid = False
        self.nodes["de_identifier"].process.save_de_identification_footprints = True
        self.nodes["de_identifier"].process.no_dicom_marker = False

##############################################################
#                     Pilot
##############################################################


def pilot(working_dir="/volatile/nsap/casper",
          **kwargs):
    """ Dicom anonymizer tool
    """
    from capsul.study_config import StudyConfig
    from capsul.utils.sorted_dictionary import SortedDictionary

    # Create
    dicom_anonymizer_pipeline = Dicom_anonymiser()

    # Initialize pipeline
    dicom_anonymizer_pipeline.select_ano = "ano"
    dicom_anonymizer_pipeline.dicom_dir = "/volatile/TEST/DICOM"
    dicom_anonymizer_pipeline.psc1 = "060000125528"
    dicom_anonymizer_pipeline.no_dicom_marker = True
    dicom_anonymizer_pipeline.remove_curves = True
    dicom_anonymizer_pipeline.remove_private_tags = True
    dicom_anonymizer_pipeline.remove_overlays = True
    dicom_anonymizer_pipeline.fill_public_diffusion_tags = True
    dicom_anonymizer_pipeline.use_sop_instance_uid = False
    dicom_anonymizer_pipeline.root_folder = "/volatile/TEST/output_test"
    dicom_anonymizer_pipeline.save_de_identification_footprints = False
    dicom_anonymizer_pipeline.split_series = False

    ensure_is_dir(os.path.join(working_dir, "de_identifier"))
    # Execute the pipeline
    default_config = SortedDictionary(
        ("output_directory", os.path.join(working_dir, "de_identifier")),
        ("use_smart_caching", False),
        ("generate_logging", False)
    )
    study = StudyConfig(default_config)
    study.run(dicom_anonymizer_pipeline)

    # Print all pipeline outputs
    print "\nOUTPUTS\n"
    for trait_name, trait_value in dicom_anonymizer_pipeline.get_outputs().iteritems():
        print "{0}: {1}".format(trait_name, trait_value)


if __name__ == '__main__':
    pilot()

##############################################################
#                     METHODS
##############################################################


def write_footprints(dic, names, path, auth=False):
    """ Write down dicom de-identification dictionaries.
    Dictionaries will have the same name as their corresponding datasets

    inputs :
    dictionary list (mandatory)
    path to save them (mandatory)
    name list of the corresponding datasets (mandatory)
    auth save parameters, if False, logs won't be saved(optional)
    """
    if auth:
        for cnt, dic_unit in enumerate(dic):
            save_dict_in_json(dic_unit,
                              os.path.join(path,
                                           names[cnt] + ".json".format(cnt)))


def anonymize_dicom(dataset, fileName, new_uid="anonymous",
                    remove_curves=True, remove_private_tags=True,
                    remove_overlays=True,
                    fill_public_diffusion_tags=False,
                    use_sop_instance_uid=False):
    """ Function to anonymize DICOM

    * ALL Overlay tags

    .. note::
        
        Some fields (type 2 and 3) are removed, others are emptyed using their
        tag names.
        All private tags are removed too if necessary (parameters)

        DIFFUSION INFORMATION:
        If public diffusion field present in dataset, they are supposed to be
        filled with the correct information. If not, diffusion information may
        be contained in private field. This function recover b_value and
        g_vector from private fields and fill the corresponding public field.
        These private fields are NOT erased

    Parameters
    ----------
    inpath : dataset (mandatory)
        file to be processed
    savePath : folder (mandatory)
        folder to fill with ananymized files
        remove_curves (optional) : remove or not curve fields (default = True)
        remove_overlays (optional) : remove overlay fields (default = True)
        fill_public_diffusion_tags (optional) : get diffusion information from
        private fields and put them in public fields (default = False)
        use_sop_instance_uid (optional) : use SPO uid for name generation
        (defailt = False)
        
    Returns
    -------
    writes anonymized file in the newly created folder
    """

    # create dictionnaries of deleted/erased elements
    dictionary_removed_private = {}
    dictionary_removed_public = {}
    dictionary_blank_public = {}
    dictionary_patient_name = {}
    dictionary_diffusion = {}
    #last dictionary : curve, overlay ... can be in public and private fields
    #walking the wholde dataset to erase them
    dictionary_other = {}

    # change callback to enable strange tag
    def walk(dataset, callback):
        taglist = sorted(dataset.keys())
        for tag in taglist:
            data_elem = dict.__getitem__(dataset, tag)
            if not data_elem.VR in converters.keys() and data_elem.VR != None:
                #print data_elem.VR;
                if data_elem.VR not in converters:
                    converters[data_elem.VR] = convert_UN
            data_element = dataset[tag]
            callback(dataset, data_element)
            if tag in dataset and data_element.VR == "SQ":
                sequence = data_element.value
                for sub_dataset in sequence:
                    walk(sub_dataset, callback)

    # Define call-back functions for the dataset.walk() function
    def PN_callback(dataset, data_element):
        """Called from the dataset "walk" recursive function for all
        data elements."""
        if data_element.VR == "PN":
            dictionary_patient_name[repr(data_element.tag)] = repr(
                                                        data_element.value)
            data_element.value = new_uid

    def curves_callback(dataset, data_element):
        """Called from the dataset "walk" recursive function for
        all data elements."""
        if data_element.tag.group & 0xFF00 == 0x5000:
            dictionary_other[repr(data_element.tag)] = repr(data_element.value)
            del dataset[data_element.tag]

    def private_callback(dataset, data_element):
        """Called from the dataset "walk" recursive function for
        all data elements."""
        if data_element.tag.is_private:
            dictionary_removed_private[repr(data_element.tag)] = repr(
                                                        data_element.value)
            del dataset[data_element.tag]

    def overlay_callback(dataset, data_element):
        """Called from the dataset "walk" recursive function for
        all data elements."""
        if "verlay" in data_element.name:
            dictionary_other[repr(data_element.tag)] = repr(data_element.value)
            del dataset.data_element.tag

    def fields40_callback(dataset, data_element):
        """Called from the dataset "walk" recursive function for
        all data elements."""
        if data_element.tag.group & 0xFF00 == 0x0040:
            dictionary_removed_public[repr(data_element.tag)] = repr(
                                                        data_element.value)
            dataset[data_element.tag].value = ""

    # Remove patient name and any other person names
    walk(dataset, PN_callback)

    # Remove 0040 fields group
    walk(dataset, fields40_callback)

    # Change ID
    dataset.PatientID = new_uid

    # Remove data elements in dicom_tag_to_remove
    for tag_name, tag in dicom_tag_to_remove.iteritems():
        if tag_name in dataset:
            dictionary_removed_public[repr(tag)] = repr(
                                        dataset.data_element(tag_name).value)
            delattr(dataset, tag_name)

    # Blank data elements in dicom_tag_to_blank
    for tag_name, tag in dicom_tag_to_blank.iteritems():
        if tag_name in dataset:
            dictionary_blank_public[repr(tag)] = repr(
                                        dataset.data_element(tag_name).value)
            dataset.data_element(tag_name).value = ""

    # Remove curves
    if remove_curves:
        walk(dataset, curves_callback)

    # Fill public diffusion fields
    if fill_public_diffusion_tags:
        dictionary_diffusion = fill_dataset_diffusion_public_elements(dataset)

    # Remove overlay
    if remove_overlays:
        walk(dataset, overlay_callback)

    # Remove private tags
    if remove_private_tags:
        walk(dataset, private_callback)

    dictionary_index = {'removed_private': dictionary_removed_private,
                        'removed_public': dictionary_removed_public,
                        'blank_public': dictionary_blank_public,
                        'diffusion': dictionary_diffusion,
                        'patient_name': dictionary_patient_name,
                        'misc': dictionary_other}

    #write output
    if use_sop_instance_uid:
        SOPInstanceUID = dataset[0x0008, 0x0018].value
        fileName = SOPInstanceUID

    return [dataset, fileName, dictionary_index]


def fill_dataset_diffusion_public_elements(dataset):
    """
    Get diffusion data from public fields and put it in public fields
    Location of diffusion information depends on manufacturer
    """
    dictionary_diffusion = {}
    # check if it is a diffusion sequence
    if (0x0008, 0x103E) in dataset:
        CodingSchemeVersion = dataset[0x0008, 0x103E].value

    if str(CodingSchemeVersion) in "DTI DWI DIFFUSION":

        # get the manufacturer
        if (0x0008, 0x0070) in dataset:
            Manufacturer = dataset[0x0008, 0x0070].value

            if "SIEMENS" in Manufacturer:
                # Use csa reader
                csa_header = parse_csa(dataset[0x0029, 0x1010])
                b_value = csa_header["B_value"][0]
                b_vector = csa_header["DiffusionGradientDirection"]

                dictionary_diffusion["b_values"] = repr(b_value)
                dictionary_diffusion["b_vectors"] = repr(b_vector)

            elif "GE" in Manufacturer:
                softVersion = dataset[0x0018, 0x1020].value
                softVersion = str(softVersion).split('\\', 1)
                softVersion = softVersion[0]
                scanVersion = dataset[0x0008, 0x1090].value
                if softVersion < 10:
                    raise Exception("GE soft version {0} not "
                                    "supported".format(softVersion))
                if "GENESIS" in scanVersion:
                    raise Exception("GE soft version {0} not "
                                    "supported".format(softVersion))
                else:
                    b_value = dataset[0x0043, 0x1039].value
                    b_value = b_value[0]
                    b_vector = [dataset[0x0019, 0x10bb].value,
                                dataset[0x0019, 0x10bc].value,
                                dataset[0x0019, 0x10bd].value]

                    dictionary_diffusion["b_values"] = repr(b_value)
                    dictionary_diffusion["b_vectors"] = repr(b_vector)

            elif "Philips" in Manufacturer:
                b_value = dataset[0x2001, 0x1003].value
                if not (0x0018, 0x9089) in dataset:
                    if b_value != 0:
                        b_vector = dataset[0x2001, 0x1004].value
                    else:
                        b_vector = [0, 0, 0]
                else:
                    b_vector = dataset[0x0018, 0x9089].value

                dictionary_diffusion["b_values"] = repr(b_value)
                dictionary_diffusion["b_vectors"] = repr(b_vector)

            else:
                raise Exception("Manufacturer {0} not "
                                "supported".format(Manufacturer))

            b_vector = numpy.asarray(b_vector)
            b_vector.shape += (1,)
            if b_value != 0:
                b_matrix = numpy.dot(b_vector, b_vector.T) * b_value
                b_matrix = b_matrix[numpy.triu_indices(3)]
            else:
                b_matrix = [0, ] * 6

        # Create an element to store the b-value
        b_value_element = dicom.dataelem.DataElement(
                                (0x0018, 0x9087),
                                "FD",
                                b_value)
        if not (0x0018, 0x9087) in dataset:
            dataset[0x0018, 0x9087] = b_value_element

        # Create an element to store the diffusion directionality
        if b_value == 0:
            diffusion_directionality_element = dicom.dataelem.DataElement(
                                            (0x0018, 0x9075),
                                            "CS",
                                            "NONE")
        else:
            diffusion_directionality_element = dicom.dataelem.DataElement(
                            (0x0018, 0x9075),
                            "CS",
                            "BMATRIX")
        if not (0x0018, 0x9075) in dataset:
            dataset[0x0018, 0x9075] = diffusion_directionality_element

        # Create an element for the b-vector
        b_vector_element = dicom.dataelem.DataElement(
                    (0x0018, 0x9089),
                    "FD",
                    b_vector.squeeze().tolist())
        if not (0x0018, 0x9089) in dataset:
            dataset[0x0018, 0x9089] = b_vector_element

        # Create en element fo the b-matrix
        for cnt, tag in enumerate([(0x0018, 0x9602), (0x0018, 0x9603),
                        (0x0018, 0x9604), (0x0018, 0x9605),
                        (0x0018, 0x9606), (0x0018, 0x9607)]):
            element = dicom.dataelem.DataElement(
                        tag,
                        "FD",
                        b_matrix[cnt])
            if not tag in dataset:
                dataset[tag] = element

    return dictionary_diffusion


def split_series(datasets, fileNames, out_root):
    """
    write datasets in their corresponding serie folder.
    imputs:
    datasets : set of dataset to proceed
    out_root : root folder to fill
    """
    nb_of_files = float(len(datasets))
    for cnt, dataset in enumerate(datasets):
        progress_bar(float(cnt) / nb_of_files)

        # find character encoding of DICOM attributes
        # we currently expect encoding to be ISO_IR 100
        SpecificCharacterSet = dataset[0x0008, 0x0005].value
        if SpecificCharacterSet != 'ISO_IR 100':
            print('file encoding is not ISO_IR 100 as expected')
            continue

        # process other DICOM attributes
        # decode strings assuming 'ISO_IR 100'
        #SOPInstanceUID = dataset[0x0008, 0x0018].value

        if (0x0008, 0x103e) in dataset:
            SeriesDescription = cleanup(decode(dataset[0x0008, 0x103e].value))
        else:
            SeriesDescription = None

        SeriesNumber = dataset[0x0020, 0x0011].value

        # build the full path to the outgoing directory
        # we assume that there is only one session
        if SeriesDescription:
            serie_name = SeriesDescription + "_" + str(
                                                SeriesNumber).rjust(6, '0')
        else:
            serie_name = str(SeriesNumber).rjust(6, '0')
        output_dicom_dir = os.path.join(out_root, "SessionA", serie_name)

        # build a new name for the DICOM file
        output_dicom_file = os.path.join(output_dicom_dir,
                                         fileNames[cnt] + '.dcm')

        # move DICOM file
        # if outgoing file already exists, override it
        ensure_is_dir(os.path.dirname(output_dicom_file))
        dataset.save_as(output_dicom_file)

##############################################################
#             De-identification dictionaries
##############################################################

# dicom type 3 element: optional
dicom_tag_to_remove = {
    "AcquisitionDate": (0x0008, 0x0022),
    "OperatorsName": (0x0008, 0x1070),
    "PerformingPhysicianName": (0x0008, 0x1050),
    "InstitutionalDepartmentName": (0x0008, 0x1040),
    "PhysiciansOfRecord": (0x0008, 0x1048),
    "PhysiciansOfRecordIdentificationSequence": (0x0008, 0x1049),
    "PerformingPhysicianIdentificationSequence": (0x0008, 0x1052),
    "OperatorIdentificationSequence": (0x0008, 0x1072),
    "ReferringPhysicianAddress": (0x0008, 0x0092),
    "ReferringPhysicianTelephoneNumbers": (0x0008, 0x0094),
    "ReferringPhysicianIdentificationSequence": (0x0008, 0x0096),
    "InstitutionName": (0x0008, 0x0080),
    "InstitutionAddress": (0x0008, 0x0081),
    "InstanceCreationDate": (0x0008, 0x0012),
    "OtherPatientIDs": (0x0010, 0x1000),
    "OtherPatientNames": (0x0010, 0x1001),
    "PatientComments": (0x0010, 0x4000)}

# dicom type 2 element: mandatory but not really usefull
dicom_tag_to_blank = {
    "ClinicalTrialCoordinatingCenterName": (0x0012, 0x0060),
    "PatientIdentityRemoved": (0x0012, 0x0062),
    "ClinicalTrialSubjectReadingID": (0x0012, 0x0042),
    "ClinicalTrialSponsorName": (0x0012, 0x0010),
    "ClinicalTrialSubjectID": (0x0012, 0x0040),
    "ClinicalTrialSiteName": (0x0012, 0x0031),
    "ClinicalTrialSiteID": (0x0012, 0x0030),
    "AdditionalPatientHistory": (0x0010, 0x21B0),
    "PatientReligiousPreference": (0x0010, 0x21F0),
    "ResponsiblePerson": (0x0010, 0x2297),
    "ResponsiblePersonRole": (0x0010, 0x2298),
    "ResponsibleOrganization": (0x0010, 0x2299),
    "BranchOfService": (0x0010, 0x1081),
    "MedicalRecordLocator": (0x0010, 0x1090),
    "MedicalAlerts": (0x0010, 0x2000),
    "Allergies": (0x0010, 0x2110),
    "CountryOfResidence": (0x0010, 0x2150),
    "RegionOfResidence": (0x0010, 0x2152),
    "PatientTelephoneNumber": (0x0010, 0x2154),
    "MilitaryRank": (0x0010, 0x1080),
    "PatientMotherBirthName": (0x0010, 0x1060),
    "PatientAddress": (0x0010, 0x1040),
    "PatientBirthName": (0x0010, 0x1005),
    "IssuerOfPatientID": (0x0010, 0x0021),
    "ReferringPhysicianName": (0x0008, 0x0090),
    "ContentDate": (0x0008, 0x0023),
    "AcquisitionDatetime": (0x0008, 0x002A),
    "SeriesDate": (0x0008, 0x0021),
    "PatientName": (0x0010, 0x0010),
    "StudyDate": (0x0008, 0x0020),
    "PatientBirthDate": (0x0010, 0x0030),
    "StationName": (0x0008, 0x1010)}
