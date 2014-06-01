#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jonathan Storm <the.jonathan.storm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jstorm'

import argparse

import png

import transmedia.encoders as encoders


def png2words(file, encoder=encoders.simple_decode):
    """Given a png file and encoding function, convert png rows to a bytearray.
    This assumes each pixel is 24-bit.

    :param file: png file opened for binary read
    :type file: io.BufferedReader() or io.BytesIO()
    :param encoder: encoding function
    :type encoder: function()

    :return: a bytearray
    :rtype: bytes()
    """
    png_rows = png.Reader(file).read()[2]
    words = bytearray()
    for png_row in png_rows:
        row = png_row.tolist()
        while len(row):
            try:
                r, g, b = row[0:3]
                del row[0:3]
                words += encoder(r, g, b)

            except ValueError:
                break

    return words


def write_pcm(samples, file):
    """Write samples to a pcm file.

    :param samples: a bytearray
    :type samples: bytes()
    :param file: target pcm file
    :type file: io.BufferedReader() or io.BytesIO()

    :return: nothing
    :rtype: None
    """
    file.write(samples)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Transform PNG to PCM')
    parser.add_argument('-i', '--input', help='input PNG file', required=True)
    parser.add_argument('-o', '--output', help='output PCM file', required=True)
    args = parser.parse_args()

    # Encode pcm and write as png
    with open(args.input, 'rb') as png_file:
        pcm_samples = png2words(png_file)

    with open(args.output, 'wb') as pcm_file:
        write_pcm(pcm_samples, pcm_file)
