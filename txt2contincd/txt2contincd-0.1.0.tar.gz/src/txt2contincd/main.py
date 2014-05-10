# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import sys
import numpy as np
import maidenhair
import maidenhair.statistics
from txt2contincd.utils import ichunk

@np.vectorize
def molar_concentration(c, m):
    """
    Calculate molar concentration (mol/L)

    Args:
        c (float): concentration in g/L
        m (float): molecular weight in kDa (=kg/mol)
    """
    m = m * 10e+3   # kDa -> Da (=g/mol)
    return c / m

@np.vectorize
def mean_residue_ellipticity(phi, n, c, l):
    """
    Calculate mean residue ellipticity (millideg cm2 / decimol) from
    ellipticity (mdeg)

    Args:
        phi (float): a ellipticity (milli deg)
        n (int): the number of residues
        c (float): the molar concentration of the polymer (mol/L)
        l (float): the length of the cuvette (cm)

    Returns:
        a mean residue ellipticity (deg cm2 decimol^{-1} residue^{-1})
    """
    return phi / (10 * l * n * c)

def translate_dataset(dataset, n, m, c, L,
                      is_molar_concentration=False):
    """
    Translate dataset from mdeg into mean residue ellipticities

    Args:
        n (int): the number of residues
        m (float): molecular weight in kDa (=kg/mol)
        c (float): concentration in g/L
        L (float): the length of the cuvette (cm)
        is_molar_concentration (bool): True if the specified concentration is 
            a molar concentration (mol/L)

    Returns:
        a dataset with mean residue ellipticity (deg cm2 decimol^{-1})
    """
    if not is_molar_concentration:
        # g/L to mol/L
        c = molar_concentration(c, m)
    for i, (x, y) in enumerate(dataset):
        dataset[i][1] = mean_residue_ellipticity(y, n, c, L)
    return dataset

def print_contincd_in(dataset, title, out=sys.stdout, strict=True):
    """
    Print dataset in CONTINT-CD format 

    Args:
        dataset (list): A maidenhair output dataset
        title (str): A title prefix of each dataset
        strict (bool): True for regulate the CD spectrum region
    """
    for i, (x, y) in enumerate(dataset):
        x = maidenhair.statistics.average(x)
        y = maidenhair.statistics.average(y)
        if strict:
            where = np.where((x >= 190) & (x <= 240))
            x, y = x[where], y[where]
        # a heading of the block
        print >> out, " {} - {:d}".format(title, i)
        if i == 0:
            # specify the input FORMAT of the mean residue ellipticities
            print >> out, " IFORMY"
            print >> out, " (7F9.0)"
        # print LAST if there is more than one dataset
        if len(dataset) > 1:
            if i == 0:
                print >> out, " LAST" + (" " * 18) + "-1."
            elif i == len(dataset) - 1:
                print >>out, " LAST" + (" " * 18) + "1."
        print >> out, " END"
        # print ellipticities
        N, S, E = str(len(x)), str(x[0]), str(x[-1])
        print >> out, " NSTEND   {}{}{}{}{}".format(
                    N, " "*(13-len(N)), 
                    S, " "*(15-len(S)), E) 
        # 7 columns
        for ychunk in ichunk(y, 7):
            cols = map(lambda x: str(x).rjust(8)[:8], ychunk)
            print >> out, " " + " ".join(cols)

