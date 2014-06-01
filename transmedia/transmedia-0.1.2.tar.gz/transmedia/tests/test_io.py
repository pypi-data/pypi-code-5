#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jonathan Storm <the.jonathan.storm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jstorm'

import io

import transmedia.pcm2png as pcm2png
import transmedia.png2pcm as png2pcm


def test_write_png_produces_file_of_expected_size():
    white = [255, 255, 255]
    black = [0, 0, 0]
    pixel_rows = [black + white + black,
                  white + black + white,
                  black + white + black]

    file = io.BytesIO()
    pcm2png.write_png(pixel_rows, file)
    # Magic number 77: precomputed size of png file
    assert len(file.getvalue()) == 77


def test_write_pcm_produces_file_of_expected_size():
    samples = bytearray.fromhex('ffffe3990012')
    file = io.BytesIO()
    png2pcm.write_pcm(samples, file)
    assert len(file.getvalue()) == len(samples)
