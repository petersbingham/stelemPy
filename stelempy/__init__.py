from stelemFind import *
from stelemConverge import *

from sets import Set

default_starting_distThres = 0.01

def _combineGrps(oldConvGrps, newConvGrps):
    combinedConvGrps = {}
    for i in oldConvGrps:
        stelement = oldConvGrps[i]
        if stelement[2]!="LOST":
            combinedConvGrps[i] = stelement
    for i in newConvGrps:
        stelement = newConvGrps[i]
        if stelement[2]!="LOST":
            combinedConvGrps[i] = stelement
    return combinedConvGrps

# Two returns. First is group where close groups have been amalgamated.
# Second is the groups that have been amalgamated.
def _amalgamate(distinctConvGrps, amalgThres, ratCmp):
    if ratCmp is None:
        ratCmp = num.RationalCompare1(10**(-default_zeroValExp), amalgThres)
    newDistinctConvGrps = []
    combinedConvGrps = []
    combinedIndices = []
    for i in range(len(distinctConvGrps)):
        if i not in combinedIndices:
            if i<len(distinctConvGrps)-1:
                maxi1 = _getMaxIndex(distinctConvGrps[i][0])
                cmpkVal1 = distinctConvGrps[i][0][maxi1][0]
                iRepeat = False
                for j in range(i+1, len(distinctConvGrps)):
                    maxi2 = _getMaxIndex(distinctConvGrps[j][0])
                    cmpkVal2 = distinctConvGrps[j][0][maxi2][0]
                    if ratCmp.isClose(cmpkVal1, cmpkVal2):
                        if not iRepeat:
                            combinedConvGrps.append(distinctConvGrps[i])
                            iRepeat = True
                        combinedConvGrps.append(distinctConvGrps[j])
                        combinedIndices.append(j)
                        if maxi1 > maxi2:
                            convGrp = distinctConvGrps[i][0]
                        else:
                            convGrp = distinctConvGrps[j][0]
                        # Update calculations, using higher N:
                        dt_indices1 = distinctConvGrps[i][3]
                        dt_indices2 = distinctConvGrps[j][3]
                        dt_indices = _combineIndices(dt_indices1, dt_indices2)
                        u1 = distinctConvGrps[i][1]+distinctConvGrps[j][1]
                        u2 = distinctConvGrps[i][2]+distinctConvGrps[j][2]
                        distinctConvGrps[i] = [convGrp, u1, u2, dt_indices]
            newDistinctConvGrps.append(distinctConvGrps[i])
    return newDistinctConvGrps, combinedConvGrps

def _combineIndices(a, b):
    return list(Set(a).union(Set(b)))

def _calculateQIsFromRange(convGrps, distThress):  
    QIs = []
    convGrps.sort(key=lambda x: x[1], reverse=True)
    
    for convGrp in convGrps:
        smallestdk = distThress[max(convGrp[3])]
        maxi = _getMaxIndex(convGrp[0])
        QIs.append([convGrp[0][maxi][0], smallestdk, convGrp[2]])
    return QIs

def _getDistinctConvGrpIndex(distinctConvGrps, convGrp):
    for i in range(len(distinctConvGrps)):
        filtDistinctConvGrp = _filtOutLost(distinctConvGrps[i][0])
        filtIndices = filtDistinctConvGrp.keys()
        filtStelements = map(lambda x: x[0], filtDistinctConvGrp.values())
        found = True
        for j in sorted(convGrp.keys()):
            stelements = convGrp[j]
            if stelements[2]=="LOST":
                break
            elif j not in filtIndices or stelements[0] not in filtStelements:
                found = False
                break
        if found:
            return i
    return -1

def _filtOutLost(convGrp):
    nonLostStelements = {}
    for i in convGrp:
        stelement = convGrp[i]
        if stelement[2]!="LOST":
            nonLostStelements[i] = stelement
    return nonLostStelements

