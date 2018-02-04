import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelemPy import *

import unittest

class example_testcase(unittest.TestCase):
    def runTest(self):
        self.assertTrue(True)

if __name__ == "__main__":
    #Just for debug
    b = example_testcase()
    b.runTest()
    