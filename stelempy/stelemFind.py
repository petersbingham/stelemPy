import pynumutil as num

DEFAULT_ZEROVALEXP = 7
DEFAULT_DISTHRES = 0.001
DEFAULT_CFSTEPS = 1

class stelemFind:
    def __init__(self, distThres=DEFAULT_DISTHRES, cfSteps=DEFAULT_CFSTEPS, 
                 ratCmp=None):
        self.distThres = distThres
        self.cfSteps = cfSteps

        self.ratCmp = ratCmp
        if self.ratCmp is None:
            self.ratCmp = num.rationalCompare1(10**(-DEFAULT_ZEROVALEXP))
        self.lastSet = []
        self.allSets = []

        self.allStelements = []
        self.allStelementsHist = []

        self.lastStelements = []
        self.lostIndices = []
        self.totStelements = 0
        self.totLostStelements = 0
        self.newIndex = -1

    def addSets(self, sets):
        resultSets = []
        for set in sets:
            resultSets.append(self._locateStelements(set))
        return resultSets

    def addSet(self, set):
        return self._locateStelements(set)

#######################################################
#######################################################

    def _locateStelements(self, set):
        si = len(self.allSets)
        newStelements = []
        newStelementsLastElements = []
        newStelementsInfoStrs = []
        lastStelementElementIndices = ()
        if len(self.lastStelements) > 0:
            lastStelementElementIndices = zip(*self.lastStelements)[0]
        if si >= self.cfSteps:  
            for i in range(len(set)):
                element = set[i]
                self._updateForPreviousSets(si, i, element, newStelements,
                                         newStelementsLastElements,
                                         newStelementsInfoStrs,
                                         lastStelementElementIndices)
        self.allSets.append(set)

        #Determine if lost stelement. If so then note.
        for lastStelement in self.lastStelements:
            newLastIndices = map(lambda x : x[0], newStelementsLastElements)
            if lastStelement[0] not in newLastIndices:
                for i in range(len(self.allStelements)):
                    if self.allStelements[i] == lastStelement[1]:
                        if i not in self.lostIndices:
                            self.lostIndices.append(i)

        # Now determine if the new stelement is a continuation of a prior 
        # stelement. If so then just update. If not then append.
        # The indices of the prior element of the newStelement are compared to 
        # element indices of the prior stelement to establish this.
        self.newIndex = -1
        # However, two new stelements may have the same last element, 
        # so we need to keep the details:
        allocationDetails = {}
        for i in range(len(newStelements)):
            newStelementLastElementIndex = newStelementsLastElements[i][0]
            newStelement = newStelements[i]
            newStelementsInfoStr = newStelementsInfoStrs[i]
            found = False
            for j in range(len(self.lastStelements)):
                lastStelementElementIndex = lastStelementElementIndices[j]
                lastStelement = self.lastStelements[j][1]
                if newStelementLastElementIndex == lastStelementElementIndex:
                    if j not in allocationDetails.keys():
                        # Uninitialised. Will contain index in the 
                        # self.allStelements that this maps to, last stelement 
                        # value that was replaced. We need to keep these because
                        # if a new stelement has the same maps then need to 
                        # compared both to the original last stelement value.
                        allocationDetails[j] = None 
                    found = True
                    break

            if not found:
                self._addNewStelement(newStelement[1], newStelementsInfoStr)
            else:
                if allocationDetails[j] is None: 
                    # We dont know where it is so have to search.
                    found = False
                    for k in range(len(self.allStelements)):
                        if lastStelement==self.allStelements[k]:
                            if k not in self.lostIndices:
                                allocationDetails[j] = [k, self.allStelements[k]]
                                found = True
                                break
                    if not found:
                        assert False # Could not find stelement to update
                    self._updateStelement(newStelement[1], newStelementsInfoStr,
                                          k)
                else:
                    k = allocationDetails[j][0]
                    origStelement = allocationDetails[j][1]
                    if self._isLatestStelementCloser(newStelement[1], 
                                                     self.allStelements[k], 
                                                     origStelement): 
                        #Swap them
                        self._addNewStelement(self.allStelements[k], 
                                              self.allStelementsHist[k])
                        self._updateStelement(newStelement[1], 
                                              newStelementsInfoStr, k)
                    else:
                        self._addNewStelement(newStelement[1], 
                                              newStelementsInfoStr)                    

        self.lastStelements = newStelements

        stelements = 0
        newStelements = 0
        lostStelements = 0
        allStelementsLabels = []
        for i in range(len(self.allStelements)):
            stelements += 1
            lbl = "REP"
            if self.newIndex!=-1 and i>=self.newIndex:
                lbl = "NEW"
                newStelements += 1

            for j in range(len(self.lostIndices)):
                if i == self.lostIndices[j]:
                    lbl = "LOST"
                    stelements -= 1
                    lostStelements += 1
                    break

            allStelementsLabels.append(lbl)

        self.totStelements = stelements+lostStelements
        self.totLostStelements = lostStelements

        return list(self.allStelements),\
               list(self.allStelementsHist),\
               list(allStelementsLabels)

    def _updateForPreviousSets(self, si, i, element, newStelements,
                               newStelementsLastElements, newStelementsInfoStrs,
                               lastStelementElementIndices):
        cmpElement = element
        isStelement = True
        hist = [(si, i)]
        firstStep = True
        repeatStelement = False
        for k in reversed(range(si-self.cfSteps, si)):
            cmpElementSet = self.allSets[k]
            smallestDiff = None
            if len(cmpElementSet) > 0:
                for j in range(len(cmpElementSet)):
                    cmpElement2 = cmpElementSet[j]
                    cdiff = self.ratCmp.getComplexDiff(cmpElement, cmpElement2)
                    diff = num.absDiff(cmpElement, cmpElement2) 
                    if self.ratCmp.checkComplexDiff(cdiff, self.distThres):
                        if smallestDiff is None or diff < smallestDiff:
                            histTemp = (k, j)
                            smallestDiff = diff
                            smallestCmpElement2 = cmpElement2
                            if firstStep:
                                lastIndex = j
                                lastSmallestCmpElement = smallestCmpElement2
                    if j==len(cmpElementSet)-1:
                        if smallestDiff is None:
                            isStelement = False
                        elif repeatStelement or\
                        (firstStep and lastIndex in lastStelementElementIndices):
                            repeatStelement = True
            else:
                isStelement = False
            firstStep = False
            if not isStelement:
                break
            else:
                cmpElement = smallestCmpElement2
                hist.append(histTemp)

        if isStelement:    
            newStelements.append((i,element))
            newStelementsLastElements.append((lastIndex,lastSmallestCmpElement))
            newStelementsInfoStrs.append(hist)

    def _addNewStelement(self, newStelement, newStelementsInfoStr):
        self.allStelements.append(newStelement)
        self.allStelementsHist.append(newStelementsInfoStr)
        #Record when we start adding new stelements
        if self.newIndex == -1:
            self.newIndex = len(self.allStelements)-1

    def _updateStelement(self, newStelement, newStelementsInfoStr, k):
        self.allStelements[k] = newStelement
        self.allStelementsHist[k] = newStelementsInfoStr

    def _isLatestStelementCloser(self, newStelement, oldStelement, origStelement):
        newDiff = self.ratCmp.getComplexDiff(newStelement, origStelement)
        oldDiff = self.ratCmp.getComplexDiff(oldStelement, origStelement)
        return abs(newDiff) < abs(oldDiff)
