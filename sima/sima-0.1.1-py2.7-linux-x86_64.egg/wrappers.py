from os.path import join, basename, dirname
import cPickle

from sima.frame_alignment import CorrectedImagingDataset
from sima.mcorr import MCImagingDataset
from sima.iterables import MultiPageTIFF


def motion_correction(
        filenames, num_states_retained=50, clip=None,
        save_corrected_tseries=False, max_displacement=None,
        trimming_min_occupancy=None, artifact_channels=None,
        save_path='displacements.pkl'):
    """Motion correct the imaging timeseries.

    This function creates a directory called 'corrected' within the directory
    containing the images, Saves the estimated diplacements in a file named
    displacements.pkl within the corrected directory. This function also
    optionally saves the corrected time series TIFF files in the corrected
    directory.

    Parameters
    ----------
    filenames : list of list of str
        Filenames of the time series TIFF files, arranged such that
        filenames[n][m] is the filename for channel m of imaging cycle n.
    num_states_retained : int
        Number of states to retain at each time step of the HMM.
    clip : tuple of tuple of int, optional
        The number of rows/columns to clip from each edge
        in order ((top, bottom), (left, right)).
    save_corrected_tseries : bool
        Whether to save the corrected time series.
    max_displacement : array of int
        The maximum allowed displacement magnitudes in [y,x].
    trimming_min_occupancy: float, optional
        The minimum fraction of frames on which a row/column must be imaged
        to be included in corrected data. If None, all pixels that go out of
        frame at any time are clipped.
    artifact_channels : list of int, optional
        Channels for which artifact light should be checked.
    save_directory : str, optional
        The directory in which to save the motion correction output.
    """
    iterables = [[MultiPageTIFF(chan, clip) for chan in cycle]
                 for cycle in filenames]
    mcds = MCImagingDataset(iterables)
    mc_record = mcds.estimate_displacements(num_states_retained,
                                            max_displacement,
                                            artifact_channels)
    with open(save_path, 'wb') as f:
        cPickle.dump(mc_record, f, protocol=cPickle.HIGHEST_PROTOCOL)

    save_filenames = [[join(dirname(chan), 'corrected', basename(chan))
                       for chan in cycle] for cycle in filenames]
    time_avg_filenames = [join(dirname(chan), 'corrected', basename(chan))
                          for chan in filenames[0]]
    save_corrected(filenames, mc_record['displacements'], save_filenames,
                   time_avg_filenames, trimming_min_occupancy, clip=clip)
    print('*** SUCCESSFULLY COMPLETED ***\n')


def save_corrected(filenames, displacements, save_filenames=None,
                   time_avg_filenames=None, min_occupancy=None, clip=None):
    """Save corrected time averages and (optionally) time series.

    Parameters
    ----------
    trimming_min_occupancy: the minimum fraction of frames on which a
        row/column must be imaged to be included in corrected data.
        If None, all pixels that go out of frame at any time are clipped.
    """
    iterables = [[MultiPageTIFF(chan, clip) for chan in cycle]
                 for cycle in filenames]
    ids = CorrectedImagingDataset(iterables, displacements)
    if save_filenames is not None:
        ids.save_frames(save_filenames)
    if time_avg_filenames is not None:
        ids.save_time_averages(time_avg_filenames)
