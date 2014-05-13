#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import nibabel
import numpy
import matplotlib

matplotlib.use("AGG")

import matplotlib.pyplot as plt


""" The application of the BIRN / Calibrain protocol yields six measurements

* Mean Signal Image
* Temporal Fluctuation Noise Image

"""


def load_fmri_dataset(fmri_file):
    """ Load a functional volume

    Parameters
    ----------
    fmri_file: str (mandatory)
        the path to the functional volume

    Returns
    -------
    array: numpy ndarray [X,Y,Z,N]
        the functional volume
    """
    img = nibabel.load(fmri_file)
    return img.get_data()


def get_fmri_signal(array):
    """ The fmri signal is the the average voxel intensity across time

    A signal summary value is obtained from an ROI placed in the center.

    Parameters
    ----------
    array: numpy ndarray [X,Y,Z,N]
        the functional volume

    Returns
    -------
    signal: numpy ndarray [X,Y,Z]
        the fmri signal

    FMRI Data Quality, Pablo Velasco, 2014
    SINAPSE fMRI Quality Assurance, Katherine Lymer
    """
    return numpy.average(array, 3)


def get_fmri_temporal_fluctuation_noise(array):
    """ The fluctuation noise image is produced by substracting for each voxel
    a trend line estimated from the data (the BIRN function uses a second
    order polynomial - It's effectively a standard deviation image)

    By removing the trend from the data, the fluctuation noise image is an
    image of the standard deviation of the residuals, voxel by voxel.

    A linear trand may indicate a systematic
    increase or decrease in the data (caused by eg sensor drift)

    Parameters
    ----------
    array: numpy ndarray [X,Y,Z,N]
        the functional volume
    """
    flat_array = array.ravel()
    voxels_per_volume = reduce(lambda x, y: x * y, array.shape[: -1], 1)
    tfn = numpy.ndarray((voxels_per_volume,), dtype=numpy.single)

    x = numpy.arange(array.shape[3])
    for i in range(voxels_per_volume):
        y = flat_array[i::voxels_per_volume]
        polynomial = numpy.polyfit(x, y, 2)
        model = numpy.polyval(polynomial, x)
        residuals = y - model
        tfn[i] = numpy.std(residuals)

    return tfn.reshape(array.shape[:-1])


def get_signal_to_fluctuation_noise_ratio(signal_array, tfn_array,
                                          roi_size=10):
    """ The SFNR image is is obtained by dividing, voxel by voxel,
    the mean fMRI signal image by the temporal fluctuation image.

    A 21 x 21 voxel ROI, placed in the center of the image, is created.
    The average SFNR across these voxels is the SFNR summary value.
    """
    sfnr_array = signal_array / (tfn_array + numpy.finfo(float).eps)
    center = numpy.round(sfnr_array.shape / 2)
    roi = sfnr_array[center[0] - roi_size: center[0] + roi_size,
                     center[1] - roi_size: center[1] + roi_size,
                     center[2]]
    sfnr_summary = numpy.average(roi)
    return sfnr_array, sfnr_summary


def get_static_spatial_noise(array):
    """ In order to measure the spatial noise, the sum of the odd and even
    numbered slices are calculated separately.
    The static patial noise is then approximated by the differences of
    these two sums.

    If there is no drift in either amplitude or geometry across time series,
    then the difference image will show no structure and provides
    """
    shape_x = array.shape[0]
    odd_array = array[range(1, shape_x, 2)]
    odd_sum_array = numpy.sum(odd_array, 0)
    even_array = array[range(0, shape_x, 2)]
    even_sum_array = numpy.sum(even_array, 0)
    ssn_array = odd_sum_array - even_sum_array
    return ssn_array


def get_spatial_noise_ratio(signal_array, ssn_array, nb_time_points,
                            roi_size=10):
    """ The same ROI is placed in the center of the static spatial noise
    image
    The SNR is the signal summary value divided by by the square
    root of the variance summary value divided by the numbre of time points
    SNR = (signal summary value)/sqrt((variance summary value)/#time points).
    """
    center = numpy.round(signal_array.shape / 2)
    signal_roi_array = signal_array[
        center[0] - roi_size: center[0] + roi_size,
        center[1] - roi_size: center[1] + roi_size,
        center[2]]
    ssn_roi_array = ssn_array[
        center[0] - roi_size: center[0] + roi_size,
        center[1] - roi_size: center[1] + roi_size,
        center[2]]
    signal_summary = numpy.average(signal_roi_array)
    variance_summary = numpy.var(ssn_roi_array)

    snr = signal_summary / numpy.sqrt(variance_summary / nb_time_points)

    return snr


