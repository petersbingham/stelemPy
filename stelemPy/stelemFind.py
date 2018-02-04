import sys
import os
import traceback
sys.path.append("../utilities")
import general.numerical as num
from ratsmat import *
from decimator import *
import general.type_wrap as tw
from globalSettings import *

ZEROVALEXP = 7
DOUBLE_N = 'doubleN'
INC_N = 'incN'
COMPLETE_STR = "Complete"
   
class PoleFinder:
    def __init__(self, sMats, fitkCal, resultFileHandler, startIndex, endIndex, offset, endLock, distThreshold, cfSteps=1, cmpValue=None, mode=DOUBLE_N, populateSmatCB=None, zeroValExp=ZEROVALEXP, Nmin=DEFAULT_N_MIN, Nmax=DEFAULT_N_MAX, ratkCal=None):
        self.sMats = sMats
        self.fitkCal = fitkCal
        self.resultFileHandler = resultFileHandler
        self.decimator = Decimator(startIndex, endIndex, offset, resultFileHandler)
        self.endLock = endLock
        self.cfSteps = cfSteps
        self.distThreshold = distThreshold
        self.zeroValue = 10**(-zeroValExp)
        self.ratCmp = num.RationalCompare(self.zeroValue)
        self.lastRoots = []
        self.allPoles = []
        self.allPolesInfoStrs = []
        self.allRoots = []
        self.allNs = []
        self.lastPoles = []
        self.lostIndices = []
        self.cmpValue = cmpValue
        self.populateSmatCB = populateSmatCB
        self.file_poles = None
        self.mode = mode
        self.first = True
        self.Nmin = Nmin
        self.Nmax = Nmax
        self.ratkCal = ratkCal
        self.NmaxTotPoles = 0
        self.NmaxLostPoles = 0
        self.errState = False
        self.newIndex = -1
        if mode == DOUBLE_N:
            self._doubleN()
        else:
            self._incN()

    def _doubleN(self):
        N = self.Nmin
        while N <= self.Nmax:
            if not self._doForN(N):
                break
            N = 2*N

    def _incN(self):
        N = self.Nmin
        while N <= self.Nmax:
            if not self._doForN(N):
                break
            N = N+2

    def _doForN(self, N):
        ret = True
        try:
            if not self.first:
                print "\n"
            self.first = False
            roots = self._getNroots(N)
            self._locatePoles(roots, N)
            self.allNs.append(N)
        except InternalException as inst:
            string = "Unhandled Exception: " + str(inst) + "\n"
            print string
            if self.file_poles is not None:
                self.file_poles.write(string)
            self.errState = True
            ret = False
        if self.file_poles is not None:
            self.file_poles.close()
            self.file_poles = None
        return ret

    def _getNroots(self, N):
        sMats, descStr = self.decimator.decimate(self.sMats, N, self.endLock)
        ratSmat = RatSMat(sMats, self.fitkCal, self.ratkCal, resultFileHandler=self.resultFileHandler, doCalc=False)
        self.resultFileHandler.setPoleFindParameters(self.mode, self.cfSteps, self.distThreshold, self.zeroValue)
        
        roots = None
        cleanRoots = None
        
        if not ALWAYS_CALCULATE:
            if self._isReadCleanRootsRequired():
                cleanRoots = self._readCleanroots(ratSmat, N)
            if self._isReadBaseRootsRequired(cleanRoots):
                roots = self._readBaseroots(ratSmat, N)
            
        if self._isCalculationRequired(cleanRoots, roots):
            if self._isBaseCalculationRequired(roots):
                roots = self._calculateRoots(sMats, ratSmat, descStr, N)
            if self._isCleanCalculationRequired(cleanRoots):
                cleanRoots = self._cleanRoots(ratSmat, roots, descStr, N)
            
        if cleanRoots is not None:
            finalRoots = cleanRoots
        else:
            finalRoots = roots
        
        self.file_poles = open(self.resultFileHandler.getPoleFilePath(), 'w')
        self.file_poles.write(descStr+"\n")
        
        return finalRoots

    def _printInfoStr(self, preFix, N, roots):
        print preFix + " Roots for N=" + str(N) + ":"
        print "  " + str(len(roots)) + " roots."
        

