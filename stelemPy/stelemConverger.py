import os
import sys
base =  os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,base+'/..')
sys.path.insert(0,base+'/../../../utilities')
from general import *
from general.file import *
from globalSettings import *
import general.numerical as num
import polefinder
import general.type_wrap as tw

POLE_STATUS_NEW = "NEW"
POLE_STATUS_LOST = "LOST"
POLE_STATUS_REP = "REP"

FIXPATH = True #When debugging the path seems to get screwed up, so I pull into a shorter path and remove the fix when debugging.

class Vals(list):
    def __init__(self, N, S, E):
        super(Vals, self).__init__()
        self.N = N
        self.S = S
        self.E = E
class Roots(Vals):
    pass
class Poles(Vals):
    pass

class Val:
    def __init__(self, k, E):
        self.k = k
        self.E = E
    def __eq__(self, other):
        return self.k == other.k
class Root(Val):
    def __init__(self, k, E):
        Val.__init__(self, k, E)
class Pole(Val):
    def __init__(self, k, E, isNew, isLost, convRoots):
        Val.__init__(self, k, E)
        self.isNew = isNew
        self.isLost = isLost
        self.convRoots = convRoots
    def getStatus(self):
        if self.isNew:
            return POLE_STATUS_NEW
        elif self.isLost:
            return POLE_STATUS_LOST
        else:
            return POLE_STATUS_REP
  
DISPLAY_DIFFPRECISION = 16
def formatRoot(num):
    if abs(num) < pow(10,-DISPLAY_DIFFPRECISION):
        return "&lt;E-"+str(DISPLAY_DIFFPRECISION)
    else:
        if type(num) is str or type(num) is unicode:
            return num
        elif type(num) is tw.mpmath.mpf:
            n = DISPLAY_DIFFPRECISION+tw.mpIntDigits(num)
            return tw.mpmath.nstr(num, n=n)
        else:
            return ('{:.'+str(DISPLAY_DIFFPRECISION)+'f}').format(num)