def get_snr_percent_fluctuation_and_drift(array, roi_size=10):
    """ A time-series of the average intensity within a 21 x 21 voxel ROI
    centered in the image is calculated.

    A second-order polynomial trend is fit to the volume number vs
    average intensity.

    The mean signal intensity of the time-series (prior
    to detrending) and SD of the residuals after subtracting the fit line
    from the data, are calculated.

    %fluctuation = 100*(SD of the residuals)/(mean signal intensity)
    %drift = ((max fit value) - (min fit value)) /
             (mean signal intensity signal)
    """
    center = numpy.round(numpy.asarray(array.shape) / 2)
    roi = array[center[0] - roi_size: center[0] + roi_size,
                center[1] - roi_size: center[1] + roi_size,
                center[2]]
    shape = roi.shape

    mean_signal_intensity = numpy.average(roi)
    average_intensity = numpy.sum(numpy.sum(roi, 1), 1)
    average_intensity /= shape[-2] * shape[-1]

    volume_number = numpy.arange(shape[0])
    polynomial = numpy.polyfit(volume_number, average_intensity, 2)
    average_intensity_model = numpy.polyval(polynomial, volume_number)
    residuals = average_intensity - average_intensity_model

    fluctuation = 100. * numpy.std(residuals) / mean_signal_intensity
    drift = 100. * (average_intensity_model.max() -
            average_intensity_model.min()) / mean_signal_intensity

    return average_intensity, polynomial, residuals, fluctuation, drift


def get_residuals_spectrum(residuals, repetition_time):
    """ Residuals of the mean signal intensity fit are submitted to
    a fast Fourier transform (FFT)
    """
    fft = numpy.fft.rfft(residuals)
    if residuals.size % 2 == 0:
        # Discard real term for frequency n/2
        fft = fft[:-1]
    fftfreq = numpy.fft.fftfreq(len(residuals), repetition_time)
    return numpy.vstack((fftfreq[:len(fft)], numpy.abs(fft)))


def get_weisskoff_analysis(array, max_size=21):
    """ The Weisskoff analysis provides another measure of scanner
    stability included in the GSQAP.
    """
    x = numpy.arange(1, max_size + 1)
    fluctuation = [get_snr_percent_fluctuation_and_drift(array, r)[-2]
                   for r in x]
    theoretical_fluctuation = fluctuation[0] / x
    rdc = fluctuation[0] / fluctuation[-1]

    return (numpy.vstack((x, fluctuation)),
            numpy.vstack((x, theoretical_fluctuation)), rdc)


def weisskoff_figure(fluctuations, theoretical_fluctuations, rdc):
    """ Return a matplotlib figure containing the Weisskoff analysis.
    """
    figure = plt.figure()
    plot = figure.add_subplot(111)

    plot.plot(fluctuations[0], fluctuations[1], "ko-", fillstyle="full")
    plot.plot(theoretical_fluctuations[0], theoretical_fluctuations[1],
              "ko-", markerfacecolor="w")

    plot.axes.loglog()
    plot.axes.set_xlabel("ROI width (pixels)")
    plot.axes.set_ylabel("Fluctuation (%)")
    plot.xaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
    plot.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
    plot.legend(("Measured", "Theoretical"), "upper right")

    return figure


def spectrum_figure(spectrum):
    """ Return a matplotlib figure containing the Fourier spectrum, without its
        DC coefficient.
    """
    figure = plt.figure()
    plot = figure.add_subplot(111)
    plot.plot(spectrum[0, 1:], spectrum[1, 1:], "k-")
    plot.axes.set_xlabel("Frequency (Hz)")
    plot.axes.set_ylabel("Magnitude")
    return figure


def time_series_figure(time_series, polynomial):
    """ Return a matplotlib figure containing the time series and
    its polynomial model.
    """
    figure = plt.figure()
    plot = figure.add_subplot(111)

    x = numpy.arange(2, 2 + len(time_series))
    model = numpy.polyval(polynomial, x)

    plot.plot(x, time_series, "k-")
    plot.plot(x, model, "k-")

    plot.axes.set_xlabel("Volume number")
    plot.axes.set_ylabel("Intensity")

    return figure


##############################################################
#                     Pilot
##############################################################

def pilot(working_dir="/volatile/nsap/casper"):
    """
    """
    # Pilot imports
    from caps.toy_datasets import get_sample_data

    # Get toy dataset
    toy_dataset = get_sample_data("localizer")
    print toy_dataset.fmri, toy_dataset.TR

    array = load_fmri_dataset(toy_dataset.fmri)
    print array.shape
    signal = get_fmri_signal(array)
    print signal.shape
    #tfn = get_fmri_temporal_fluctuation_noise(array)
    #print tfn.shape

    (average_intensity, polynomial, residuals, fluctuation,
     drift) = get_snr_percent_fluctuation_and_drift(array)
    spectrum = get_residuals_spectrum(residuals, 2.4 * 10e-3)
    spectrum_figure(spectrum)
    time_series_figure(average_intensity, polynomial)

    (fluctuations, theoretical_fluctuations,
     rdc) = get_weisskoff_analysis(array, max_size=21)
    print fluctuations
    #weisskoff_figure(fluctuations, theoretical_fluctuations, rdc)
    plt.show()


if __name__ == "__main__":
    pilot()