#-*- coding: utf-8 -*-
#
# Copyright © 2014 Jonathan Storm <the.jonathan.storm@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING.WTFPL file for more details.

__author__ = 'jstorm'

import io

import png

import transmedia.pcm2png as pcm2png
import transmedia.png2pcm as png2pcm
import transmedia.encoders as encoders


test_pcm_data = bytearray.fromhex('ffff6d06cb0cc436103c2741895c1f5f4861')
test_png_data = pcm2png.pcm2pixels(io.BytesIO(test_pcm_data), 3,
                                   encoders.simple_encode)


### pcm2pixels tests ###

def check_pcm2pixels_returns_correct_width(correct_width):
    test_pcm_file = io.BytesIO(test_pcm_data)
    rows = pcm2png.pcm2pixels(test_pcm_file, correct_width,
                              encoders.simple_encode)

    byte_depth = 3
    width_top = len(rows[0]) / byte_depth
    width_bottom = len(rows[-1]) / byte_depth

    assert width_top == width_bottom == correct_width, \
        "({} == {} == {}) is false".format(width_top, width_bottom,
                                           correct_width)


def test_pcm2pixels_returns_correct_width():
    for width in (1, 3, 9):  # a single column, a square, a single row
        yield check_pcm2pixels_returns_correct_width, width


def test_pcm2pixels_returns_square():
    correct_dimension = 3  # 3x3 square
    test_pcm_file = io.BytesIO(test_pcm_data)
    rows = pcm2png.pcm2pixels(test_pcm_file, correct_dimension,
                              encoders.simple_encode)

    byte_depth = 3
    width_top = len(rows[0]) / byte_depth
    height = len(rows)

    assert width_top == height == correct_dimension, \
        "({} == {} == {} == {}) is false".format(width_top, height,
                                                 correct_dimension)


def test_pcm2pixels_raises_runtime_error_on_negative_width():
    try:
        negative_width = -1
        file = io.BytesIO(test_pcm_data)
        pcm2png.pcm2pixels(file, negative_width, encoders.simple_encode)

        assert False, "encode_pcm erroneously succeeds on negative width"

    except RuntimeError:
        pass


def test_pcm2pixels_raises_runtime_error_on_zero_width():
    try:
        zero_width = 0
        file = io.BytesIO(test_pcm_data)
        pcm2png.pcm2pixels(file, zero_width, encoders.simple_encode)

        assert False, "encode_pcm erroneously succeeds on zero width"

    except RuntimeError:
        pass


def test_pcm2pixels_returns_max_width_on_excessive_width_input():
    excessive_width = len(test_pcm_data) // 2 + 1  # max width + 1
    test_pcm_file = io.BytesIO(test_pcm_data)
    rows = pcm2png.pcm2pixels(test_pcm_file, excessive_width,
                              encoders.simple_encode)

    byte_depth = 3
    actual_width = len(rows[0]) / byte_depth

    assert actual_width != excessive_width, \
        "{} == {} == {}".format(actual_width, excessive_width)


### png2words tests ###

def test_png2words_returns_correct_length():
    correct_length = len(test_pcm_data)
    test_png_file = io.BytesIO()
    w = png.Writer(len(test_png_data[0]) // 3, len(test_png_data))
    w.write(test_png_file, test_png_data)
    test_png_file.seek(0)
    words = png2pcm.png2words(test_png_file, encoders.simple_decode)
    actual_length = len(words)

    assert actual_length == correct_length, \
        "{} != {}".format(actual_length, correct_length)
