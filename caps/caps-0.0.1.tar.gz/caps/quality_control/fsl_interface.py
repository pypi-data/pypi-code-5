#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os
import shutil
from glob import glob
import warnings

import numpy as np

from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec, Info
from nipype.interfaces.base import (traits, TraitedSpec, OutputMultiPath, File,
                                    InputMultiPath, isdefined, Directory)
from nipype.utils.filemanip import (load_json, save_json, split_filename,
                                fname_presuffix)


#############################################################
#                       Slicer
#############################################################

class SlicerInputSpec(FSLCommandInputSpec):
    in_file = File(exists=True, position=1, argstr='%s', mandatory=True,
                   desc='input volume')
    image_edges = File(exists=True, position=2, argstr='%s',
                       desc='volume to display edge overlay for (useful for checking registration')
    label_slices = traits.Bool(
        position=3, argstr='-L', desc='display slice number',
        usedefault=True, default_value=True)
    colour_map = File(exists=True, position=4, argstr='-l %s',
                      desc='use different colour map from that stored in nifti header')
    intensity_range = traits.Tuple(
        traits.Float, traits.Float, position=5, argstr='-i %.3f %.3f',
        desc='min and max intensities to display')
    threshold_edges = traits.Float(
        position=6, argstr='-e %.3f', desc='use threshold for edges')
    dither_edges = traits.Bool(position=7, argstr='-t',
                               desc='produce semi-transparaent (dithered) edges')
    nearest_neighbour = traits.Bool(position=8, argstr='-n',
                                    desc='use nearest neighbour interpolation for output')
    show_orientation = traits.Bool(
        position=9, argstr='%s', usedefault=True, default_value=True,
        desc='label left-right orientation')
    _xor_options = (
        'single_slice', 'middle_slices', 'all_axial', 'sample_axial')
    single_slice = traits.Enum('x', 'y', 'z', position=10, argstr='-%s',
                               xor=_xor_options, requires=['slice_number'],
                               desc='output picture of single slice in the x, y, or z plane')
    slice_number = traits.Int(
        position=11, argstr='-%d', desc='slice number to save in picture')
    middle_slices = traits.Bool(position=10, argstr='-a', xor=_xor_options,
                                desc='output picture of mid-sagital, axial, and coronal slices')
    all_axial = traits.Bool(
        position=10, argstr='-A', xor=_xor_options, requires=['image_width'],
                            desc='output all axial slices into one picture')
    sample_axial = traits.Int(position=10, argstr='-S %d',
                              xor=_xor_options, requires=['image_width'],
                              desc='output every n axial slices into one picture')
    image_width = traits.Int(
        position=-2, argstr='%d', desc='max picture width')
    out_file = File(position=-1, genfile=False, argstr='%s',
                    desc='picture to write', hash_files=False)
    scaling = traits.Float(position=0, argstr='-s %f', desc='image scale')


class SlicerOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='picture to write')


class Slicer(FSLCommand):
    """Use FSL's slicer command to output a png image from a volume.

Examples
--------
>>> from nipype.interfaces import fsl
>>> from nipype.testing import example_data
>>> slice = fsl.Slicer()
>>> slice.inputs.in_file = example_data('functional.nii')
>>> slice.inputs.all_axial = True
>>> slice.inputs.image_width = 750
>>> res = slice.run() #doctest: +SKIP

"""
    _cmd = 'slicer'
    input_spec = SlicerInputSpec
    output_spec = SlicerOutputSpec

    def _format_arg(self, name, spec, value):
        if name == 'show_orientation':
            if value:
                return ''
            else:
                return '-u'
        elif name == "label_slices":
            if value:
                return '-L'
            else:
                return ''
        #elif name == "out_file":
        #    print "**", value, self.inputs.out_file
        return super(Slicer, self)._format_arg(name, spec, value)

    def _list_outputs(self):
        outputs = self._outputs().get()
        out_file = self.inputs.out_file
        if not isdefined(out_file):
            out_file = self._gen_fname(self.inputs.in_file, ext='.png')
        outputs['out_file'] = os.path.abspath(out_file)
        return outputs

    def _gen_filename(self, name):
        if name == 'out_file':
            return self._list_outputs()['out_file']
        return None

#############################################################
#                       pngappend
#############################################################


class PngAppendInputSpec(FSLCommandInputSpec):
    """
    Parameters
    ----------
    in_file : str or list of str (mandatory)
        File or list of .png files to merge.

    merge : str (mandatory)
        Merge option : "merge_horizontally" or "merge_vertically".

    out_file : str
        Image to write.
    """
    in_file = traits.Either(
        File(exists=True),
        traits.List(File(exists=True)),
        mandatory=True,
        argstr="%s",
        position=1,
        desc="file or list of .png files")
    merge = traits.Enum('merge_horizontally', 'merge_vertically',
        argstr="%s", position=0,
        desc="merge option",
        mandatory=True)
    out_file = File(
        argstr="%s",
        genfile=False,
        desc="image to write",
        hash_files=False)


class PngAppendOutputSpec(TraitedSpec):
    """
    Returns
    -------
    out_file : str
        Merged output file.
    """
    out_file = File(
        exists=True,
        desc='merged output file')


class PngAppend(FSLCommand):
    """Use pngappend to merge images.

    Examples
    --------

    >>> import nsap.nipype.fsl_interfaces as fsl
    >>> f = fsl.PngAppend()
    >>> f.inputs.in_files = ['slice-1.png',slice-2.png']
    >>> f.inputs.merge = 'merge_horizontally'
    >>> f.inputs.out_file = 'merge.png'
    >>> f.run()
    """
    input_spec = PngAppendInputSpec
    output_spec = PngAppendOutputSpec

    _cmd = "pngappend"

    def _format_arg(self, name, spec, value):
        if name == "in_file":
            if isinstance(value, list):
                if self.inputs.get()["merge"] == "merge_horizontally":
                    return " + ".join(value)
                else:
                    return " - ".join(value)
            else:
                return "%s" % value
        elif name == "merge":
            return ""
        return super(PngAppend, self)._format_arg(name, spec, value)

    def _list_outputs(self):
        outputs = self._outputs().get()
        out_file = self.inputs.out_file
        if not isdefined(out_file):
            infile = self.inputs.in_file
            out_file = self._gen_fname(infile, ext='.png')
        outputs['out_file'] = os.path.abspath(out_file)
        return outputs

    def _gen_filename(self, name):
        if name == 'out_file':
            return self._list_outputs()['out_file']
        return None

