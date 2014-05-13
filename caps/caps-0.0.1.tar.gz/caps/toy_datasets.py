#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import urllib
import urllib2
import time
import logging
import os
import shutil
import numpy
import sys
import hashlib
import curses
import tarfile
import zipfile
import gzip
import tarfile


def Enum(**enums):
    """ Generate an enum structure
    """
    enums["items"] = enums.items()
    return type("Enum", (), enums)


SAMPLE_DATE_FILES = {
    "fa_1mm": Enum(
        template=("fsl_dir", "data/standard/FMRIB58_FA_1mm.nii.gz",
                  "a6f9a5222f64eff5f61b21b5e6e1c67d"),
        nl_config=("fsl_dir", "etc/flirtsch/FA_2_FMRIB58_1mm.cnf",
                   "c1fcda805d0feedf68894ac7f494410d")),
    "mni_1mm": Enum(
        mni=("fsl_dir", "data/standard/MNI152_T1_1mm.nii.gz",
             "fdd164e97d9d576aea4b83b8317489ed"),
        brain=("fsl_dir", "data/standard/MNI152_T1_1mm_brain.nii.gz",
               "7c47f203858f57c50ee93bcf7b0662fc"),
        mask=("fsl_dir", "data/standard/MNI152_T1_1mm_brain_mask.nii.gz",
              "47b8c7f50533688494aa44ff22d5f988"),
        mesh=("nsap_url", "MNI152_T1_1mm_Bothhemi.gii",
              "67a0af59da5fa7c6ff16358db606566a"),
        erode_mesh=("nsap_url", "MNI152_T1_1mm_Bothwhite.gii",
                    "0b0aebcabfd9a5ebb1189d56298cb0e0")),
    "mni_2mm": Enum(
        mni=("fsl_dir", "data/standard/MNI152_T1_2mm.nii.gz",
             "457b2df45e806b35f64f11a98e6b459b"),
        brain=("fsl_dir", "data/standard/MNI152_T1_2mm_brain.nii.gz",
               "2b2769d1795711c1e040827a4a62433d"),
        mask=("fsl_dir", "data/standard/MNI152_T1_2mm_brain_mask.nii.gz",
              "84cd8269e63867f77249c4a8967adaf6")),
    "spm_auditory": Enum(
        fmri=("nsap_url", "spm_auditory_fmri_data.nii.gz",
              "90b37996c31a9c6ff7101a4cc380e2aa"),
        anat=("nsap_url", "spm_auditory_t1.nii.gz",
              "a6cd202f033433b6184066ef8da77d5b"),
        TR=7,
        timings=("nsap_url", "spm_auditory_timings.txt",
                 "eaf1d1d0f3245ddbda912823e286567a")),
    "tpm": Enum(
        all=("spm_dir", "toolbox/Seg/TPM.nii",
             "9f7b044ae53708f43887505ab6551024"),
        gm=("spm_dir", "tpm/grey.nii",
            "331edb3340587dc8ba427eb08badc23f"),
        wm=("spm_dir", "tpm/white.nii",
            "46e18b2fe947457b52bdd69573853692"),
        csf=("spm_dir", "tpm/csf.nii",
             "861f7bba117a504ee5e4291a065d929d")),
    "localizer": Enum(
        fmri=("nsap_url", "fmri_localizer.nii.gz",
              "9457918182ef66e5d5b9473fe7d1d1b7"),
        anat=("nsap_url", "t1_localizer.nii.gz",
              "9617b36e5510a4783038c63241da21d4"),
        mean=("nsap_url", "mean_fmri_localizer.nii.gz",
              "2aa39900027e3ff89f0d66804521e153"),
        TR=2.4,
        timings=("nsap_url", "localizer_timings.txt",
                 "c5f10b621fbb3ca689ad9fe41a7dc9a6"),
        fmridcm=("nsap_url", "func.tar.gz",
                 "0de40a9970e5b7f3f02b62db6f18f417"),
        anatdcm=("nsap_url", "anat.tar.gz",
                 "2aa880e13a746cd66f88ba56d053b063")),
    "dwi": Enum(
        dwi=("nsap_url", "DTI30s010.nii",
             "220f069c259fd0323953dd13817e7ea6"),
        bvecs=("nsap_url", "DTI30s010.bvec",
               "0f801f03f15cd3e5d20609975661f957"),
        bvals=("nsap_url", "DTI30s010.bval",
               "98ff765baacda3b6ae3d4f0b06360bb5"),
        fa=("nsap_url", "DTI30s010_fa.nii.gz",
            "9e31f6306d0e616e9a0c0e5e5e892238"),
        mask=("nsap_url", "DTI30s010_mask.nii.gz",
              "4cd58aeec91003af8a4d040494922140"),
        tensor=("nsap_url", "DTI30s010_tensor2.nii.gz",
                "b2bc7f7fc0e196b227c758429f263dcc")),
    "brainvisa_palette": Enum(
        edouard=("nsap_url", "palette_signed_values_blackcenter.tiff",
                 "346250964d6661bd14c1128f78aa7847"))
}


