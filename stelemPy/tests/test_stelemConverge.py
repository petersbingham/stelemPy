import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelemPy.stelemConverge import *
from testSets import *

import unittest

class test_singleStable_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_1_IN, SETS_1_01_FOUT1)
        convergenceGroups = s.createConvergenceGroups()
        self.assertEqual(convergenceGroups, SETS_1_01_COUT1)
        s.writePriorElements(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT1_PRE)
        s.setClosestElementToLost(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT1_POST)

class test_singleStable_twoStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_1_IN, SETS_1_01_FOUT2)
        convergenceGroups = s.createConvergenceGroups()
        self.assertEqual(convergenceGroups, SETS_1_01_COUT2)
        s.writePriorElements(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT2_PRE)
        s.setClosestElementToLost(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT2_POST)

class test_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemConverger(SETS_2_IN, SETS_2_01_FOUT1)
        convergenceGroups = s.createConvergenceGroups()
        self.assertEqual(convergenceGroups, SETS_2_01_COUT1)
        s.writePriorElements(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_2_01_COUT1_PRE)
        s.setClosestElementToLost(convergenceGroups)
        self.assertEqual(convergenceGroups, SETS_2_01_COUT1_POST)


if __name__ == "__main__":
    #Just for debug
    b = test_twoStable_oneLost_oneStep()
    b.runTest()
