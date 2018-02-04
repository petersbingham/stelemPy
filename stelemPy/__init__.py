import copy
import math
import sets

from polefinder import *
from poleconverger import *
from globalSettings import *
from general import *
import general.numerical as num

CALCULATIONS = ["Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]


class PoleMetaCalculator:
    def __init__(self, startIndex, endIndex, offset, endLock, mode, cfSteps, startingDistThreshold, amalgThreshold, zeroValExp, Nmin, Nmax, resultFileHandler, endDistThreshold=None):
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.offset = offset
        self.endLock = endLock
        self.mode = mode
        self.cfSteps = cfSteps
        self.startingDistThreshold = startingDistThreshold
        self.amalgThreshold = amalgThreshold
        self.zeroValExp = zeroValExp
        self.Nmin = Nmin
        self.Nmax = Nmax
        self.endDistThreshold = endDistThreshold
        self.resultFileHandler = resultFileHandler
        self.resultFileHandler.setDistThresholdEnd(endDistThreshold)
        self.distThresholds = {k:[] for k in self.cfSteps}
        self.allDistThresholds = []

    def doPoleCalculations(self, smats, kCal, mode, populateSmatCB=None, ratkCal=None, cmpPole=None):
        if len(smats) <= self.endIndex:
            raise Exception("Specified End Index outside range.")
        if self.startIndex < 0:
            raise Exception("Specified Start Index less than zero.")
        tabCounts = {}
        poleSetsDict = {}
        self.errState = False
        for cfSteps in self.cfSteps:
            tabCounts[cfSteps] = []
            poleSetsDict[cfSteps] = []
            distThreshold = self.startingDistThreshold
            while True:
                self.distThresholds[cfSteps].append(distThreshold)
                if distThreshold not in self.allDistThresholds:
                    self.allDistThresholds.append(distThreshold)
                pf = PoleFinder(copy.deepcopy(smats), kCal, self.resultFileHandler, self.startIndex, self.endIndex, self.offset, self.endLock, distThreshold, cfSteps, cmpPole, mode, populateSmatCB, zeroValExp=self.zeroValExp, Nmin=self.Nmin, Nmax=self.Nmax, ratkCal=ratkCal)
                self.errState = self.errState | pf.errState
                if not self.errState:
                    tabCounts[cfSteps].append((pf.NmaxTotPoles, pf.NmaxLostPoles))
                    pc = PoleConverger(self.resultFileHandler, self.Nmin, self.Nmax)
                    pc.createPoleTable()
                    poleSetsDict[cfSteps].append(pc.poleSets)
                    if pf.NmaxTotPoles != 0 and (self.endDistThreshold is None or distThreshold > (self.endDistThreshold + self.endDistThreshold/10.0)):
                        distThreshold /= 10.0
                    else:
                        break
        if not self.errState:
            self.resultFileHandler.setPoleMetaCalcParameters(self.amalgThreshold, self.Nmin, self.Nmax)
            self._writePoleCountTables(tabCounts, self.resultFileHandler)
            self._writePoleCalculationTable(poleSetsDict, self.resultFileHandler)
            
    def _writePoleCountTables(self, tabCounts, resultFileHandler):
        tabHeader = ["dk"]
        for cfSteps in self.cfSteps:
            if cfSteps == 1:
                tabHeader.append(str(cfSteps)+" Step")
            else:
                tabHeader.append(str(cfSteps)+" Steps")
             
        tabValues = []
        for id in range(len(self.allDistThresholds)):
            tabRow = [num.format_e(self.allDistThresholds[id]) + NOTABULATEFORMAT]
            for cfSteps in self.cfSteps:
                if id < len(tabCounts[cfSteps]):
                    if tabCounts[cfSteps][id][1] > 0:
                        tabRow.append(str(tabCounts[cfSteps][id][0])+"("+str(tabCounts[cfSteps][id][1])+")")
                    else:
                        tabRow.append(str(tabCounts[cfSteps][id][0]))
                else:
                    tabRow.append("-")
            tabValues.append(tabRow)
                
        outStr = getFormattedHTMLTable(tabValues, tabHeader, stralign="center", numalign="center", border=True)
        with open(resultFileHandler.getPoleCountTablePath(), 'w+') as f:
            f.write(outStr)
        print outStr

    def _writePoleCalculationTable(self, poleSetsDict, resultFileHandler):   
        for cfSteps in poleSetsDict:
            poleSetsList = poleSetsDict[cfSteps]
            uniquePoleSets = []
            kTOT = 0.0
            lenPiSumkSumi = 0.0
            totPoleCnts = 0.0
            for i_dk in range(len(poleSetsList)):
                poleSets = poleSetsList[i_dk]
                if len(poleSets) > 0:
                    kTOT += 1
                    lenPiSumk = reduce(lambda x,y: x+y, map(lambda poleSet: self._getLenpi(poleSet), poleSets))
                    lenPiSumkSumi += lenPiSumk
                    for poleSet in poleSets:
                        i = self._getUniquePoleSetIndex(uniquePoleSets, poleSet)
                        
                        lenPi = self._getLenpi(poleSet)
                        q1_inter = float(lenPi)/lenPiSumk
                        q2_inter = lenPi
                        totPoleCnts += 1.0
                        
                        if i == -1:
                            uniquePoleSets.append( [poleSet, q1_inter, q2_inter, [i_dk]] )
                        else:
                            oldPoleSet = uniquePoleSets[i][0]
                            q1_inter_old = uniquePoleSets[i][1]
                            q2_inter_old = uniquePoleSets[i][2]
                            q5_inter = uniquePoleSets[i][3]
                            if i_dk not in q5_inter:
                                q5_inter.append(i_dk)
                            uniquePoleSets[i] = [self._combinePoleSets(oldPoleSet, poleSet), q1_inter_old+q1_inter, q2_inter_old+q2_inter, q5_inter] #Update pole set
            if self.amalgThreshold > 0:
                uniquePoleSets, combinedPoleSets = self._combineUniquePoleSets(uniquePoleSets)
            self._writeTable(resultFileHandler.getPolePrevalenceTablePath, cfSteps, uniquePoleSets, kTOT, lenPiSumkSumi, totPoleCnts)
            if self.amalgThreshold > 0:
                self._writeTable(resultFileHandler.getCombinedPolePrevalenceTablePath, cfSteps, combinedPoleSets, kTOT, lenPiSumkSumi, totPoleCnts)
    
    def _combinePoleSets(self, oldPoleSet, newPoleSet):
        combinedPoleSet = {}
        for N in oldPoleSet:
            pole = oldPoleSet[N]
            if not pole.isLost:
                combinedPoleSet[N] = pole
        for N in newPoleSet:
            pole = newPoleSet[N]
            if not pole.isLost:
                combinedPoleSet[N] = pole
        return combinedPoleSet
    
    # Produces two table. The fist is named ...PREVALENCE.tab and contains tables of amalgamated poles, with up dataed calculations.
    # The second is only a partial table, named PREVALENCECOMB.tab, to indicate the poles that have been combined.
    def _combineUniquePoleSets(self, uniquePoleSets):
        zeroValue = 10**(-self.zeroValExp)
        ratCmp = num.RationalCompare(zeroValue, self.amalgThreshold)
        newUniquePoleSets = []
        combinedPoleSets = []
        combinedIndices = []
        for i in range(len(uniquePoleSets)):
            if i not in combinedIndices:
                if i<len(uniquePoleSets)-1:
                    Nmax1 = self._getMaxNInPoleSet(uniquePoleSets[i][0])
                    cmpkVal1 = uniquePoleSets[i][0][Nmax1].k
                    iRepeat = False
                    for j in range(i+1, len(uniquePoleSets)):
                        Nmax2 = self._getMaxNInPoleSet(uniquePoleSets[j][0])
                        cmpkVal2 = uniquePoleSets[j][0][Nmax2].k
                        if ratCmp.isClose(cmpkVal1, cmpkVal2):
                            if not iRepeat:
                                combinedPoleSets.append(uniquePoleSets[i])
                                iRepeat = True
                            combinedPoleSets.append(uniquePoleSets[j])
                            combinedIndices.append(j)
                            if Nmax1 > Nmax2:
                                poleSet = uniquePoleSets[i][0]
                            else:
                                poleSet = uniquePoleSets[j][0]
                            q5_inter = list(sets.Set(uniquePoleSets[i][3]).union(sets.Set(uniquePoleSets[j][3])))
                            # Update the calculations, using the pole set at the higher N.
                            uniquePoleSets[i] = [poleSet, uniquePoleSets[i][1]+uniquePoleSets[j][1], uniquePoleSets[i][2]+uniquePoleSets[j][2], q5_inter]
                newUniquePoleSets.append(uniquePoleSets[i])
        return newUniquePoleSets, combinedPoleSets
            
    def _writeTable(self, fileFun, cfSteps, uniquePoleSets, kTOT, lenPiSumkSumi, totPoleCnts):
        if self.mode == DOUBLE_N:
            nTOT = math.log(self.Nmax,2.0) - math.log(self.Nmin,2.0) + 1.0
        else:
            nTOT = self.Nmax/2.0 - self.Nmin/2.0 + 1.0        
        tabValues = []
        uniquePoleSets.sort(key=lambda x: x[1], reverse=True)
        
        tabHeader = ["pole.E.real", "pole.E.imag", "Smallest dk", "Total n Range"]
        #tabHeader = ["pole.E.real", "pole.E.imag", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"] # Some of these are experimental quantities.
        for uniquePoleSet in uniquePoleSets:
            Nmax = self._getMaxNInPoleSet(uniquePoleSet[0])
            q1 = str(uniquePoleSet[1]/kTOT) + NOTABULATEFORMAT
            q2 = str(uniquePoleSet[2]) + NOTABULATEFORMAT
            q3 = str(uniquePoleSet[2]/nTOT) + NOTABULATEFORMAT
            q4 = str(uniquePoleSet[2]/lenPiSumkSumi) + NOTABULATEFORMAT
            q5 = str(len(uniquePoleSet[3])) + NOTABULATEFORMAT
            q6 = str(len(uniquePoleSet[3])/nTOT) + NOTABULATEFORMAT
            q7 = str(len(uniquePoleSet[3])/totPoleCnts) + NOTABULATEFORMAT
            smallestdk = num.format_e(self.distThresholds[cfSteps][max(uniquePoleSet[3])]) + NOTABULATEFORMAT
            tabValues.append([formatRoot(uniquePoleSet[0][Nmax].E.real), formatRoot(uniquePoleSet[0][Nmax].E.imag), smallestdk, q2])
            #tabValues.append([formatRoot(uniquePoleSet[0][Nmax].E.real), formatRoot(uniquePoleSet[0][Nmax].E.imag), q1, q2, q3, q4, q5, q6, q7])
            
        outStr = getFormattedHTMLTable(tabValues, tabHeader, floatFmtFigs=DISPLAY_DIFFPRECISION, stralign="center", numalign="center", border=True)
        with open(fileFun(cfSteps), 'w+') as f:
            f.write(outStr)
    
    def _getUniquePoleSetIndex(self, uniquePoleSets, poleSet):
        for i in range(len(uniquePoleSets)):
            uniquePoleSet = self._getPolesInPoleSet(uniquePoleSets[i][0])
            found = True
            for N in sorted(poleSet.keys()):
                pole = poleSet[N]
                if pole.isLost:
                    break
                elif N not in uniquePoleSet.keys() or pole not in uniquePoleSet.values():
                    found = False
                    break
            if found:
                return i
        return -1
    
    def _getPolesInPoleSet(self, poleSet):
        nonLostPoles = {}
        for N in poleSet:
            pole = poleSet[N]
            if not pole.isLost:
                nonLostPoles[N] = pole
        return nonLostPoles
    
    def _getLenpi(self, poleSet):
        return sum(not pole.isLost for pole in poleSet.values())
    
    def _getMaxNInPoleSet(self, poleSet):
        Nmax = 0
        for N in poleSet:
            pole = poleSet[N]
            if not pole.isLost and N>Nmax:
                Nmax = N
        return Nmax
                       