def uncompress_file(fname, delete_archive=False):
    """Uncompress files contained in a data_set.

    Parameters
    ----------
    fname: str (mandatory)
        path of file to be uncompressed.

    delete_archive: bool (optional)
        option to delete the archive once it is uncompressed.

    Returns
    -------
    out: str
        the path to the uncompressed object

    Notes
    -----
    The function handles zip, tar, gzip and bzip files only.
    """
    logging.info("Extracting data from {0}...".format(fname))
    # First check if the file has already been uncompressed
    out, ext = os.path.splitext(fname)
    if ext == ".gz":
        out, _ = os.path.splitext(out)
    if os.path.isdir(out) or os.path.isfile(out):
        return out
    # Uncompress in the same directory
    data_dir = os.path.dirname(fname)
    # Try to uncompress
    try:
        # Raise an exception if this parameter is false at the end
        processed = False
        # Parameter for .gz archive
        is_gz = 0
        # Get the file extension
        filename, ext = os.path.splitext(fname)
        # If zip file
        if ext == ".zip":
            z = zipfile.ZipFile(fname)
            z.extractall(data_dir)
            z.close()
            processed = True
        # If gzip file
        elif ext == ".gz":
            gz = gzip.open(fname)
            out = open(filename, "wb")
            shutil.copyfileobj(gz, out, 8192)
            gz.close()
            out.close()
            # Delete archive if required
            if delete_archive:
                os.remove(fname)
            fname = filename
            filename, ext = os.path.splitext(fname)
            processed = True
            is_gz += 1
        # If tar or bzip file
        if ext in [".tar", ".tgz", ".bz2"]:
            tar = tarfile.open(fname, "r")
            tar.extractall(path=data_dir)
            tar.close()
            processed += 1
            is_gz += 1
        if not processed:
            raise IOError("Uncompress: unknown file extension: "
                          "{0}".format(ext))
        # Delete archive if required
        if delete_archive or (is_gz == 2):
            os.remove(fname)

        logging.info("...done.")
    except Exception as e:
        raise Exception("Error uncompressing file: {0}".format(e))

    return filename