class PoleConverger:
    def __init__(self, resultFileHandler, Nmin=DEFAULT_N_MIN, Nmax=DEFAULT_N_MAX):
        self.setNmin = Nmin
        self.setNmax = Nmax
        if "COEFFS-mpmath" in resultFileHandler.getCoeffFilePath():
            tw.mode = tw.mode_mpmath
        else:
            tw.mode = tw.mode_norm
        self.poleSets = None
        fileBase = resultFileHandler.getRootDir()
        self.allRoots = self._parseFiles(fileBase, Roots, Root, False)
        self.Nmin = None
        self.Nmax = None
        self.polePath = resultFileHandler.getPoleDir()
        poleDirName = resultFileHandler.getPoleDirName()
        self.allPoles = self._parseFiles(self.polePath, Poles, Pole, True)
                
        if self.setNmin!=self.Nmin or self.setNmax!=self.Nmax:
            s = str(self.setNmin) + " " + str(self.Nmin) + " " + str(self.setNmax) + " " + str(self.Nmax) + " "
            raise Exception("Required pole files do not exist: " + s + "Likely a prior exception or impossible Nmax value.")
        
        self.zeroVal = float(poleDirName[poleDirName.find("_zk")+3:])

    def _parseFiles(self, fileBase, subContainerClass, typeClass, setNExtents):
        containerClass = []
        keyedFileNames = {}
        fileNames = os.listdir(fileBase)
        for fileName in fileNames:
            if fileName.endswith(".dat"):
                N = self._extractN(fileName, setNExtents)
                if N is not None:
                    keyedFileNames[N] = fileName
            
        for N in sorted(keyedFileNames.keys()):
            fileName = keyedFileNames[N]
            S, E = self._getFileParameters(fileName)
            subContainer = subContainerClass(N,S,E)
            containerClass.append(subContainer)
            self._extractValues(fileBase+fileName, subContainer, typeClass)
        return containerClass

    def _extractN(self, fileName, setNExtents):
        N = int(fileName.split("=")[1].split("_")[0])
        if N>=self.setNmin and N<=self.setNmax:
            if setNExtents:
                if self.Nmin is None or N<self.Nmin:
                    self.Nmin = N
                if self.Nmax is None or N>self.Nmax:
                    self.Nmax = N
            return N
        else:
            return None

    def _getFileParameters(self, fileName):
        params = fileName.split("_")
        params[2] = params[2].replace(".dat","")
        S = int(params[1].split("=")[1])
        E = int(params[2].split("=")[1])
        return S, E
    
    def _extractValues(self, path, container, typeClass):
        with open(path, 'r') as f:
            first = True
            for line in f:
                if not first and polefinder.COMPLETE_STR not in line:
                    kstr = line[line.find(']=')+2:line.find('i')]+'j'
                    post = ""
                    if typeClass==Pole:
                        post = " "
                    Estr = line[line.rfind(']=')+2:line.rfind('i'+post)]+'j' 
                    #print kstr + "\t" + Estr  
                    if typeClass==Root:
                        type = Root(tw.complex(kstr), tw.complex(Estr))
                    else:
                        convRootsStrs = line[line.find("with")+5:].split(" ")
                        convRoots = map(lambda x: map(lambda y: int(y), x[2:-1].replace("]","").split("[")), convRootsStrs)
                        type = Pole(tw.complex(kstr), tw.complex(Estr), POLE_STATUS_NEW in line, POLE_STATUS_LOST in line, convRoots)
                    container.append(type) 
                first = False      
                
    def createPoleTable(self):
        poleSets = self._createPoleSets()
        try:
            poleSets = sorted(poleSets, key=self._getFinalImag)
            self.poleSets = sorted(poleSets, key=self._getFinalImag, cmp=self._poleCmp)  #Do two sorts since we want to both group by pole/antipole and then ensure that the pole comes first.
            self._writePoleSets(poleSets)
        except InternalException as e:
            self._writeErrorToFile(str(e))
    
    def _createPoleSets(self):
        poleSets = []
        lastN = None
        for poles in self.allPoles:
            for pole in poles:
                if pole.isNew:
                    poleSets.append({poles.N:pole})
                elif not pole.isLost:
                    found = False
                    for i in range(len(poleSets)):
                        if poles.N not in poleSets[i] and poleSets[i][lastN].convRoots[0][1]==pole.convRoots[1][1]:
                            poleSets[i][poles.N] = pole
                            found = True
                            break
                    if not found:
                        raise Exception("Could not find pole set for repeated pole!") #Should never be here
                else:
                    for i in range(len(poleSets)):
                        if poleSets[i][lastN].k == pole.k:
                            poleSets[i][poles.N] = pole #Just carry the value forward for now.
                    
            lastN = poles.N
        return poleSets
    
    def _getFinalImag(self, poleSet): #Sort on pole at highest N
        for N in sorted(poleSet.keys(),reverse=True):
            pole = poleSet[N]
            if pole.getStatus() != POLE_STATUS_LOST:
                return pole.E.imag
        raise Exception("LOST pole when none were ever found!") #Should never be here
    
    def _poleCmp(self, v1, v2):
        if abs(v1) < self.zeroVal and abs(v2) < self.zeroVal:
            return 0
        elif abs(v1) < self.zeroVal:
            return -1
        elif abs(v2) < self.zeroVal:
            return 1
        elif abs(v1) < abs(v2):
            return -1
        elif abs(v1) > abs(v2):
            return 1
        else:
            return 0
    
    def _writePoleSets(self, poleSets):
        table = []
        for poleSet in poleSets:
            table.append([" ", "_", "_", "_"])
            first = True
            for N in sorted(poleSet.keys()):
                pole = poleSet[N]
                if first:
                    self._writePriorRoots(table, pole)
                if pole.getStatus() == POLE_STATUS_LOST:
                    self._setClosestRoot(N, pole)
                first = False
                table.append([N, pole.getStatus(), formatRoot(pole.E.real), formatRoot(pole.E.imag)])
        outStr = getFormattedHTMLTable(table, ["N","Status", "pole.E.real", "pole.E.imag"], self.zeroVal, numalign="decimal")
        self._writePoleSetsToFile(outStr)
        print outStr
    
    def _writePoleSetsToFile(self, outStr):
        self._writeToFile(outStr)
    
    def _writeErrorToFile(self, msg):
        self._writeToFile(msg)
    
    def _writeToFile(self, string):
        if self.polePath is not None: 
            path = self.polePath+"Nmin="+str(self.Nmin)+"_Nmax="+str(self.Nmax)+".tab"
            with open(path, 'w+') as f:
                f.write(string)
            
    def _writePriorRoots(self, table, initPole):
        for priorRoot in reversed(initPole.convRoots[1:]):
            N = priorRoot[0] #N of root
            I = priorRoot[1] #Index of root
            Nroots = self._getRootsForN(N)
            table.append([N, "ROOT", formatRoot(Nroots[I].E.real), formatRoot(Nroots[I].E.imag)])
            
    def _setClosestRoot(self, N, pole):
        Nroots = self._getRootsForN(N)
        smallestDiff = None
        smallestIndex = None
        for i in range(len(Nroots)):
            root = Nroots[i]
            diff = num.absDiff(root.k, pole.k)
            if smallestDiff is None or diff<smallestDiff:
                smallestDiff = diff
                smallestIndex = i
        pole.k = Nroots[smallestIndex].k
        pole.E = Nroots[smallestIndex].E
            
    def _getRootsForN(self, N):
        for roots in self.allRoots:
            if roots.N == N:
                return roots
