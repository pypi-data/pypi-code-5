#! /usr/bin/env python
##########################################################################
# DICOM - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os
import sys
import tarfile
import dicom
import shutil
import logging
from csa2 import parse_csa
import numpy
import json
import string
from dicom.values import converters, convert_UN


def decode(attribute):
    """Decode DICOM attributes from ISO_IR 100.

    DICOM headers are routinely encoded with ISO_IR 100 which is
    equivalent to IS0 8859-1.

    We currently expect all our DICOM headers to be encoded using
    ISO_IR 100. In this context DICOM string attributes returned
    by pydicom are 8-bit strings encoded with ISO_IR 100.

    Parameters
    ----------
    attribute  : str
        The 8-bit string to decode from ISO_IR 100.

    Returns
    -------
    unicode
        The decoded string.

    """
    return attribute.decode('latin_1')


_ILLEGAL_CHARACTERS = u'\\/:*?"<>|_ \t\r\n\0'
_CLEANUP_TABLE = dict((ord(char), u'-') for char in _ILLEGAL_CHARACTERS)


def cleanup(attribute):
    """Get rid of illegal characters in DICOM attributes.

    Replace characters that are illegal in pathnames.
    - Windows reserved characters
    - '_' since it is reserved by Brainvisa
    - spaces, tab, newline and null character

    Parameters
    ----------
    attribute  : unicode
        Decoded string.

    Returns
    -------
    unicode
        String with illegal characters replaced.

    """
    return attribute.translate(_CLEANUP_TABLE)


def copy_flatten_tree(src_dir, dest_dir):
    for root, dirs, files in os.walk(src_dir):
        prefix = os.path.basename(root)
        for fname in files:
            if not (fname.startswith(("PS_", "XX_"))):
                src_file = os.path.join(root, fname)
                dest_file = os.path.join(dest_dir, prefix + "_" + fname)
                shutil.copy(src_file, dest_file)


def save_dict_in_json(dictionnary, out_file_name):
    """ Save meta information in json format
    """
    json_struct = unicode(json.dumps(dictionnary, indent=4))
    f = open(out_file_name, 'w')
    print >> f, json_struct
    f.close()


