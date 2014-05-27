"""Alignment of motion-corrected data."""
import itertools as it
import warnings
import cPickle
import os

import numpy as np

from sima.misc import lazyprop, mkdir_p
from sima.imaging import ImagingDataset, _ImagingCycle
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sima.tifffile import TiffFileWriter


class CorrectedImagingDataset(ImagingDataset):
    """Imaging dataset subclassed with alignment functionality.

    Iterating over an object of this class yields motion-corrected
    frames with NaN values in unobserved locations.

    Parameters
    ----------
    TODO
    trimming_min_occupancy :

    See ImagingDataset.

    """
    def __init__(self, iterables, savedir, displacements=None,
                 trimming_min_occupancy=None, channel_names=None):
        if displacements is None:
            with open(os.path.join(savedir, 'displacements.pkl'), 'rb') as f:
                displacements = cPickle.load(f)
        else:
            mkdir_p(savedir)
            with open(os.path.join(savedir, 'displacements.pkl'), 'wb') as f:
                cPickle.dump(displacements, f, cPickle.HIGHEST_PROTOCOL)
        min_displacement = np.amin(
            [x.min(axis=0) for x in displacements], axis=0)
        self.displacements = [x - min_displacement for x in displacements]
        self.max_displacement = np.amax(
            [x.max(axis=0) for x in self.displacements], axis=0)
        self.trimming_min_occupancy = trimming_min_occupancy
        assert all(d.shape[1] == 2 for d in self.displacements)
        ImagingDataset.__init__(self, iterables=iterables, savedir=savedir,
                                channel_names=channel_names)


    def todict(self):
        """Returns the dataset as a dictionary, useful for saving"""
        data = super(CorrectedImagingDataset, self).todict()
        return data.update(
            {'trimming_min_occupancy': self.trimming_min_occupancy})

    # def save(self, filename, extra_data=None):
