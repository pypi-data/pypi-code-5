from __future__ import division, print_function
import math
import itertools
import os
import sys
import subprocess


def window(iterable, size=2, step=1):
    """
    iterate over subseqs of iterable
    
    Example
    =======
    
    >>> seq = range(6)
    
    >>> list(window(seq, 3, 1))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    
    >>> list(window(seq, 3, 2))
    [(0, 1, 2), (2, 3, 4)]
    
    # the same as pairwise
    >>> assert list(window(range(5), 2, 1)) == [(0, 1), (1, 2), (2, 3), (3, 4)]
    """
    iterators = itertools.tee(iterable, size)
    for skip_steps, itr in enumerate(iterators):
        for ignored in itertools.islice(itr, skip_steps):
            pass
    window_itr = itertools.izip(*iterators)
    if step != 1:
        window_itr = itertools.islice(window_itr, 0, 99999999, step)
    return window_itr


def soundpressure_to_soundlevel(Pa, p0=0.00002):
    """
    convert soundpressure in Pascal to sound level in dB (dBSPL)

    Lp(dBSPL) = 20 * log10(p/p0)

    p0: threshold of hearing, 0.00002 Pa (20uPa)
    """
    return 20 * math.log10(Pa / p0)


def soundlevel_to_soundpressure(dB, p0=0.00002):
    """
    convert sound-level in dB to sound-pressure in Pascal

    p = p0 * e^(1/20*Lp*log10(10))

    p0: threshold of hearing, 0.00002 Pa (20uPa) 
    """
    return p0 * math.exp(1 / 20 * dB * _math.log(10))


dB2Pa = L2p = soundlevel_to_soundpressure
Pa2dB = p2L = soundpressure_to_soundlevel


def _findfile(f, possible_folders):
    for folder in possible_folders:
        if os.path.exists(os.path.join(folder, f)):
            return folder
    return None


def detect_lambda():
    """
    Returns the path of the Lambda binary or None if not found

    :rtype: str or None. The path to the lambda binary
    """
    def check_which():
        """
        :rtype : str or None. The path of the file
        """
        try:
            path = subprocess.check_output(["which", "lambda"])
            if os.path.exists(path):
                return path
        except subprocess.CalledProcessError:
            pass

    if sys.platform == 'darwin':
        lambdabin = check_which()
        if lambdabin is not None:
            return lambdabin
        possible_folders = [
            "/Applications",
            os.path.expanduser("~/Applications")
        ]
        lambda_app = _findfile('Lambda.app', possible_folders)
        if not lambda_app:
            return None
        lambdabin = os.path.join(lambda_app, 'Contents', 'MacOS', 'Lambda')
        if not os.path.exists(lambdabin):
            raise IOError("Found the lambda app (%s) but the lambda binary was not present" % lambda_app)
        return lambdabin
    elif sys.platform == 'linux2':
        lambdabin = check_which()
        if lambdabin is not None:
            return lambdabin
    elif sys.platform == 'window':
        return None
