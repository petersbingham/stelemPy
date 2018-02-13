import pynumutil as num

class stelemConverger:
    def __init__(self, sets, stelementsResults):
        self.sets = sets
        self.stelementsResults = stelementsResults

    def createConvergenceGroups(self):
        convGroups = []
        lastsi = None
        for si in range(len(self.stelementsResults)):
            stelementsResult = self.stelementsResults[si]
            for pi in range(len(stelementsResult[0])):
                stelement = stelementsResult[0][pi]
                hist = stelementsResult[1][pi]
                lbl = stelementsResult[2][pi]

                if lbl == "NEW":
                    convGroups.append({si:[stelement,hist,lbl]})
                elif lbl != "LOST":
                    found = False
                    for i in range(len(convGroups)):
                        if si not in convGroups[i]:
                            if convGroups[i][lastsi][1][0][1]==hist[1][1]:
                                convGroups[i][si] = [stelement,hist,lbl]
                                found = True
                                break
                    if not found:
                        assert False #Could not find repeated stelement
                else:
                    for i in range(len(convGroups)):
                        if convGroups[i][lastsi][0] == stelement:
                            # Just carry the value forward for now:
                            convGroups[i][si] = [stelement,None,"LOST"]

            lastsi = si
        return convGroups

    def writePriorElements(self, convGroups):
        for stelementSet in convGroups:
            firstFnd = min(stelementSet.keys())
            firstHist = stelementSet[firstFnd][1]
            for h in firstHist[1:]:
                si = h[0]
                ei = h[1]
                stelementSet[si] = [self.sets[si][ei],None,"PRE"]

    def setClosestElementToLost(self, convGroups):
        for stelementSet in convGroups:
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
