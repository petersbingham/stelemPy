import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

from stelemPy.stelemFind import *

import unittest

class test_singleStable_oneStep(unittest.TestCase):
    def getElement(self, i):
        if i == 0:
            return [1.01,2.,3.,4.]
        if i == 1:
            return [5.,1.001,6.,7.]
        if i == 2:
            return [8.,9.,1.0001,10.]

    def runTest(self):
        s = stelemFind(0.01,self.getElement,3)
        r = s.getResults()
        #print r

        # Test all the lengths:
        self.assertTrue(len(r)==3)
        for i in range(3):
            self.assertTrue(len(r[i])==3)

        self.assertTrue(len(r[0][0])==0)
        self.assertTrue(len(r[0][1])==1)
        self.assertTrue(len(r[0][2])==1)

        self.assertTrue(len(r[1][0])==0)
        self.assertTrue(len(r[1][1])==1)
        self.assertTrue(len(r[1][2])==1)

        self.assertTrue(len(r[2][0])==0)
        self.assertTrue(len(r[2][1])==1)
        self.assertTrue(len(r[2][2])==1)

        self.assertTrue(r[0][1][0]==1.001)
        self.assertTrue(r[0][2][0]==1.0001)

        self.assertTrue(r[1][1][0]==[(1, 1), (0, 0)])
        self.assertTrue(r[1][2][0]==[(2, 2), (1, 1)])

        self.assertTrue(r[2][1][0]=='NEW')
        self.assertTrue(r[2][2][0]=='')

        self.assertTrue(s.totStelements==1)
        self.assertTrue(s.totLostStelements==0)


class test_twoStable_oneLost_oneStep(unittest.TestCase):
    def getElement(self, i):
        if i == 0:
            return [1.01,2.01,3.,4.,5]
        if i == 1:
            return [6.,2.001,1.001,7.,8.]
        if i == 2:
            return [9.,10.,1.0001,11.,2.0001]
        if i == 3:
            return [12.,13.,1.00001,14.,15.]

    def runTest(self):
        s = stelemFind(0.01,self.getElement,4)
        r = s.getResults()
        #print
        #for i in range(3): 
        #    print r[i]
        
        # Test all the lengths:
        self.assertTrue(len(r)==3)
        for i in range(3):
            self.assertTrue(len(r[i])==4)

        self.assertTrue(len(r[0][0])==0)
        self.assertTrue(len(r[0][1])==2)
        self.assertTrue(len(r[0][2])==2)
        self.assertTrue(len(r[0][3])==2)

        self.assertTrue(len(r[1][0])==0)
        self.assertTrue(len(r[1][1])==2)
        self.assertTrue(len(r[1][2])==2)
        self.assertTrue(len(r[1][3])==2)

        self.assertTrue(len(r[2][0])==0)
        self.assertTrue(len(r[2][1])==2)
        self.assertTrue(len(r[2][2])==2)
        self.assertTrue(len(r[2][3])==2)

        self.assertTrue(r[0][1]==[2.001,1.001])
        self.assertTrue(r[0][2]==[2.0001,1.0001])
        self.assertTrue(r[0][3]==[2.0001,1.00001])

        self.assertTrue(r[1][1]==[[(1, 1), (0, 1)], [(1, 2), (0, 0)]])
        self.assertTrue(r[1][2]==[[(2, 4), (1, 1)], [(2, 2), (1, 2)]])
        self.assertTrue(r[1][3]==[[(2, 4), (1, 1)], [(3, 2), (2, 2)]])

        self.assertTrue(r[2][1]==['NEW', 'NEW'])
        self.assertTrue(r[2][2]==['', ''])
        self.assertTrue(r[2][3]==['LOST ', ''])

        self.assertTrue(s.totStelements==2)
        self.assertTrue(s.totLostStelements==1)

class test_singleStable_twoStep(unittest.TestCase):
    def getElement(self, i):
        if i == 0:
            return [1.01,2.,3.,4.]
        if i == 1:
            return [5.,1.001,6.,7.]
        if i == 2:
            return [8.,9.,1.0001,10.]

    def runTest(self):
        s = stelemFind(0.01,self.getElement,3,cfSteps=2)
        r = s.getResults()
        #print r

        # Test all the lengths:
        self.assertTrue(len(r)==3)
        for i in range(3):
            self.assertTrue(len(r[i])==3)

        self.assertTrue(len(r[0][0])==0)
        self.assertTrue(len(r[0][1])==0)
        self.assertTrue(len(r[0][2])==1)

        self.assertTrue(len(r[1][0])==0)
        self.assertTrue(len(r[1][1])==0)
        self.assertTrue(len(r[1][2])==1)

        self.assertTrue(len(r[2][0])==0)
        self.assertTrue(len(r[2][1])==0)
        self.assertTrue(len(r[2][2])==1)

        self.assertTrue(r[0][2][0]==1.0001)

        self.assertTrue(r[1][2][0]==[(2, 2), (1, 1), (0, 0)])

        self.assertTrue(r[2][2][0]=='NEW')

        self.assertTrue(s.totStelements==1)
        self.assertTrue(s.totLostStelements==0)

if __name__ == "__main__":
    #Just for debug
    b = example_testcase()
    b.runTest()
