from stelemFind import *
from stelemConverge import *

from sets import Set

DEFAULT_STARTING_DISTHRES = 0.01

def calculateStelements(sets, distThres=DEFAULT_DISTHRES, cfSteps=DEFAULT_CFSTEPS, ratCmp=None):
    s = stelemFind(distThres, cfSteps, ratCmp)
    return s.addSets(sets)
    
def calculateConvergenceGroups(sets, stelementsResults):
    s = stelemConverger(sets, stelementsResults)
    convergenceGroups = s.createConvergenceGroups()
    s.writePriorElements(convergenceGroups)
    s.setClosestElementToLost(convergenceGroups)
    return convergenceGroups

def calculateConvergenceGroupsRange(sets, startingDistThreshold=DEFAULT_STARTING_DISTHRES, endDistThreshold=None, cfSteps=DEFAULT_CFSTEPS, ratCmp=None):
    tabCounts = []
    convergenceGroupsRange = []
    distThress = []

    distThres = startingDistThreshold    
    while True:
        distThress.append(distThres)

        sf = stelemFind(distThres, cfSteps, ratCmp)   
        stelementsResults = sf.addSets(sets)
        tabCounts.append((sf.totStelements, sf.totLostStelements))

        sc = stelemConverger(sets, stelementsResults)
        convergenceGroups = sc.createConvergenceGroups()
        sc.writePriorElements(convergenceGroups)
        sc.setClosestElementToLost(convergenceGroups)
        convergenceGroupsRange.append(convergenceGroups)

        if sf.totStelements != 0 and (endDistThreshold is None or distThres > endDistThreshold*1.1):
            distThres /= 10.0
        else:
            break
        
    return convergenceGroupsRange, tabCounts, distThress

def calculateQIs(convergenceGroupsRangeReturn, amalgThreshold=0., ratCmp=None):
    return _writePoleCalculationTable(convergenceGroupsRangeReturn, amalgThreshold, ratCmp)


def _writePoleCalculationTable(convergenceGroupsRangeReturn, amalgThreshold, ratCmp):
    poleSetsList = convergenceGroupsRangeReturn[0]
    distThress = convergenceGroupsRangeReturn[2]
    
    uniquePoleSets = []
    lenPiSumkSumi = 0.0
    totPoleCnts = 0.0
    for i_dk in range(len(poleSetsList)):
        poleSets = poleSetsList[i_dk]
        if len(poleSets) > 0:
            lenPiSumk = reduce(lambda x,y: x+y, map(lambda poleSet: _getLenpi(poleSet), poleSets))
            lenPiSumkSumi += lenPiSumk
            for poleSet in poleSets:
                i = _getUniquePoleSetIndex(uniquePoleSets, poleSet)
                
                lenPi = _getLenpi(poleSet)
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
                    uniquePoleSets[i] = [_combinePoleSets(oldPoleSet, poleSet), q1_inter_old+q1_inter, q2_inter_old+q2_inter, q5_inter] #Update pole set
    if amalgThreshold > 0:
        uniquePoleSets, combinedPoleSets = _combineUniquePoleSets(uniquePoleSets, amalgThreshold, ratCmp)
    ret_a = _writeTable(uniquePoleSets, distThress)
    ret_b = None
    if amalgThreshold > 0:
        ret_b = _writeTable(combinedPoleSets, distThress)
    return ret_a, ret_b

def _combinePoleSets(oldPoleSet, newPoleSet):
    combinedPoleSet = {}
    for N in oldPoleSet:
        pole = oldPoleSet[N]
        if pole[2]!="LOST":
            combinedPoleSet[N] = pole
    for N in newPoleSet:
        pole = newPoleSet[N]
        if pole[2]!="LOST":
            combinedPoleSet[N] = pole
    return combinedPoleSet

# Produces two tables. The fist is named ...PREVALENCE.tab and contains tables of amalgamated poles, with updated calculations.
# The second is only a partial table, named PREVALENCECOMB.tab, to indicate the poles that have been combined.
def _combineUniquePoleSets(uniquePoleSets, amalgThreshold, ratCmp):
    if ratCmp is None:
        ratCmp = num.RationalCompare(10**(-DEFAULT_ZEROVALEXP), amalgThreshold)
    newUniquePoleSets = []
    combinedPoleSets = []
    combinedIndices = []
    for i in range(len(uniquePoleSets)):
        if i not in combinedIndices:
            if i<len(uniquePoleSets)-1:
                Nmax1 = _getMaxNInPoleSet(uniquePoleSets[i][0])
                cmpkVal1 = uniquePoleSets[i][0][Nmax1][0]
                iRepeat = False
                for j in range(i+1, len(uniquePoleSets)):
                    Nmax2 = _getMaxNInPoleSet(uniquePoleSets[j][0])
                    cmpkVal2 = uniquePoleSets[j][0][Nmax2][0]
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
                        q5_inter = list(Set(uniquePoleSets[i][3]).union(Set(uniquePoleSets[j][3])))
                        # Update the calculations, using the pole set at the higher N.
                        uniquePoleSets[i] = [poleSet, uniquePoleSets[i][1]+uniquePoleSets[j][1], uniquePoleSets[i][2]+uniquePoleSets[j][2], q5_inter]
            newUniquePoleSets.append(uniquePoleSets[i])
    return newUniquePoleSets, combinedPoleSets
        
def _writeTable(uniquePoleSets, distThress):  
    tabValues = []
    uniquePoleSets.sort(key=lambda x: x[1], reverse=True)
    
    for uniquePoleSet in uniquePoleSets:
        smallestdk = distThress[max(uniquePoleSet[3])]
        Nmax = _getMaxNInPoleSet(uniquePoleSet[0])
        tabValues.append([uniquePoleSet[0][Nmax][0], smallestdk, uniquePoleSet[2]])
    return tabValues

def _getUniquePoleSetIndex(uniquePoleSets, poleSet):
    for i in range(len(uniquePoleSets)):
        uniquePoleSet = _getPolesInPoleSet(uniquePoleSets[i][0])
        found = True
        for N in sorted(poleSet.keys()):
            pole = poleSet[N]
            if pole[2]=="LOST":
                break
            elif N not in uniquePoleSet.keys() or pole[0] not in map(lambda x: x[0], uniquePoleSet.values()):
                found = False
                break
        if found:
            return i
    return -1

def _getPolesInPoleSet(poleSet):
    nonLostPoles = {}
    for N in poleSet:
        pole = poleSet[N]
        if pole[2]!="LOST":
            nonLostPoles[N] = pole
    return nonLostPoles

def _getLenpi(poleSet):
    return sum((pole[2]!="LOST" and pole[2]!="PRE") for pole in poleSet.values())
    
def _getMaxNInPoleSet(poleSet):
    Nmax = 0
    for N in poleSet:
        pole = poleSet[N]
        if (pole[2]!="LOST" and pole[2]!="PRE") and N>Nmax:
            Nmax = N
    return Nmax
