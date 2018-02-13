import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelempy import *
from testSets import *

import unittest

class test_calculateStelements_singleStable_oneStep(unittest.TestCase):
    def runTest(self):
        self.assertEqual(calculateStelements(SETS_1_IN,0.01), SETS_1_01_FOUT1)

class test_calculateStelements_singleStable_twoStep(unittest.TestCase):
    def runTest(self):
        self.assertEqual(calculateStelements(SETS_1_IN,0.01,2), SETS_1_01_FOUT2)

class test_calculateStelements_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        self.assertEqual(calculateStelements(SETS_2_IN,0.01), SETS_2_01_FOUT1)



class test_calculateConvergenceGroups_singleStable_oneStep(unittest.TestCase):
    def runTest(self):
        convergenceGroups = calculateConvergenceGroups(SETS_1_IN, SETS_1_01_FOUT1)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT1_POST)

class test_calculateConvergenceGroups_singleStable_twoStep(unittest.TestCase):
    def runTest(self):
        convergenceGroups = calculateConvergenceGroups(SETS_1_IN, SETS_1_01_FOUT2)
        self.assertEqual(convergenceGroups, SETS_1_01_COUT2_POST)

class test_calculateConvergenceGroups_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        convergenceGroups = calculateConvergenceGroups(SETS_2_IN, SETS_2_01_FOUT1)
        self.assertEqual(convergenceGroups, SETS_2_01_COUT1_POST)



class test_calculateStelementsForQIs_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        ret = calculateConvergenceGroupsRange(SETS_2_IN)
        self.assertEqual(ret[0][0], SETS_2_01_COUT1_POST)
        self.assertEqual(ret[0][1], SETS_2_001_COUT1_POST)
        self.assertEqual(ret[0][2], SETS_2_0001_COUT1_POST)
        self.assertEqual(ret[0][3], [])

        for i, nums in enumerate(ret[1]):
            self.assertEqual(nums[0], len(ret[0][i]))
        self.assertEqual(ret[1][0][1], 1)
        self.assertEqual(ret[1][1][1], 1)
        self.assertEqual(ret[1][2][1], 0)
        
        self.assertEqual(ret[2][0], 0.01)
        self.assertEqual(ret[2][1], 0.001)
        self.assertEqual(ret[2][2], 0.0001)
        self.assertEqual(ret[2][3], 0.00001)



class test_calculateQIs_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        ret = calculateConvergenceGroupsRange(SETS_2_IN)
        ret = calculateQIs(ret)
        self.assertEqual(ret, SETS_2_QI)

class test_calculateQIs_amalgamation(unittest.TestCase):
    def runTest(self):
        ret = calculateConvergenceGroupsRange(SETS_3_IN)
        ret = calculateQIs(ret, amalgThreshold=0.01)
        self.assertEqual(ret, SETS_2_QI)

if __name__ == "__main__":
    #Just for debug
    b = test_calculateQIs_amalgamation()
    b.runTest()