#################File Read Related#####################
#######################################################

    def _isReadCleanRootsRequired(self):
        return self.resultFileHandler.useCleanRoots() and self.resultFileHandler.doesCleanRootFileExist()

    def _readCleanroots(self, ratSmat, N):
        roots = None
        ratSmat.coeffSolve.printCalStr(True)
        try:
            roots = self._readNroots(N, self.resultFileHandler.getCleanRootFilePath())
            ratSmat.rootSolver.printCalStr(True)
            ratSmat.rootCleaner.printCalStr(True)
            self._printInfoStr("Loaded Clean", N, roots)
        except InternalException as e:
            print "Error reading clean roots will attempt to recalculate: " + str(e)        
        return roots

    def _isReadBaseRootsRequired(self, cleanRoots):
        return cleanRoots is None and self.resultFileHandler.doesRootFileExist()

    def _readBaseroots(self, ratSmat, N):
        roots = None
        ratSmat.coeffSolve.printCalStr(True)
        try:
            roots = self._readNroots(N, self.resultFileHandler.getRootFilePath())
            ratSmat.rootSolver.printCalStr(True)
            self._printInfoStr("Loaded", N, roots)
        except InternalException as e:
            print "Error reading roots will attempt to recalculate: " + str(e)        
        return roots
        
    def _readNroots(self, N, rootPath):
        roots = []
        fileComplete = False
        with open(rootPath, 'r') as f:
            firstLine = True
            for line in f:        
                if COMPLETE_STR in line:
                    return roots
                elif not firstLine:
                    k_str = line[line.find('=')+1:line.find('i')]+'j'
                    E_str = line[line.rfind('=')+1:line.rfind('i')]+'j'
                    roots.append((complex(k_str),complex(E_str)))
                firstLine = False
        raise Exception("Incomplete Root File")        

