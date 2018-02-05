import numericalUtilities as num

DEFAULT_ZEROVALEXP = 7

InternalException = Exception # Set to None for debug

class stelemFind:
    def __init__(self, distThreshold, getElementFun, Nmin, Nmax, cfSteps=1, 
                 zeroValExp=DEFAULT_ZEROVALEXP, cmpValue=None):
        self.distThreshold = distThreshold
        self.getElementFun = getElementFun
        self.cfSteps = cfSteps
        self.zeroValue = 10**(-zeroValExp)
        self.cmpValue = cmpValue
        
        self.ratCmp = num.RationalCompare(self.zeroValue)
        self.lastRoots = []
        self.allRoots = []
        
        self.allPoles = []
        self.allPolesInfoStrs = []

        self.accPoles = {}
        self.accPolesInfoStrs = {}
        self.accPolesLabels = {}

        self.allNs = []
        self.lastPoles = []
        self.lostIndices = []
        self.file_poles = None
        self.NmaxTotPoles = 0
        self.NmaxLostPoles = 0
        self.errState = False
        self.newIndex = -1

        self.Nmin = Nmin
        self.Nmax = Nmax
        self._incN()

    def getResults(self):
        return self.accPoles, self.accPolesInfoStrs, self.accPolesLabels

    def _incN(self):
        for N in range(self.Nmin,self.Nmax):
            if not self._doForN(N):
                break

    def _doForN(self, N):
        ret = True
        try:
            self.first = False
            roots = self.getElementFun(N)
            self._locatePoles(roots, N)
            self.allNs.append(N)
        except InternalException as inst:
            string = "Unhandled Exception: " + str(inst) + "\n"
            print string
            self.errState = True
            ret = False
        return ret

