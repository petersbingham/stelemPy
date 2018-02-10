import numericalUtilities as num

class stelemConverger:
    def __init__(self, sets, stelementsResults):
        self.sets = sets
        self.stelementsResults = stelementsResults

    def createConvergenceGroups(self):
        convergenceGroups = []
        lastsi = None
        for si in range(len(self.stelementsResults)):
            stelementsResult = self.stelementsResults[si]
            for pi in range(len(stelementsResult[0])):
                stelement = stelementsResult[0][pi]
                hist = stelementsResult[1][pi]
                lbl = stelementsResult[2][pi]

                if lbl == "NEW":
                    convergenceGroups.append({si:[stelement,hist,lbl]})
                elif lbl != "LOST":
                    found = False
                    for i in range(len(convergenceGroups)):
                        if si not in convergenceGroups[i] and convergenceGroups[i][lastsi][1][0][1]==hist[1][1]:
                            convergenceGroups[i][si] = [stelement,hist,lbl]
                            found = True
                            break
                    if not found:
                        raise Exception("Could not find stelement set for repeated stelement!") #Should never be here
                else:
                    for i in range(len(convergenceGroups)):
                        if convergenceGroups[i][lastsi][0] == stelement:
                            convergenceGroups[i][si] = [stelement,None,"LOST"] #Just carry the value forward for now.

            lastsi = si
        return convergenceGroups

    def writePriorElements(self, convergenceGroups):
        for stelementSet in convergenceGroups:
            firstFnd = min(stelementSet.keys())
            firstHist = stelementSet[firstFnd][1]
            for h in firstHist[1:]:
                si = h[0]
                ei = h[1]
                stelementSet[si] = [self.sets[si][ei],None,"PRE"]

    def setClosestElementToLost(self, convergenceGroups):
        for stelementSet in convergenceGroups:
            for si,stelement in stelementSet.iteritems():
                if stelement[2] == "LOST":
                    smallestDiff = None
                    smallestei = None
                    for ei, el in enumerate(self.sets[si]):
                        diff = num.absDiff(el, stelement[0])
                        if smallestDiff is None or diff<smallestDiff:
                            smallestDiff = diff
                            smallestei = ei
                    if smallestei is not None:
                        stelement[0] = self.sets[si][smallestei]
