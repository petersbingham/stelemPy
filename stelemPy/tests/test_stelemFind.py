import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelemPy.stelemFind import *
from sets import *

import unittest

class test_singleStable_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemFind(0.01)
        self.assertEqual(s.addSets(SETS_1_IN), SETS_1_FOUT1)
        self.assertEqual(s.totStelements, 1)
        self.assertEqual(s.totLostStelements, 0)

class test_singleStable_twoStep(unittest.TestCase):
    def runTest(self):
        s = stelemFind(0.01, 2)
        self.assertEqual(s.addSets(SETS_1_IN), SETS_1_FOUT2)
        self.assertEqual(s.totStelements, 1)
        self.assertEqual(s.totLostStelements, 0)

class test_twoStable_oneLost_oneStep(unittest.TestCase):
    def runTest(self):
        s = stelemFind(0.01)
        self.assertEqual(s.addSets(SETS_2_IN), SETS_2_FOUT1)
        self.assertEqual(s.totStelements, 2)
        self.assertEqual(s.totLostStelements, 1)

if __name__ == "__main__":
    #Just for debug
    b = example_testcase()
    b.runTest()
