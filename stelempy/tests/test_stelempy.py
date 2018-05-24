import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelempy import *
from testsets import *

import unittest

class test_calculate_stelements_single_stable_one_step(unittest.TestCase):
    def runTest(self):
        import stelempy as sp
        sp.default_rtol = 0.01
        self.assertEqual(calculate_stelements(SETS_1_IN), SETS_1_01_FOUT1)
        sp.default_rtol = 0.001

class test_calculate_stelements_single_stable_two_step(unittest.TestCase):
    def runTest(self):
        self.assertEqual(calculate_stelements(SETS_1_IN,
                                              num.RationalCompare1(0.01),2),
                        SETS_1_01_FOUT2)

class test_calculate_stelements_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        self.assertEqual(calculate_stelements(SETS_2_IN,
                                              num.RationalCompare1(0.01)),
                        SETS_2_01_FOUT1)


class test_calculate_convergence_groups_single_stable_one_step(unittest.TestCase):
    def runTest(self):
        convergence_groups = calculate_convergence_groups(SETS_1_IN,
                                                          SETS_1_01_FOUT1)
        self.assertEqual(convergence_groups, SETS_1_01_COUT1_POST)

class test_calculate_convergence_groups_single_stable_two_step(unittest.TestCase):
    def runTest(self):
        convergence_groups = calculate_convergence_groups(SETS_1_IN,
                                                          SETS_1_01_FOUT2)
        self.assertEqual(convergence_groups, SETS_1_01_COUT2_POST)

class test_calculate_convergence_groups_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        convergence_groups = calculate_convergence_groups(SETS_2_IN,
                                                          SETS_2_01_FOUT1)
        self.assertEqual(convergence_groups, SETS_2_01_COUT1_POST)



class test_calculateStelementsForQIs_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        ret = calculate_convergence_groups_range(SETS_2_IN)
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


class test_calculate_QIs_from_range_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        ret = calculate_convergence_groups_range(SETS_2_IN)
        ret = calculate_QIs_from_range(ret)
        self.assertEqual(ret, SETS_2_QI)

class test_calculate_QIs_from_range_amalgamation(unittest.TestCase):
    def runTest(self):
        ret = calculate_convergence_groups_range(SETS_3_IN)
        ret = calculate_QIs_from_range(ret, num.RationalCompare1(0.01))
        self.assertEqual(ret, SETS_3_QI_AMALAG)

class test_calculate_QIs(unittest.TestCase):
    def runTest(self):
        ret = calculate_QIs(SETS_3_IN, amalg_ratcmp=num.RationalCompare1(0.01))
        self.assertEqual(ret, SETS_3_QI_AMALAG)

if __name__ == "__main__":
    #Just for debug
    b = test_calculate_QIs_from_range_amalgamation()
    b.runTest()