def _isConv(stelement):
    return stelement[2]!="LOST" and stelement[2]!="PRE"

def _getConvLen(convGrp):
    return sum(_isConv(stelement) for stelement in convGrp.values())
    
def _getMaxIndex(convGrp):
    imax = 0
    for i in convGrp:
        stelement = convGrp[i]
        if _isConv(stelement) and i>imax:
            imax = i
    return imax

########################################################################   
######################### Public Interface #############################
########################################################################

def calculateStelements(sets, distThres=default_distThres, 
                        cfSteps=default_cfSteps, ratCmp=None):
    s = stelemFind(distThres, cfSteps, ratCmp)
    return s.addSets(sets)
    
def calculateConvergenceGroups(sets, stelementsResults):
    s = stelemConverger(sets, stelementsResults)
    convergenceGroups = s.createConvergenceGroups()
    s.writePriorElements(convergenceGroups)
    s.setClosestElementToLost(convergenceGroups)
    return convergenceGroups

def calculateQIs(sets, startingDistThres=default_starting_distThres,
                 endDistThres=None, cfSteps=default_cfSteps, amalgThres=0.,
                 ratCmp=None):
    ret = calculateConvergenceGroupsRange(sets, startingDistThres, endDistThres,
                                          cfSteps, ratCmp)
    return calculateQIsFromRange(ret, amalgThres, ratCmp)


# Following two functions are the two steps used for the calculateQIs. They have
# been made public since the intermediate calculations may be of interest.
def calculateConvergenceGroupsRange(sets, 
                                    startingDistThres=default_starting_distThres, 
                                    endDistThres=None, cfSteps=default_cfSteps, 
                                    ratCmp=None):
    tabCounts = []
    convergenceGroupsRange = []
    distThress = []

    distThres = startingDistThres    
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

        stop = (endDistThres is not None and distThres < endDistThres*1.1)
        if sf.totStelements != 0 and not stop:
            distThres /= 10.0
        else:
            break

    return convergenceGroupsRange, tabCounts, distThress

def calculateQIsFromRange(convergenceGroupsRangeRet, amalgThres=0., ratCmp=None):
    convergenceGroupsRange = convergenceGroupsRangeRet[0]
    distThress = convergenceGroupsRangeRet[2]
    
    distinctConvGrps = []
    for i_dt in range(len(distThress)):
        convGrps = convergenceGroupsRange[i_dt]
        if len(convGrps) > 0:
            convLens =  map(lambda convGrp: _getConvLen(convGrp), convGrps)
            totConvLen = sum(convLens)

            for convGrp,convLen in zip(convGrps,convLens):
                convLenRatio = float(convLen)/totConvLen
                
                i = _getDistinctConvGrpIndex(distinctConvGrps, convGrp)
                if i == -1:
                    distinctConvGrp = [convGrp, convLenRatio, convLen, [i_dt]]
                    distinctConvGrps.append( distinctConvGrp )
                else:
                    #Update set:
                    oldConvGrp = distinctConvGrps[i][0]
                    convLenRatio += distinctConvGrps[i][1]
                    convLen += distinctConvGrps[i][2]
                    dt_indices = distinctConvGrps[i][3]
                    if i_dt not in dt_indices:
                        dt_indices.append(i_dt)
                    distinctConvGrps[i][0] = _combineGrps(oldConvGrp, convGrp)
                    distinctConvGrps[i][1] = convLenRatio
                    distinctConvGrps[i][2] = convLen
                    distinctConvGrps[i][3] = dt_indices
    if amalgThres > 0.:
        distinctConvGrps, combinedConvGrps = _amalgamate(distinctConvGrps, 
                                                         amalgThres, ratCmp)
    ret_a = _calculateQIsFromRange(distinctConvGrps, distThress)
    ret_b = None
    if amalgThres > 0.:
        ret_b = _calculateQIsFromRange(combinedConvGrps, distThress)
    return ret_a, ret_b