###############Calculation Related#####################
#######################################################
        
    def _isCalculationRequired(self, cleanRoots, roots):
        if self.resultFileHandler.useCleanRoots():
            return cleanRoots is None
        else:
            return roots is None
    
    def _isBaseCalculationRequired(self, roots):
        return roots is None
    
    def _isCleanCalculationRequired(self, cleanRoots):
        return self.resultFileHandler.useCleanRoots() and cleanRoots is None
    
    def _calculateRoots(self, sMats, ratSmat, descStr, N):
        if self.populateSmatCB is not None:
            self.populateSmatCB(sMats, self.sMats)
        file = open(self.resultFileHandler.getRootFilePath(), 'w')
        try:
            ratSmat.doCalc()
            roots = ratSmat.findRoots(self.lastRoots)
            self.lastRoots = roots
            self._printInfoStr("Calculated", N, roots)
            self._recordRoots(file, descStr, roots)     
            file.close()
        except InternalException as inst:
            string = "Unhandled Exception: " + str(inst) + "\n"
            file.write(string)  
            file.close()
            raise inst
        return roots
    
    def _cleanRoots(self, ratSmat, roots, descStr, N):
        cleanRoots, rejectRoots = ratSmat.cleanRoots(roots)
        
        file = open(self.resultFileHandler.getCleanRootFilePath(), 'w')
        self._recordRoots(file, descStr, cleanRoots)
        file.close()
        file = open(self.resultFileHandler.getRejectRootFilePath(), 'w')
        self._recordRoots(file, descStr, rejectRoots)
        file.close()
        
        self._printInfoStr("Cleaned", N, cleanRoots)
        return cleanRoots
    
    def _recordRoots(self, file, descStr, roots):
        file.write(descStr+"\n")
        closestIndex = self._getClosestIndex(roots)
        for i in range(len(roots)):
            self._recordRoot(file, i, roots[i], closestIndex)
        file.write(COMPLETE_STR)     
                 
    def _recordRoot(self, file, i, root, closestIndex):
        endStr = ""
        if self.cmpValue is not None and closestIndex==i:
            endStr = " @<****>@"
        writeStr = ("Root_k[%d]="+self._getComplexFormat()+"\tRoot_E[%d]="+self._getComplexFormat()+"\t%s\n") % (i,root[k_INDEX].real,root[k_INDEX].imag,i,root[E_INDEX].real,root[E_INDEX].imag,endStr)
        file.write(writeStr)     

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
                infoStr = "with N=%d[%d]" % (N, i)
                firstStep = True
                repeatPole = False
                for k in reversed(range(len(self.allRoots)-self.cfSteps, len(self.allRoots))): #Look at the last sets
                    cmpRootSet = self.allRoots[k]
                    smallestAbsCdiff = None
                    infoStr2 = ""
                    if len(cmpRootSet) > 0:
                        for j in range(len(cmpRootSet)):
                            cmpRoot2 = cmpRootSet[j]
                            cdiff = self.ratCmp.getComplexDiff(cmpRoot[k_INDEX], cmpRoot2[k_INDEX])
                            absCdiff = num.absDiff(cmpRoot[k_INDEX], cmpRoot2[k_INDEX]) 
                            if self.ratCmp.checkComplexDiff(cdiff, self.distThreshold):
                                if smallestAbsCdiff is None or absCdiff < smallestAbsCdiff:
                                    infoStr2 = " N=%d[%d]" % (self.allNs[k], j)
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
                        infoStr += infoStr2
                        
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
                    if self._isLatestPoleCloser(newPole[1][k_INDEX], self.allPoles[k][k_INDEX], origPole[k_INDEX]): 
                        #Swap them
                        self._addNewPole(self.allPoles[k], self.allPolesInfoStrs[k])
                        self._updatePole(newPole[1], newPolesInfoStr, k)
                    else:
                        self._addNewPole(newPole[1], newPolesInfoStr)                    
                    
        self.lastPoles = newPoles

        poles = 0
        newPoles = 0
        lostPoles = 0
        for i in range(len(self.allPoles)):
            poles += 1
            endStr = ""
            if self.newIndex!=-1 and i>=self.newIndex:
                endStr = "NEW "
                newPoles += 1
              
            for j in range(len(self.lostIndices)):
                if i == self.lostIndices[j]:
                    endStr = "LOST "
                    poles -= 1
                    lostPoles += 1
                    break
            
            writeStr = ("Pole_k[%d]="+self._getComplexFormat()+"\tPole_E[%d]="+self._getComplexFormat()+"    \t%s%s\n") % (i,self.allPoles[i][k_INDEX].real,self.allPoles[i][k_INDEX].imag,i,self.allPoles[i][E_INDEX].real,self.allPoles[i][E_INDEX].imag,endStr,self.allPolesInfoStrs[i])
            self.file_poles.write(writeStr)
          
        self.file_poles.write(COMPLETE_STR)
        print "Poles calculated in mode " + self.mode + ", using dk=" + str(self.distThreshold)
        print "Calculated Poles for N=" + str(N) + ":"
        print "  " + str(poles) + " poles, of which " + str(newPoles) + " are new. " + str(lostPoles) + (" has" if lostPoles==1 else " have") + " been lost."
        if N == self.Nmax:
            self.NmaxTotPoles = poles+lostPoles
            self.NmaxLostPoles = lostPoles
    
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
                diff = abs(self.cmpValue-roots[j][E_INDEX])
                if j==0 or diff<closestDiff:
                    closestDiff = diff
                    closestIndex = j
                
    def _printSep1(self, file):
        file.write("@<---------------------------------------------------------------------------------------------->@\n")

    def _printSep2(self, file):
        file.write("@<**********************************************************************************************>@\n")
        
    def _getComplexFormat(self):
        if tw.mode == tw.mode_norm:
            return "%.14f%+.14fi"
        else:
            return "%."+str(tw.dps)+"f%+."+str(tw.dps)+"fi"   