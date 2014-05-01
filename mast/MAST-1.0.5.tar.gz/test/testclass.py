import os
import sys

class MyClass:
    def __init__(self, mynum=0):
        self.mynum=mynum
        self.mycalc=None
        if mynum>10:
            print "Mynum %i > 10" % self.mynum
            import pymatgen
            self.mycalc = pymatgen.io.vaspio.Poscar()
            print "pymatgen imported"
    def poscar(self):
        mypos = self.mycalc.from_file("//home/tam/test_df/POSCAR_perfect")
        print mypos

