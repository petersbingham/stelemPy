import numericalUtilities as num

class stelemConverger:
    def __init__(self, sets, stelementsResults):
        self.sets = sets
        self.stelementsResults = stelementsResults

    def createPoleSets(self):
        poleSets = []
        lastsi = None
        for si in range(len(self.stelementsResults)):
            stelementsResult = self.stelementsResults[si]
            for pi in range(len(stelementsResult[0])):
                pole = stelementsResult[0][pi]
                hist = stelementsResult[1][pi]
                lbl = stelementsResult[2][pi]

                if lbl == "NEW":
                    poleSets.append({si:[pole,hist,lbl]})
                elif lbl != "LOST":
                    found = False
                    for i in range(len(poleSets)):
                        if si not in poleSets[i] and poleSets[i][lastsi][1][0][1]==hist[1][1]:
                            poleSets[i][si] = [pole,hist,lbl]
                            found = True
                            break
                    if not found:
                        raise Exception("Could not find pole set for repeated pole!") #Should never be here
                else:
                    for i in range(len(poleSets)):
                        if poleSets[i][lastsi][0] == pole:
                            poleSets[i][si] = [pole,None,"LOST"] #Just carry the value forward for now.

            lastsi = si
        return poleSets

    def writePriorRoots(self, poleSets):
        for poleSet in poleSets:
            firstFnd = min(poleSet.keys())
            firstHist = poleSet[firstFnd][1]
            for h in firstHist[1:]:
                si = h[0]
                ei = h[1]
                poleSet[si] = [self.sets[si][ei],None,"PRE"]

    def setClosestRootToLost(self, poleSets):
        for poleSet in poleSets:
            for pole in poleSet:
                if pole[2] == "LOST":
                    si = pole[1][0][0]
                    smallestDiff = None
                    smallestIndex = None
                    for ei, el in enumerate(self.sets[si]):
                        diff = num.absDiff(el, pole[0])
                        if smallestDiff is None or diff<smallestDiff:
                            smallestDiff = diff
                            smallestIndex = ei
                    pole[0] = self.sets[si][ei]
