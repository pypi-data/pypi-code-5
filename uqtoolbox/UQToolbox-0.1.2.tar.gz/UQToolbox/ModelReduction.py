# -*- coding: utf-8 -*-

#
# This file is part of UQToolbox.
#
# UQToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UQToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with UQToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#


import sys

import numpy as np

from numpy import linalg as la

from scipy import linalg as scla

from SpectralToolbox import Spectral1D

def KLExpansion1D(C,N,scFun=None,totVar=1.):
    """
    KLExpansion1D(): Computes the 1D KL expansion of the covariance matrix C, using the
       Legendre-Gauss-Loabatto rule for the solution to the generalized eigenvalue 
       problem A * u = lmb * M * u
    
    Syntax:
        ``(x,val,vec,var,Nvar) = KLExpansion1D(C,N,[scFun=None],[totVar=1.])``
    
    Input:
        * ``C`` = (function) Covariance function C(x1,x2)
        * ``N`` = (1d-array,float) number of discretization points
        * ``scFun`` = (function) scaling function of coordinates from Legendre-Gauss-Lobatto points to real domain of C(x1,x2)
        * ``totVar`` = (float) total variance to be represented by the output KL-expansion
    
    Output:
        * ``x`` = (1d-array, float) Legendre-Gauss-Lobatto nodes used
        * ``val`` = (1d-array, float) eigenvalues
        * ``vec`` = (2d-array, float) normalized eigenvectors. The eigenvector vec[:,i] corresponds to the eigenvalue val[i].
        * ``var`` = (float) total variance represented
        * ``Nvar`` = (int) number of modes to be consider in order to achieve ``totVar``
    """
    
    if scFun == None:
        def scFun(x):
            return x;    

    # Lagrange polynomials....
    poly = Spectral1D.Poly1D(Spectral1D.JACOBI,[0.,0.])
    (xI,wI) = poly.GaussLobattoQuadrature(2 * N)
    # wI /= np.sum(wI)
    
    xSc = scFun(xI)
    X1,X2 = np.meshgrid(xSc,xSc)
    
    M = np.diag(wI)
    K = np.dot(M, np.dot(C(X1,X2),M) )
    
    ''' Solve generalized eigenvalue problem '''
    (valI,vecI) = scla.eig(K,M)
    valI = np.real(valI[:N])
    vecI = np.real(vecI[:,:N])    
    
    ''' Compute variance represented by the successive modes '''
    j = -1
    var = 0.
    while (var < totVar) and (j<N-1):
        j += 1
        var += valI[j] * np.dot( wI * vecI[:,j], vecI[:,j])
    
    if var < totVar:
        print >> sys.stderr, "KL-expansion: length of the expansion not sufficient to resolve the target variance:"
        print >> sys.stderr, "KL-expansion: Target Variance      = %f" % totVar
        print >> sys.stderr, "KL-expansion: Represented Variance = %f" % var
    
    return (xI,valI,vecI,var,j+1)
    
