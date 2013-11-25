"""Find the most probable value in a HiSPARC spectrum.

:class:`FindMostProbableValueInSpectrum`
   find the most probable value in a HiSPARC spectrum

"""
import datetime
import urllib2
import json
import StringIO
import warnings

import numpy as np
from scipy.stats import norm
from scipy.optimize import curve_fit

import pylab as plt


API_URL = 'http://data.hisparc.nl/api/stations/data/%d/%d/%d/'
HIST_URL = 'http://data.hisparc.nl/show/source/pulseintegral/%d/%d/%d/%d/'

MPV_FIT_WIDTH_FACTOR = .4


class FindMostProbableValueInSpectrum(object):
    """Find the most probable value (MPV) in a HiSPARC spectrum.

    This is a fast algorithm to find the MPV value in a HiSPARC spectrum.
    The MPV value indicates the position of the minimum-ionizing particles
    (MIP) peak.  The algorithm makes some assumptions about the shape of
    the spectrum:

       * the spectrum includes the gamma peak (left-most part of
         spectrum) which has more counts per bin than the MIP peak.
       * ignoring the gamma peak, the MIP peak can be bracketed on the
         left by the numerically largest bin-to-bin increase in the
         number of counts.
       * the MIP peak can be approximated by a normal distribution.

    Public methods:

    :meth:`find_mpv`
        Find the most probable value
    :meth:`find_first_guess_mpv`
        Make a first guess of the most probable value
    :meth:`fit_mpv`
        Based on a first guess, fit the MIP peak to obtain the MPV

    """

    def __init__(self, n, bins):
        """Initialize the class instance.

        :param n, bins: histogram counts and bins, as obtained using
            :func:`numpy.histogram`.

        """
        self.n, self.bins = n, bins

    def find_mpv(self):
        """Find the most probable value.

        First perform a first guess, then use that value to fit the MIP
        peak.

        :return mpv: best guess of the most probable value
        :return boolean is_fitted: indicates if the fit was successful.

        """
        first_guess = self.find_first_guess_mpv()
        try:
            mpv = self.fit_mpv(first_guess)
        except RuntimeError:
            warnings.warn("Fit failed")
            return -999, False
        else:
            return mpv, True

    def find_first_guess_mpv(self):
        """First guess of most probable value.

        The algorithm is fast and simple. The following steps are
        performed:

           * From the left: find the greatest value and cut off all data
             to the left of that maximum.  We now assume the first
             datapoint to be the maximum of the gamma peak.
           * From the right: find the location of the greatest decrease
             from bin to bin.  We assume that this value is where the MIP
             peak dips before joining the gamma peak.
           * Find the maximum *to the right* of this value.  We assume
             this to be the approximate location of the MIP peak.

        :returns mpv: first guess of the most probable value

        """
        n, bins = self.n, self.bins

        # cut off trigger from the left
        left_idx = n.argmax()
        cut_n = n[left_idx:]

        # find greatest decrease from right
        delta_n = cut_n[:-1] - cut_n[1:]
        idx_greatest_decrease = delta_n.argmin()
        cut_cut_n = cut_n[idx_greatest_decrease:]

        # estimate most probable value with maximum in bracketed data
        idx_right_max = cut_cut_n.argmax()

        # calculate position of most probable value
        idx_mpv = idx_right_max + idx_greatest_decrease + left_idx
        mpv = (bins[idx_mpv] + bins[idx_mpv + 1]) / 2.

        return mpv

    def fit_mpv(self, first_guess, width_factor=MPV_FIT_WIDTH_FACTOR):
        """Fit a normal distribution to the MIP peak to obtain the MPV.

        A normal distribution is fitted to the spectrum in a restricted
        domain around the first guess value.  The width of the domain can
        be adjusted by the width_factor parameter.

        :param first_guess: approximate location of the most probable
            value
        :param width_factor: float in the range [0., 1.] to indicate the
            width of the fit domain.  The domain is given by
            [(1. - width_factor) * first_guess, (1. + width_factor) *
            first_guess]
        :returns mpv: mpv value obtained from the fit

        """
        n, bins = self.n, self.bins

        bins_x = (bins[:-1] + bins[1:]) / 2.

        # calculate fit domain
        left = (1. - width_factor) * first_guess
        right = (1. + width_factor) * first_guess

        # bracket histogram data
        x = bins_x.compress((left <= bins_x) & (bins_x < right))
        y = n.compress((left <= bins_x) & (bins_x < right))

        # sanity check: number of data points must be at least equal to
        # the number of fit parameters
        if len(x) < 3:
            raise RuntimeError("Number of data points not sufficient")

        # fit to a normal distribution
        f = lambda x, N, a, b: N * norm.pdf(x, loc=a, scale=b)
        popt, pcov = curve_fit(f, x, y, p0=(y.max(), first_guess,
                                            first_guess))
        mpv = popt[1]

        # sanity check: if MPV is outside domain, the MIP peak was not
        # bracketed correctly
        if mpv < x[0] or mpv > x[-1]:
            raise RuntimeError("Fitted MPV value outside range")

        return mpv


def main():
    """Demo the MPV finder with actual data."""

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    station_ids = get_station_ids_with_data(yesterday)

    for station in station_ids:
        if station == 10:
            continue
        print station
        n, bins = get_histogram_for_station_on_date(station, yesterday)
        find_mpv = FindMostProbableValueInSpectrum(n, bins)
        mpv, is_fitted = find_mpv.find_mpv()

        plt.figure()
        plt.plot((bins[:-1] + bins[1:]) / 2., n)
        if is_fitted:
            plt.axvline(mpv, c='g')
        else:
            plt.axvline(mpv, c='r')
        plt.title(station)
        plt.yscale('log')


def get_station_ids_with_data(date):
    """Return the station ids having data on this day."""

    url = API_URL % (date.year, date.month, date.day)

    reply = urllib2.urlopen(url)
    reply = reply.read()

    station_list = json.loads(reply)
    station_ids = [int(u['number']) for u in station_list]

    return station_ids


def get_histogram_for_station_on_date(station_id, date):
    """Return a histogram of the spectrum of a station on a date.

    :return n, bins: histogram counts and bins, as obtained using
       :func:`numpy.histogram`.

    """
    url = HIST_URL % (station_id, date.year, date.month, date.day)

    reply = urllib2.urlopen(url)
    reply = reply.read()

    file_like = StringIO.StringIO(reply)
    data = np.genfromtxt(file_like)

    bins = data[:, 0]
    bins = list(bins)
    bins.append(bins[-1] + (bins[-1] - bins[-2]))
    bins = np.array(bins)

    n = data[:, 1]

    return n, bins


if __name__ == '__main__':
    warnings.simplefilter('always')
    main()
    plt.show()
