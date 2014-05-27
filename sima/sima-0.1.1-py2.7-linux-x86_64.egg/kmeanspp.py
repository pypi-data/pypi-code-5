# coding: utf-8
#
# Copyright (c) 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright (c) 2003-2012 SciPy Developers.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   a. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   b. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   c. Neither the name of Enthought nor the names of the SciPy Developers
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
"""
Python implementation of the kmeans++ algorithm.

Reference:
    Arthur, D. and Vassilvitskii, S. (2007). "k-means++: the advantages of
    careful seeding". Proceedings of the eighteenth annual ACM-SIAM symposium
    on Discrete algorithms. Society for Industrial and Applied Mathematics.
    Philadelphia, PA, USA. pp. 1027–1035.

Note that this code is modified from scipy.vq.kmeans and this contains the
following copyright notice.

COPYRIGHT NOTICE
================

"""
import numpy as np
from scipy.cluster.vq import kmeans, vq


def _kpppoints(obs, k):
    """Select points for initialization of cluster centers."""
    points = []
    points.append(obs[np.random.randint(obs.shape[0])])
    sq_dist = [((d - points[0]) ** 2).sum() for d in obs]
    for _ in xrange(1, k):
        r = np.random.rand() * sum(sq_dist)
        idx = 0
        while r > sq_dist[idx]:
            r -= sq_dist[idx]
            idx += 1
        points.append(obs[idx])
        sq_dist = [min(sq_dist[i], ((obs[i] - points[-1]) ** 2).sum())
                   for i in xrange(obs.shape[0])]
    return np.array(points)


def kmeanspp(obs, k, iter=5, thresh=1e-5):
    """
    Perform kmeans++ on a set of observation vectors forming k clusters.

    The k-means algorithm adjusts the centroids until sufficient
    progress cannot be made, i.e. the change in distortion since
    the last iteration is less than some threshold. This yields
    a code book mapping centroids to codes and vice versa.

    Distortion is defined as the sum of the squared differences
    between the observations and the corresponding centroid.

    Parameters
    ----------
    obs : ndarray
       Each row of the M by N array is an observation vector. The
       columns are the features seen during each observation.
       The features must be whitened first with the `whiten` function.

    k : int
       The number of centroids to generate. A code is assigned to
       each centroid, which is also the row index of the centroid
       in the code_book matrix generated.

       The initial k centroids are chosen by randomly selecting
       observations from the observation matrix.

    iter : int, optional
       The number of times to run k-means++, returning the codebook
       with the lowest distortion. This argument is ignored if
       initial centroids are specified with an array for the
       ``k_or_guess`` parameter. This parameter does not represent the
       number of iterations of the k-means algorithm.

    thresh : float, optional
       Terminates the k-means algorithm if the change in
       distortion since the last k-means iteration is less than
       or equal to thresh.

    Returns
    -------
    codebook : ndarray
       A k by N array of k centroids. The i'th centroid
       codebook[i] is represented with the code i. The centroids
       and codes generated represent the lowest distortion seen,
       not necessarily the globally minimal distortion.

    distortion : float
       The distortion between the observations passed and the
       centroids generated.

    idx :
    """
    if int(iter) < 1:
        raise ValueError('iter must be at least 1.')
    distortion = np.inf
    for _ in range(iter):
        _codebook, _distortion = kmeans(obs, _kpppoints(obs, k), thresh=thresh)
        if _distortion < distortion:
            distortion = _distortion
            codebook = _codebook
    idx, _ = vq(obs, codebook)
    return codebook, distortion, idx
