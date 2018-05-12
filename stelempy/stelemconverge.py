import pynumutil as num

class StelemConverger:
    def __init__(self, sets, stelements_results):
        self.sets = sets
        self.stelements_results = stelements_results

    def create_convergence_groups(self):
        conv_groups = []
        lastsi = None
        for si in range(len(self.stelements_results)):
            stelementsResult = self.stelements_results[si]
            for pi in range(len(stelementsResult[0])):
                stelement = stelementsResult[0][pi]
                hist = stelementsResult[1][pi]
                lbl = stelementsResult[2][pi]

                if lbl == "NEW":
                    conv_groups.append({si:[stelement,hist,lbl]})
                elif lbl != "LOST":
                    found = False
                    for i in range(len(conv_groups)):
                        if si not in conv_groups[i]:
                            if conv_groups[i][lastsi][1][0][1]==hist[1][1]:
                                conv_groups[i][si] = [stelement,hist,lbl]
                                found = True
                                break
                    if not found:
                        assert False #Could not find repeated stelement
                else:
                    for i in range(len(conv_groups)):
                        if conv_groups[i][lastsi][0] == stelement:
                            # Just carry the value forward for now:
                            conv_groups[i][si] = [stelement,None,"LOST"]

            lastsi = si
        return conv_groups

    def write_prior_elements(self, conv_groups):
        for stelementSet in conv_groups:
            firstFnd = min(stelementSet.keys())
            firstHist = stelementSet[firstFnd][1]
            for h in firstHist[1:]:
                si = h[0]
                ei = h[1]
                stelementSet[si] = [self.sets[si][ei],None,"PRE"]

    def set_closest_element_to_lost(self, conv_groups):
        for stelementSet in conv_groups:
            for si,stelement in stelementSet.iteritems():
                if stelement[2] == "LOST":
                    smallestDiff = None
                    smallestei = None
                    for ei, el in enumerate(self.sets[si]):
                        diff = num.abs_diff(el, stelement[0])
                        if smallestDiff is None or diff<smallestDiff:
                            smallestDiff = diff
                            smallestei = ei
                    if smallestei is not None:
                        stelement[0] = self.sets[si][smallestei]