def load_json_as_dict(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data


def start_logging(name="dicom", level=logging.INFO, logfile=None):

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logfile:
        handler = logging.FileHandler(logfile)
        handler.setLevel(logging.WARN)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.debug('start logging to file: ' + logfile)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.debug('start logging to stderr')

    return logger


def ensure_is_dir(d, clear_dir=False):
    """ If the directory doesn't exist, use os.makedirs """
    if not os.path.exists(d):
        os.makedirs(d)
    elif clear_dir:
        shutil.rmtree(d)
        os.makedirs(d)


def progress_bar(ratio, bar_length=20):
    progress = int(ratio * 100.)
    block = int(round(bar_length * ratio))
    text = "\rProgress: [{0}] {1}%".format("=" * block +
           " " * (bar_length - block), progress)
    sys.stdout.write(text)
    sys.stdout.flush()


def de_targz(source_tar, output_dir):
    tar_open = tarfile.open(source_tar)
    tar_open.extractall(path=output_dir)
    tar_open.close()


def make_targz(source_dir, output_filename=None):
    """ Create a compressed tar (.tar.gz) archieve.

    Parameters
    ----------
    source_dir: directory (mandatory)
        a valid directory.
    output_filename: file
        a file name. If None, the output is generate in source_dir directory
        with the same name.
    """

    if not os.path.isdir(source_dir):
        raise Exception("{0} is not a valid directory.".format(source_dir))

    if not output_filename:
        fname = os.path.basename(os.path.normpath(source_dir)) + ".tar.gz"
        output_filename = os.path.join(os.path.dirname(source_dir), fname)

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def is_valid_dicom_file(dicom_file, force):

    #filtering text files that are mixed with dicom files :
    #they are supposed to be full of digits whereas dicom files are not
    #if proportion of digits is higher that 30%, the file is eliminated
    #test added for PARIS
    dicom_text = open(dicom_file).read()
    digit_char = ''.join(c for c in dicom_text if c.isdigit())
    rate = float(len(digit_char)) / float(len(dicom_text))

    if rate > 0.3:
        return False
    else:

        try:
            dataset = dicom.read_file(dicom_file, force=force)
            return True
        except:
            return False


def rename_dicom_dir(dicom_dir, no_dicom_marker=False):
    dicom_file = os.path.join(dicom_dir, os.listdir(dicom_dir)[0])
    dataset = dicom.read_file(dicom_file, force=no_dicom_marker)

    if (0x0008, 0x103e) in dataset:
        SeriesDescription = cleanup(decode(dataset[0x0008, 0x103e].value))
    else:
        SeriesDescription = None
    SeriesNumber = dataset[0x0020, 0x0011].value

    if SeriesDescription:
        serie_name = SeriesDescription + "_" + str(SeriesNumber).rjust(6, '0')
    else:
        serie_name = str(SeriesNumber).rjust(6, '0')

    new_dicom_dir = os.path.join(os.path.dirname
                    (dicom_dir), "SessionA", serie_name)
    ensure_is_dir(os.path.dirname(new_dicom_dir))
    #check that destination dicom dir is unisuqe
    #new_dicom_dir = add_prefix_dicom_dir(new_dicom_dir)
    if not os.path.isdir(new_dicom_dir):
        os.rename(dicom_dir, new_dicom_dir)
    else:
        shutil.rmtree(dicom_dir)


def add_prefix_dicom_dir(dicom_dir, prefix=None):
    prefix = prefix or ""
    new_dicom_dir = os.path.join(os.path.dirname(dicom_dir),
                                 prefix + os.path.basename(dicom_dir))
    if os.path.isdir(new_dicom_dir):
        return add_prefix_dicom_dir(dicom_dir, prefix + "b")
    else:
        return new_dicom_dir


def anonymized_serie(in_folder, out_folder, new_uid,
                     log_base_name="anony_dcm", generate_log=True,
                     fill_public_diffusion_tags=False,
                     log_output_dir=None, no_dicom_marker=False):

    # at least one file in folder
    if len(os.listdir(in_folder)) > 0:
        # init output dicom directory
        ensure_is_dir(out_folder, True)

        # list all the dicom
        to_treat_dicom = [os.path.join(in_folder, x)
                          for x in os.listdir(in_folder)
                          if (os.path.isfile(os.path.join(in_folder, x)) and
                              not x.startswith(("PS_", "XX_")) and
                              not x.endswith(("docx")))]

        # loop over dicom files
        nb_dicom_files = float(len(to_treat_dicom))
        for cnt, dicom_file in enumerate(to_treat_dicom):
            progress_bar(float(cnt) / nb_dicom_files)
            file_name = "IMAGEN_{0}_{1}.dcm".format(new_uid, cnt)
            output_dicom_file = os.path.join(out_folder, file_name)
            # test if it's a valid DICOM file
            if is_valid_dicom_file(dicom_file, force=no_dicom_marker):
                log = anonymize_dicom(dicom_file, output_dicom_file, new_uid,
                                      use_sop_instance_uid=True,
                                      no_dicom_marker=no_dicom_marker,
                                      fill_public_diffusion_tags=fill_public_diffusion_tags)
                if generate_log:
                    if not log_output_dir:
                        log_output_dir = os.path.join(out_folder, "log")
                    ensure_is_dir(log_output_dir)
                    file_name = os.path.splitext(os.path.basename
                                                    (dicom_file))[0]
                    log_file = os.path.join(log_output_dir,
                                log_base_name + "_{0}.json".format(file_name))
                    save_dict_in_json(log, log_file)
        return 1
    # empty folder
    else:
        return 0


def copy_serie(in_folder, out_folder, new_uid, no_dicom_marker=True):

    # at least one file in folder
    if len(os.listdir(in_folder)) > 0:
        # init output dicom directory
        ensure_is_dir(out_folder, True)

        # list all the dicom
        to_treat_dicom = [os.path.join(in_folder, x)
                          for x in os.listdir(in_folder)
                          if (os.path.isfile(os.path.join(in_folder, x)) and
                              not x.startswith(("PS_", "XX_")))]

        nb_dicom_files = float(len(to_treat_dicom))
        # loop over dicom files
        for cnt, dicom_file in enumerate(to_treat_dicom):
            progress_bar(float(cnt) / nb_dicom_files)
            file_name = "IMAGEN_{0}_{1}.dcm".format(new_uid, cnt)
            output_dicom_file = os.path.join(out_folder, file_name)
            if is_valid_dicom_file(dicom_file, force=no_dicom_marker):
                shutil.copyfile(dicom_file, output_dicom_file)

        return 1
    # empty folder
    else:
        return 0

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


def anonymize_dicom(inpath, savePath, new_uid="anonymous",
                    remove_curves=True, remove_private_tags=True,
                    remove_overlays=True,
                    fill_public_diffusion_tags=False,
                    use_sop_instance_uid=False,
                    no_dicom_marker=False):

    """ Function to anonymize DICOM

        * ALL Overlay tags

    .. note::
        Fields are removed (not emptyed) using their tag names
        All private tags are removed too

        DIFFUSION INFORMATION:
        If public diffusion field present in dataset, they are supposed to be
        filled with the correct information. If not, diffusion information may
        be contained in private field. This function recover b_value and
        g_vector from private fields and fill the corresponding public field.
        These private fields are NOT erased

    Parameters
    ----------
    inpath : file (mandatory)
        file to be processed
    savePath : folder (mandatory)
        folder to fill with ananymized files
    Returns
    -------
    outputs : non
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
            dictionary_patient_name[repr(data_element.tag)] = repr(data_element.value)
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
            dictionary_removed_private[repr(data_element.tag)] = repr(data_element.value)
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
            dictionary_removed_public[repr(data_element.tag)] = repr(data_element.value)
            dataset[data_element.tag].value = ""

    # Load the dicom dataset
    dataset = dicom.read_file(inpath, force=no_dicom_marker)

    # Remove patient name and any other person names
    walk(dataset, PN_callback)

    # Remove 0040 fields group
    walk(dataset, fields40_callback)

    # Change ID
    dataset.PatientID = new_uid

    # Remove data elements in dicom_tag_to_remove
    for tag_name, tag in dicom_tag_to_remove.iteritems():
        if tag_name in dataset:
            dictionary_removed_public[repr(tag)] = repr(dataset.data_element(tag_name).value)
            delattr(dataset, tag_name)

    # Blank data elements in dicom_tag_to_blank
    for tag_name, tag in dicom_tag_to_blank.iteritems():
        if tag_name in dataset:
            dictionary_blank_public[repr(tag)] = repr(dataset.data_element(tag_name).value)
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
        savePath = os.path.join(os.path.dirname(savePath),
                                                SOPInstanceUID + '.dcm')

    dataset.save_as(savePath)
    return dictionary_index


def fill_dataset_diffusion_public_elements(dataset):
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
            print b_vector
            print b_value
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
