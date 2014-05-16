"""analysis.py
offline audio oracle / factor oracle generation routines for PyOracle

Copyright (C) 1.3.2014 Cheng-i Wang

This file is part of PyOracle.

PyOracle is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyOracle is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOracle.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import sys
from Resources.PyOracle.FactOracle import get_distance 

def create_selfsim(oracle, method = 'compror'): 
    """ Create self similarity matrix from compror codes or suffix links
    """
    len_oracle = oracle.n_states - 1
    mat = np.zeros((len_oracle, len_oracle))
    if method == 'compror':
        if oracle.code == []:
            print "Codes not generated. Generating codes with encode()."
            oracle.encode()
        ind = 0
        inc = 1
        for l, p in oracle.code:
            if l == 0:
                inc = 1
            else:
                inc = l
            if inc >= 1:
                for i in range(l):
                    mat[ind+i][p+i-1] = 1
                    mat[p+i-1][ind+i] = 1
            ind = ind + inc
    elif method == 'suffix':
        for i, s in enumerate(oracle.sfx):
            while s != None and s != 0:
                mat[i-1][s-1] = 1
                mat[s-1][i-1] = 1 
                s = oracle.sfx[s]    
    return mat

def create_transition(oracle, method = 'trn'):
    if oracle.kind == 'r':
        mat, hist = _create_trn_mat_symbolic(oracle, method)
        return mat, hist
    elif oracle.kind ==  'a':
        raise NotImplementedError("Audio version is under construction, coming soon!")

def _create_trn_mat_symbolic(oracle, method):
    n = oracle.get_num_symbols()
    sym_list = [oracle.data[_s] for _s in oracle.trn[0]]
    hist = np.zeros((n))
    mat = np.zeros((n,n))
    for i in range(1, oracle.n_states-1):
        _i = sym_list.index(oracle.data[i])
        if method == 'trn':
            trn_list = oracle.trn[i]
#         elif method == 'rsfx':
#             trn_list = oracle.rsfx[i]
        elif method == 'seq':
            trn_list = [i+1]

        for j in trn_list:
            if j < oracle.n_states:
                _j = sym_list.index(oracle.data[j])
                mat[_i][_j] += 1
            else: 
                print "index " + str(j) + " is out of bounds." 
            hist[_i] += 1
    mat = mat.transpose()/hist
    mat = mat.transpose()
    return mat, hist

def _test_context(oracle, context):
    _b, _s = oracle.accept(context)
    while not _b:
        context = context[1:]
        _b, _s = oracle.accept(context)
    return _b, _s, context

def predict(oracle, context, ab=[], VERBOSE = 0):
    if VERBOSE:
        print "original context: ", context
    if ab == []:
        ab = oracle.get_alphabet()
        
    _b, _s, context = _test_context(oracle, context)    
    _lrs = [oracle.lrs[k] for k in oracle.rsfx[_s]]
    context_state = []
    while context_state == []:
        for _i,_l in enumerate(_lrs):
            if _l >= len(context):
                context_state.append(oracle.rsfx[_s][_i])
        if context_state != []:
            break
        else:
            context = context[1:]
            _b, _s = oracle.accept(context)
            _lrs =  [oracle.lrs[k] for k in oracle.rsfx[_s]]
    if VERBOSE:                    
        print "final context: ", context
        print "context_state: ", context_state
    d_count = len(ab) 
    hist = [1.0] * len(ab) # initialize all histograms with 1s.
    
    trn_data = [oracle.data[n] for n in oracle.trn[_s]]
    for k in trn_data:
        hist[ab[k]] += 1.0
        d_count += 1.0
    
    for i in context_state:
        d_count, hist = _rsfx_count(oracle, i, d_count, hist, ab)
    
    return [hist[idx]/d_count for idx in range(len(hist))], context   
     
def _rsfx_count(oracle, s, count, hist, ab, VERBOSE = 0):
    trn_data = [oracle.data[n] for n in oracle.trn[s]]
    for k in trn_data:
        hist[ab[k]] += 1.0
        count += 1.0

    rsfx_candidate = oracle.rsfx[s]
    while rsfx_candidate != []:
        s = rsfx_candidate.pop(0)
        trn_data = [oracle.data[n] for n in oracle.trn[s]]
        for k in trn_data:
            hist[ab[k]] += 1.0
            count += 1.0
        rsfx_candidate.extend(oracle.rsfx[s])
        
    return count, hist
            
def logEval(oracle, testSequence, ab = [], m_order = None, VERBOSE = 0):
    ''' Evaluate the average log-loss of a sequence given an oracle 
    '''
    if ab == []:
        ab = oracle.get_alphabet()
    if VERBOSE:
        print ' '
    
    logP = 0.0
    context = []
    increment = np.floor((len(testSequence)-1)/100)
    bar_count = -1
    maxContextLength = 0
    avgContext = 0
    for i,t in enumerate(testSequence):
        
        p, c = predict(oracle, context, ab, VERBOSE = 0)
        if len(c) < len(context):
            context = context[-len(c):]
        logP -= np.log2(p[ab[t]])
        context.append(t)
        
        if m_order != None:
            if len(context) > m_order:
                context = context[-m_order:]
        avgContext += float(len(context))/len(testSequence)

        if VERBOSE:
            percentage = np.mod(i, increment)
            if percentage == 0:
                bar_count += 1
            if len(context) > maxContextLength:
                maxContextLength = len(context)
            sys.stdout.write('\r')
            sys.stdout.write("\r[" + "=" * bar_count +  
                             " " * (100-bar_count) + "] " +  
                             str(bar_count) + "% " +
                             str(i)+"/"+str(len(testSequence)-1)+" Current max length: " + str(maxContextLength))
            sys.stdout.flush()
    return logP/len(testSequence), avgContext
            
            
def cluster(oracle):
    raise NotImplementedError("cluster() is under construction, coming soon!")
    
def segment(oracle):
    raise NotImplementedError("segment() is under construction, coming soon!")

def _rsfxmin(oracle, n, x, theta, c):
    if oracle.rsfx[n] == []:
        return c, theta
    else:
        for k in oracle.rsfx[n]:
            theta_hat = get_distance(x, oracle.data[k], oracle.params['weights'], oracle.params['dfunc'])
            if theta > theta_hat:
                theta = theta_hat
                c = k        
            return _rsfxmin(oracle, k, x, theta, c) 
    
def _sfxmin(oracle, n, x, theta, c):
    while oracle.sfx[n] != 0:
        theta_hat = get_distance(x, oracle.data[oracle.sfx[n]], oracle.params['weights'], oracle.params['dfunc'])
        if theta > theta_hat:
            theta = theta_hat
            c = oracle.sfx[n]        
        n = oracle.sfx[n]
    return c, theta

        
def query_complete(oracle, query):
    """ Return the closest path in target oracle given a query sequence
    
    Args:
        oracle: an oracle object already learned, the target. 
        query: the query sequence in a matrix form such that 
        the ith row is the feature at the ith time point 
    
    """
    N = len(query)
    K = oracle.get_num_symbols()
    C = [0] * K # cost vector
    P = [[0]* N for _i in range(K)] # path matrix 
    
    for ind,k in enumerate(oracle.rsfx[0]): # emission transition
        theta_k = get_distance(query[0], oracle.data[k], oracle.params['weights'], oracle.params['dfunc'])
        d, theta_rsfx = _rsfxmin(oracle, k, query[0], theta_k, k)
        P[ind][0] = d
        C[ind]+=theta_rsfx
     
    for i in range(1,N): # iterate over the rest of query
        for k in range(K): # iterate over the K possible paths
            _trn = oracle.trn[P[k][i-1]][:] 
            _trn.append(P[k][i-1])
            d_vec = []
            theta_vec = []
            for j in _trn:
                theta_i = get_distance(query[i], oracle.data[j], oracle.params['weights'], oracle.params['dfunc'])
                d_rsfx, theta_rsfx = _rsfxmin(oracle, j, query[i], theta_i, j)
                d_sfx, theta_sfx = _sfxmin(oracle, j, query[i], theta_i, j)
                if theta_sfx < theta_rsfx:
                    d_vec.append(d_sfx)
                    theta_vec.append(theta_sfx)
                else:
                    d_vec.append(d_rsfx)
                    theta_vec.append(theta_rsfx)
            C[k]+=np.min(theta_vec)                    
            P[k][i] = d_vec[np.argmin(theta_vec)]
    i_hat = np.argmin(C)
    return P,C,i_hat    


