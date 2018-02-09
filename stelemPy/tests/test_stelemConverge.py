import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelemPy.stelemConverge import *
from sets import *

import unittest

class test_singleStable_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_1_IN, SETS_1_FOUT1)
        cpoleSets = s.createPoleSets()
        self.assertEqual(cpoleSets, SETS_1_COUT1)
        s.writePriorRoots(cpoleSets)
        self.assertEqual(cpoleSets, SETS_1_COUT1_PRE)
        s.setClosestRootToLost(cpoleSets)
        self.assertEqual(cpoleSets, SETS_1_COUT1_POST)

class test_singleStable_twoStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_1_IN, SETS_1_FOUT2)
        cpoleSets = s.createPoleSets()
        self.assertEqual(cpoleSets, SETS_1_COUT2)
        s.writePriorRoots(cpoleSets)
        self.assertEqual(cpoleSets, SETS_1_COUT2_PRE)
        s.setClosestRootToLost(cpoleSets)
        self.assertEqual(cpoleSets, SETS_1_COUT2_POST)

class test_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_2_IN, SETS_2_FOUT1)
        cpoleSets = s.createPoleSets()
        self.assertEqual(cpoleSets, SETS_2_COUT1)
        s.writePriorRoots(cpoleSets)
        self.assertEqual(cpoleSets, SETS_2_COUT1_PRE)
        s.setClosestRootToLost(cpoleSets)
        self.assertEqual(cpoleSets, SETS_2_COUT1_POST)


if __name__ == "__main__":
    #Just for debug
    b = test_twoStable_oneLost_oneStep()
    b.runTest()