def get_sample_data(dataset_name, fsl_dir="/usr/share/fsl/4.1",
                    spm_dir="/i2bm/local/spm8-5236/"):
    """ Get a sample dataset.

    This function loads the requested dataset, downloading
    it if needed in the '$HOME/.local/share/nsap' directory.
    If a .zip or .tar.gz file is requested, the function automatically
    uncompress the file and return the path to the uncompressed file.

    Parameters
    ----------
    dataset_name: str (mandatory)
        which sample data you want - one of:

        ``mni_1mm`` - (mni, brain,mask, mesh, erode_mesh),
        ``mni_2mm`` - (mni, brain, mask),
        ``spm_auditory`` - (fmri, anat, TR, timings),
        ``tpm`` - (all,gm,wm,csf),
        ``localizer`` - (fmri, anat, TR, timings, mean, fmridcm, anatdcm),
        ``dwi`` - (dwi, bvecs, bvals, fa, mask, tensor),
        ``brainvisa_palette`` - (edouard),
        ``fa_1mm`` - (template, nl_config)

    fsl_dir: str (optional)
        the function will try first to get the fsl path from the 'FSLDIR'
        environment variable. If not found, the fsl directory will be set
        with this parameter.
        Note that the default parameter is only valid for NeuroSpin users.

    spm_dir: str (optional)
        the function will try first to get the spm path from the 'SPMDIR'
        environment variable. If not found, the spm directory will be set
        with this parameter.
        Note that the default parameter is only valid for NeuroSpin users.

    Returns
    -------
    dataset: Enum
        an Enum object containing the path to the desired dataset.

    Examples
    --------
        >>> from caps.toy_datasets import get_sample_data
        >>> dataset = get_sample_data("mni_1mm")
        >>> dataset.mni
            /usr/share/fsl/4.1/data/standard/MNI152_T1_1mm.nii.gz
    """
    # First get the dataset description
    dataset_description = SAMPLE_DATE_FILES.get(dataset_name)
    if dataset_description is None:
        raise Exception(
            "No dataset found for option {0} - allowed keys are {1}".format(
                dataset_name, SAMPLE_DATE_FILES.keys()))

    # Set the default path where the dataset can be found
    nsap_url = "http://nsap.intra.cea.fr/datasets/"
    spm_dir = os.environ.get("SPMDIR", spm_dir)
    fsl_dir = os.environ.get("FSLDIR", fsl_dir)

    # Transform the dataset description
    # Replace file path description with file real location on the disk.
    for cnt, values in enumerate(dataset_description.items):
        key, value = values
        # If tuple -> file decription
        if isinstance(value, tuple):
            # Get the resource on the web
            if value[0] == "nsap_url":
                url = os.path.join(eval(value[0]), value[1])
                local_fname = download_file(url, resume=True, overwrite=False,
                                            md5sum=value[2])
            # Resource already on the disk
            else:
                local_fname = os.path.join(eval(value[0]), value[1])
                if not os.path.isfile(local_fname):
                    raise Exception("Uknown local file '{0}'. The '{1}' "
                                    "directory resource may not be "
                                    "valid.".format(local_fname, value[0]))

            # Check if a valid fill has been found
            md5sum = value[2]
            if md5sum is not None:
                if (md5_sum_file(local_fname) != md5sum):
                    raise ValueError("File {0} checksum verification has "
                                     "failed. Dataset importation "
                                     "aborted.".format(local_fname))
                else:
                    logging.info("The imported file is valid "
                                 "(md5 sum check).")

            # Uncompress archive
            filename, ext = os.path.splitext(local_fname)
            if local_fname.endswith((".zip", "tar.gz", ".tgz", ".bz2")):
                local_fname = uncompress_file(local_fname)

            # Update the enum structure
            dataset_description.items[cnt] = (key, local_fname)
            expression = "dataset_description.{0} = '{1}'".format(key,
                                                                  local_fname)
            namespace = {"dataset_description": dataset_description}
            exec expression in namespace

    return dataset_description


def md5_sum_file(fname):
    """ Calculates the MD5 sum of a file.

    Parameters
    ----------
    fname: str (mandatory)
        the path to a file

    Returns
    -------
    md5: int
        the md5 sum of the input file
    """
    f = open(fname, 'rb')
    m = hashlib.md5()
    while True:
        data = f.read(8192)
        if not data:
            break
        m.update(data)
    return m.hexdigest()


def progress_bar(window, ratio, fname=None, bar_length=20):
    """ Generate a progress bar

    Parameters
    ----------
    ratio: float (mandatory)
        the progress status (0<=ratio<1)
    fname: str (optional)
        the name of the file beeing dowloaded
    bar_length: int (optional)
        the size of the progress bar
    """
    progress = int(ratio * 100.)
    block = int(round(bar_length * ratio))
    text = "Download '{0}' in progress: [{1}]{2: 4d}%".format(
        fname or "?", "=" * block + " " * (bar_length - block), progress)
    window.addstr(1, 0, text)
    window.refresh()


class ResumeURLOpener(object, urllib.FancyURLopener):
    """Create sub-class in order to overide error 206. This error means a
    partial file is being sent, which is fine in this case.
    Do nothing with this error.

    Note
    ----
    This was adapted from:
    http://code.activestate.com/recipes/83208-resuming-download-of-a-file/
    """
    def __init__(self):
        pass

    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass


