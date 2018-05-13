import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelempy.stelemconverge import *
from testsets import *

import unittest

class test_single_stable_one_step(unittest.TestCase):
    def runTest(self):
        s = StelemConverger(SETS_1_IN, SETS_1_01_FOUT1)
        convergence_groups = s.create_convergence_groups()
        self.assertEqual(convergence_groups, SETS_1_01_COUT1)
        s.write_prior_elements(convergence_groups)
        self.assertEqual(convergence_groups, SETS_1_01_COUT1_PRE)
        s.set_closest_element_to_lost(convergence_groups)
        self.assertEqual(convergence_groups, SETS_1_01_COUT1_POST)

class test_single_stable_two_step(unittest.TestCase):
    def runTest(self):
        s = StelemConverger(SETS_1_IN, SETS_1_01_FOUT2)
        convergence_groups = s.create_convergence_groups()
        self.assertEqual(convergence_groups, SETS_1_01_COUT2)
        s.write_prior_elements(convergence_groups)
        self.assertEqual(convergence_groups, SETS_1_01_COUT2_PRE)
        s.set_closest_element_to_lost(convergence_groups)
        self.assertEqual(convergence_groups, SETS_1_01_COUT2_POST)

class test_two_stable_one_lost_one_step(unittest.TestCase):
    def runTest(self):
        s = StelemConverger(SETS_2_IN, SETS_2_01_FOUT1)
        convergence_groups = s.create_convergence_groups()
        self.assertEqual(convergence_groups, SETS_2_01_COUT1)
        s.write_prior_elements(convergence_groups)
        self.assertEqual(convergence_groups, SETS_2_01_COUT1_PRE)
        s.set_closest_element_to_lost(convergence_groups)
        self.assertEqual(convergence_groups, SETS_2_01_COUT1_POST)


if __name__ == "__main__":
    #Just for debug
    b = test_two_stable_one_lost_one_step()
    b.runTest()
