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
import shutil
import string
import logging
import dicom
from tools import progress_bar, ensure_is_dir


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


def split_series(dicom_dir, logger_name="dicom"):
    logger = logging.getLogger(logger_name)
    logger.info('SPLIT SERIES')
    # read incoming directory
    # process each file in this directory and its sub-directories
    # expect each file to be a DICOM file
    to_treat_dicom = [os.path.join(dicom_dir, x)
                      for x in os.listdir(dicom_dir)
                      if os.path.isfile(os.path.join(dicom_dir, x))]
    nb_of_files = float(len(to_treat_dicom))
    for cnt, dicom_file in enumerate(to_treat_dicom):
        progress_bar(float(cnt) / nb_of_files)

        logger.debug('computing incoming dicom file: {0}'.format(dicom_file))

        # get the time of last modification
        logger.debug('getting time of last modification')
        mtime = os.path.getmtime(dicom_file)

        # read DICOM dataset
        logger.debug('reading DICOM attributes')
        dataset = dicom.read_file(dicom_file)

        # find character encoding of DICOM attributes
        # we currently expect encoding to be ISO_IR 100
        SpecificCharacterSet = dataset[0x0008, 0x0005].value
        if SpecificCharacterSet != 'ISO_IR 100':
            logger.error('file encoding is not ISO_IR 100 as expected')
            continue

        # process other DICOM attributes
        # decode strings assuming 'ISO_IR 100'
        SOPInstanceUID = dataset[0x0008, 0x0018].value
        if (0x0008, 0x0080) in dataset:
            InstitutionName = dataset[0x0008, 0x0080].value
        else:
            InstitutionName = None
        if (0x0008, 0x103e) in dataset:
            SeriesDescription = cleanup(decode(dataset[0x0008, 0x103e].value))
        else:
            SeriesDescription = None
#        ManufacturerModelName = dataset[0x0008, 0x1090].value
#        PatientID = cleanup(decode(dataset[0x0010, 0x0020].value))
#        StudyID = dataset[0x0020, 0x0010].value
        SeriesNumber = dataset[0x0020, 0x0011].value

        # build the full path to the outgoing directory
        # we assume that tjer is only one session
        if SeriesDescription:
            serie_name = SeriesDescription + "_" + str(SeriesNumber).rjust(6, '0')
        else:
            serie_name = str(SeriesNumber).rjust(6, '0')
        output_dicom_dir = os.path.join(dicom_dir, "SessionA", serie_name)

        # build a new name for the DICOM file
        output_dicom_file = os.path.join(output_dicom_dir,
                                         SOPInstanceUID + '.dcm')
        # we intend to move the DICOM file to this path
        logger.debug('DICOM file will be moved to: {0}'.format(output_dicom_file))

        # move DICOM file
        # handle case where outgoing file already exists
        if os.path.exists(output_dicom_file):
            logger.warn('outgoing file already exists: {0}'.format(output_dicom_file))

            # compare SOPInstanceUIDs - they have to be identical!
            dataset = dicom.read_file(output_dicom_file)
            if SOPInstanceUID != dataset[0x0008, 0x0018].value:
                logger.error('outgoing file has different SOPInstanceUID,'
                             'keeping incoming file: {0}'.format(inrelpath))
                os.remove(output_dicom_file)
                os.rename(dicom_file, output_dicom_file)

            # compare modification time and keep the most recent file
            if os.path.getmtime(output_dicom_file) < mtime:
                logger.warn('overwriting outgoing file with incoming '
                            'file: {0}'.format(inrelpath))
                os.remove(output_dicom_file)
                os.rename(dicom_file, output_dicom_file)
            else:
                logger.warn('outgoing file is more recent, '
                            'discarding incoming file')

        else:
            logger.debug('DICOM file being moved to: {0}'.format(output_dicom_file))
            ensure_is_dir(os.path.dirname(output_dicom_file))
            os.rename(dicom_file, output_dicom_file)