#######################################################
#######################################################

    def _locatePoles(self, roots, N):  
        newPoles = []
        newPolesInfoStrs = []
        newPolesLastRoots = []
        lastPoleRootIndices = ()
        if len(self.lastPoles) > 0:
            lastPoleRootIndices = zip(*self.lastPoles)[0]
        if len(self.allRoots) >= self.cfSteps:  
            for i in range(len(roots)):
                root = roots[i]
                cmpRoot = root
                isPole = True
                infoStr = [(N, i)]
                firstStep = True
                repeatPole = False
                for k in reversed(range(len(self.allRoots)-self.cfSteps, len(self.allRoots))): #Look at the last sets
                    cmpRootSet = self.allRoots[k]
                    smallestAbsCdiff = None
                    if len(cmpRootSet) > 0:
                        for j in range(len(cmpRootSet)):
                            cmpRoot2 = cmpRootSet[j]
                            cdiff = self.ratCmp.getComplexDiff(cmpRoot, cmpRoot2)
                            absCdiff = num.absDiff(cmpRoot, cmpRoot2) 
                            if self.ratCmp.checkComplexDiff(cdiff, self.distThreshold):
                                if smallestAbsCdiff is None or absCdiff < smallestAbsCdiff:
                                    infoStr2 = (self.allNs[k], j)
                                    smallestAbsCdiff = absCdiff
                                    smallestCmpRoot2 = cmpRoot2
                                    if firstStep:
                                        poleLastRootIndex = j
                                        poleLastSmallestCmpRoot = smallestCmpRoot2
                            if j==len(cmpRootSet)-1:
                                if smallestAbsCdiff is None:
                                    isPole = False
                                elif repeatPole or (firstStep and poleLastRootIndex in lastPoleRootIndices):
                                    repeatPole = True
                    else:
                        isPole = False
                    firstStep = False
                    if not isPole:
                        break
                    else:
                        cmpRoot = smallestCmpRoot2
                        infoStr.append(infoStr2)

                if isPole:    
                    newPoles.append((i,root))
                    newPolesLastRoots.append((poleLastRootIndex,poleLastSmallestCmpRoot))
                    newPolesInfoStrs.append(infoStr)

        self.allRoots.append(roots)

        #Determine if lost pole. If so then note.
        for lastPole in self.lastPoles:
            if lastPole[0] not in map(lambda x : x[0], newPolesLastRoots):
                for i in range(len(self.allPoles)):
                    if self.allPoles[i] == lastPole[1]:
                        if i not in self.lostIndices:
                            self.lostIndices.append(i)

        #Now determine if the new pole is a continuation of a prior pole. If so then just update. If not then append.
        #The indices of the prior root of the newPole are compared to root indices of the prior pole to establish this.
        self.newIndex = -1
        allocationDetails = {} #However, two new poles may have the same last root, so we need to keep the details.
        for i in range(len(newPoles)):
            newPoleLastRootIndex = newPolesLastRoots[i][0]
            newPole = newPoles[i]
            newPolesInfoStr = newPolesInfoStrs[i]
            found = False
            for j in range(len(self.lastPoles)):
                lastPoleRootIndex = lastPoleRootIndices[j]
                lastPole = self.lastPoles[j][1]
                if newPoleLastRootIndex == lastPoleRootIndex:
                    if j not in allocationDetails.keys():
                        allocationDetails[j] = None #Uninitialised. Will contain: [index in the self.allPoles that this maps to, last pole value that was replaced]. We need to keep these because if a new pole has the same maps then need to compared both to the original last pole value.
                    found = True
                    break

            if not found:
                self._addNewPole(newPole[1], newPolesInfoStr)
            else:
                if allocationDetails[j] is None: #We dont know where it is so have to search.
                    found = False
                    for k in range(len(self.allPoles)):
                        if lastPole==self.allPoles[k] and k not in self.lostIndices:
                            allocationDetails[j] = [k, self.allPoles[k]]
                            found = True
                            break
                    if not found:
                        raise Exception("Could not find pole to update") #Should never be here
                    self._updatePole(newPole[1], newPolesInfoStr, k)
                else:
                    k = allocationDetails[j][0]
                    origPole = allocationDetails[j][1]
                    if self._isLatestPoleCloser(newPole[1], self.allPoles[k], origPole): 
                        #Swap them
                        self._addNewPole(self.allPoles[k], self.allPolesInfoStrs[k])
                        self._updatePole(newPole[1], newPolesInfoStr, k)
                    else:
                        self._addNewPole(newPole[1], newPolesInfoStr)                    
                    
        self.lastPoles = newPoles

        poles = 0
        newPoles = 0
        lostPoles = 0
        allPolesLabels = []
        for i in range(len(self.allPoles)):
            poles += 1
            endStr = ""
            if self.newIndex!=-1 and i>=self.newIndex:
                endStr = "NEW"
                newPoles += 1
              
            for j in range(len(self.lostIndices)):
                if i == self.lostIndices[j]:
                    endStr = "LOST "
                    poles -= 1
                    lostPoles += 1
                    break

            allPolesLabels.append(endStr)

        if N == self.Nmax:
            self.NmaxTotPoles = poles+lostPoles
            self.NmaxLostPoles = lostPoles
            
        self.accPoles[N] = list(self.allPoles)
        self.accPolesInfoStrs[N] = list(self.allPolesInfoStrs)
        self.accPolesLabels[N] = list(allPolesLabels)
    
    def _addNewPole(self, newPole, newPolesInfoStr):
        self.allPoles.append(newPole)
        self.allPolesInfoStrs.append(newPolesInfoStr)
        #Record when we start adding new poles
        if self.newIndex == -1:
            self.newIndex = len(self.allPoles)-1
            
    def _updatePole(self, newPole, newPolesInfoStr, k):
        self.allPoles[k] = newPole
        self.allPolesInfoStrs[k] = newPolesInfoStr
        
    def _isLatestPoleCloser(self, newkPole, oldkPole, origkPole):
        newDiff = self.ratCmp.getComplexDiff(newkPole, origkPole)
        oldDiff = self.ratCmp.getComplexDiff(oldkPole, origkPole)
        return abs(newDiff) < abs(oldDiff)

    def _getClosestIndex(self, roots):
        #This is when we know the position of a pole and want to mark the closest root to this value in the output file.
        closestIndex = None
        closestDiff = None
        if self.cmpValue is not None:
            for j in range(len(roots)):
                diff = abs(self.cmpValue-roots[j])
                if j==0 or diff<closestDiff:
                    closestDiff = diff
                    closestIndex = j
  