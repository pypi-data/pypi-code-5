#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import gzip


def ungzip_image(input_image, output_directory, suffix="u"):
    """ Copy and ungzip the input files in the
    destination folder.
    """
    if os.path.isfile(input_image):

        base, extension = os.path.splitext(input_image)
        basename = os.path.basename(base)
        if extension in [".gz", ]:
            basename.replace(extension, "")
        basename = suffix + basename
        output_image = os.path.join(output_directory, basename)

        gzfobj = gzip.open(input_image, "rb")
        img_data = gzfobj.read()
        gzfobj.close()

        output = open(output_image, "w")
        output.write(img_data)
        output.close()

        return output_image
    else:
        raise Exception("Can't find the input image "
                        "'{0}'".format(input_image))


def gzip_image(input_image, output_directory, suffix="g"):
    """ Gzip the input files in the same folder with the same name.
    """
    if os.path.isfile(input_image):

        base, extension = os.path.splitext(input_image)
        basename = os.path.basename(base)
        # Nothing to do
        if extension in [".gz", ]:
            return input_image
        basename = suffix + basename + extension + ".gz"
        output_image = os.path.join(output_directory, basename)

        img_data = open(input_image, "rb")
        output = gzip.open(output_image, "w")
        output.writelines(img_data)

        output.close()
        img_data.close()

        return output_image
    else:
        raise Exception("Can't find the input image "
                        "'{0}'".format(input_image))
