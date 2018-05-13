import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelempy.stelemfind import *
from testsets import *

import unittest

class test_single_stable_one_step(unittest.TestCase):
    def runTest(self):
        s = StelemFind(0.01)
        self.assertEqual(s.add_sets(SETS_1_IN), SETS_1_01_FOUT1)
        self.assertEqual(s.tot_stelements, 1)
        self.assertEqual(s.tot_lost_stelements, 0)

class test_single_stable_two_step(unittest.TestCase):
    def runTest(self):
        s = StelemFind(0.01, 2)
        self.assertEqual(s.add_sets(SETS_1_IN), SETS_1_01_FOUT2)
        self.assertEqual(s.tot_stelements, 1)
        self.assertEqual(s.tot_lost_stelements, 0)

class test_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        s = StelemFind(0.01)
        self.assertEqual(s.add_sets(SETS_2_IN), SETS_2_01_FOUT1)
        self.assertEqual(s.tot_stelements, 2)
        self.assertEqual(s.tot_lost_stelements, 1)

if __name__ == "__main__":
    #Just for debug
    b = test_two_stable_one_lost_one_step()
    b.runTest()
