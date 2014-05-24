#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

#
# Test transformations for linear duality
#

try:
    import new
except:
    import types as new
import os
import sys
import unittest
from os.path import abspath, dirname, normpath, join

currdir = dirname(abspath(__file__))
exdir = normpath(join(currdir,'..','..','..','doc','bilevel'))

from six import iteritems
import re
import pyutilib.services
import pyutilib.subprocess
import pyutilib.common
import pyutilib.th as unittest
from pyutilib.misc import setup_redirect, reset_redirect
try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False

import coopr.environ
import coopr.opt
import coopr.pyomo.scripting.pyomo as main
from coopr.pyomo.scripting.util import cleanup
from coopr.core.plugin import ExtensionPoint
from coopr.pyomo import *

solver = coopr.opt.load_solvers('cplex', 'glpk')


class CommonTests:

    def pyomo(self, *args, **kwds):
        args=list(args)
        args.append('-c')
        if 'solver' in kwds:
            args.append('--solver='+kwds['solver'])
        pproc = None
        if 'preprocess' in kwds:
            pp = kwds['preprocess']
            if pp == 'linear_dual':
                import coopr.bilevel.linear_dual
                pproc = coopr.bilevel.linear_dual.transform
        args.append('--symbolic-solver-labels')
        args.append('--save-results=result.yml')
        #args.append('--tempdir='+currdir)
        #args.append('--keepfiles')
        #args.append('--debug')
        #args.append('--verbose')
        os.chdir(currdir)

        print('***')
        pproc.activate()
        print("Activating " + kwds['preprocess'])
        print(' '.join(args))
        try:
            output = main.run(args)
        except:
            output = None
        cleanup()
        pproc.deactivate()
        print('***')
        return output

    def check(self, problem, solver):
        pass

    def referenceFile(self, problem, solver):
        return join(currdir, problem+'.txt')

    def getObjective(self, fname):
        FILE = open(fname)
        data = yaml.load(FILE)
        FILE.close()
        solutions = data.get('Solution', [])
        ans = []
        for x in solutions:
            ans.append(x.get('Objective', {}))
        return ans

    def updateDocStrings(self):
        for key in dir(self):
            if key.startswith('test'):
                getattr(self,key).__doc__ = " (%s)" % getattr(self,key).__name__

    def test_t5(self):
        self.problem='test_t5'
        self.pyomo( join(exdir,'t5.py'), preprocess='linear_dual' )
        self.check( 't5', 'linear_dual' )

    def test_t1(self):
        self.problem='test_t1'
        self.pyomo( join(exdir,'t1.py'), preprocess='linear_dual' )
        self.check( 't1', 'linear_dual' )

    def test_t2(self):
        self.problem='test_t2'
        self.pyomo( join(exdir,'t2.py'), preprocess='linear_dual' )
        self.check( 't2', 'linear_dual' )


class Reformulate(unittest.TestCase, CommonTests):

    def pyomo(self,  *args, **kwds):
        args = list(args)
        args.append('--save-model='+self.problem+'_result.lp')
        CommonTests.pyomo(self, *args, **kwds)

    def referenceFile(self, problem, solver):
        return join(currdir, problem+"_"+solver+'.lp')

    def check(self, problem, solver):
        self.assertFileEqualsBaseline( join(currdir,self.problem+'_result.lp'),
                                           self.referenceFile(problem,solver) )


class Solver(unittest.TestCase):

    def check(self, problem, solver):
        refObj = self.getObjective(self.referenceFile(problem,solver))
        ansObj = self.getObjective(join(currdir,'result.yml'))
        self.assertEqual(len(refObj), len(ansObj))
        for i in range(len(refObj)):
            self.assertEqual(len(refObj[i]), len(ansObj[i]))
            for key,val in iteritems(refObj[i]):
                self.assertEqual(val, ansObj[i].get(key,None))


@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(solver['glpk'] is None, "The 'glpk' executable is not available")
class Solve_GLPK(Solver, CommonTests):

    def pyomo(self,  *args, **kwds):
        kwds['solver'] = 'glpk'
        CommonTests.pyomo(self, *args, **kwds)


@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(solver['cplex'] is None, "The 'cplex' executable is not available")
class Solve_CPLEX(Solver, CommonTests):

    def pyomo(self,  *args, **kwds):
        kwds['solver'] = 'cplex'
        CommonTests.pyomo(self, *args, **kwds)


if __name__ == "__main__":
    unittest.main()