def download_file(url, data_dir=None, resume=True, overwrite=False,
                  md5sum=None):
    """ Load requested file, downloading it if needed or requested.

    Parameters
    ----------
    url: str (mandatory)
        the url of the file to be downloaded.

    data_dir: str (optional)
        path of the data directory.
        default is '$HOME/.local/share/nsap'

    resume: bool (optional)
        if true, try to resume partially downloaded files

    overwrite: bool (optional)
        if true and file already exists, delete it.

    md5sum: str (optional)
        check if the downloaded file has this MD5 sum.

    Returns
    -------
    file: str
        absolute path of downloaded file.

    Notes
    -----
    If, for any reason, the download procedure fails, all downloaded files are
    removed.
    """
    # Create the default data directory
    if data_dir is None:
        home = os.path.expanduser("~")
        data_dir = os.path.join(home, ".local", "share", "nsap")

    # Create the download directory if necessary
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Determine filename using URL
    parse = urllib2.urlparse.urlparse(url)
    fname = os.path.basename(parse.path)

    # Generate the download file name
    download_fname = os.path.join(data_dir, fname)

    # Generate a temporary file for the download
    temp_fname = os.path.join(data_dir, fname + ".part")

    # If the file is already created remove it if the overwrite option is set
    # or return the file
    if os.path.exists(download_fname):
        if overwrite:
            os.remove(download_fname)
        else:
            return download_fname

    # If the temporary file is already created remove it if the overwrite
    # option is set
    if os.path.exists(temp_fname):
        if overwrite:
            os.remove(temp_fname)

    # Start a timer to evaluate the download time
    t0 = time.time()

    # Start downloading dataset
    local_file = None
    bytes_so_far = 0
    try:
        # Prepare the download
        logging.info("Downloading data from {0}...".format(url))
        # Case 1: continue the downloading from an existing temporary file
        if resume and os.path.exists(temp_fname):
            url_opener = ResumeURLOpener()
            # Download has been interrupted, we try to resume it.
            local_file_size = os.path.getsize(temp_fname)
            # If the file exists, then only download the remainder
            url_opener.addheader("Range", "bytes={0}-".format(local_file_size))
            try:
                data = url_opener.open(url)
            except urllib2.HTTPError:
                # There is a problem that may be due to resuming
                # Restart the downloading from scratch
                return download_file(url, data_dir, resume=False,
                                     overwrite=False)
            local_file = open(temp_fname, "ab")
            bytes_so_far = local_file_size
        # Case 2: just download the file
        else:
            data = urllib2.urlopen(url)
            local_file = open(temp_fname, "wb")
        # Get the total file size
        try:
            total_size = data.info().getheader("Content-Length").strip()
            total_size = int(total_size) + bytes_so_far
        except Exception, e:
            logging.error("Total size could not be determined.")
            total_size = "?"

        # Download data
        chunk_size = 8192
        window = curses.initscr()
        while True:
            # Read chunk
            chunk = data.read(chunk_size)
            # Stoping criterion
            if not chunk:
                break
            # Write to local file
            bytes_so_far += len(chunk)
            local_file.write(chunk)
            # Write report status and print a progress bar
            if isinstance(total_size, int):
                ratio = float(bytes_so_far) / float(total_size)
            else:
                ratio = 0
            status = r"{0}  [{1: .2f}%]".format(bytes_so_far, ratio * 100.)
            status = status + chr(8) * (len(status) + 1)
            logging.info(status)
            progress_bar(window, ratio, url)
        curses.endwin()

        # Temporary file must be closed prior to the move
        if not local_file.closed:
            local_file.close()
        shutil.move(temp_fname, download_fname)

        # Get process duration and print it
        dt = time.time() - t0
        exit_message = ("... '{0}'download done in {0} minutes, {1: .2f} "
                        "seconds").format(url, int(numpy.floor(dt / 60)),
                                          dt % 60)
        logging.info(exit_message)
        sys.stdout.write(exit_message + "\n")
    except urllib2.HTTPError, e:
        raise Exception("{0}\nError while downloading file '{1}'. "
                        "Dataset download aborted.".format(e, fname))
    except urllib2.URLError, e:
        raise Exception("{0}\nError while downloading file '{1}'. "
                        "Dataset download aborted.".format(e, fname))
    finally:
        # Temporary file must be closed
        if local_file is not None:
            if not local_file.closed:
                local_file.close()

    # md5 check sum
    if md5sum is not None:
        if (md5_sum_file(download_fname) != md5sum):
            raise ValueError("File {0} checksum verification has failed. "
                             "Dataset download aborted.".format(local_file))
        else:
            logging.info("The downloaded file is valid (md5 sum check).")

    return download_fname


if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.ERROR)

    for dataset_name in SAMPLE_DATE_FILES:
        print "\n", dataset_name, ":"
        dataset = get_sample_data(dataset_name)
        print dataset.items
