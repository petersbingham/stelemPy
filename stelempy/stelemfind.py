import pynumutil as num

default_zeroValExp = 7
default_dist_thres = 0.001
default_cfsteps = 1

class StelemFind:
    def __init__(self, dist_thres=default_dist_thres, cfsteps=default_cfsteps, 
                 ratcmp=None):
        self.dist_thres = dist_thres
        self.cfsteps = cfsteps

        self.ratcmp = ratcmp
        if self.ratcmp is None:
            self.ratcmp = num.RationalCompare1(10**(-default_zeroValExp))
        self.lastSet = []
        self.allSets = []

        self.allStelements = []
        self.allStelementsHist = []

        self.lastStelements = []
        self.lostIndices = []
        self.totStelements = 0
        self.totLostStelements = 0
        self.newIndex = -1

    def add_sets(self, sets):
        resultSets = []
        for set in sets:
            resultSets.append(self._locate_stelements(set))
        return resultSets

    def add_set(self, set):
        return self._locate_stelements(set)

#######################################################
#######################################################

    def _locate_stelements(self, set):
        si = len(self.allSets)
        new_stelements = []
        new_stelements_last_elements = []
        new_stelements_info_strs = []
        last_stelement_element_indices = ()
        if len(self.lastStelements) > 0:
            last_stelement_element_indices = zip(*self.lastStelements)[0]
        if si >= self.cfsteps:  
            for i in range(len(set)):
                element = set[i]
                self._update_for_previous_sets(si, i, element, new_stelements,
                                               new_stelements_last_elements,
                                               new_stelements_info_strs,
                                               last_stelement_element_indices)
        self.allSets.append(set)

        #Determine if lost stelement. If so then note.
        for lastStelement in self.lastStelements:
            newLastIndices = map(lambda x : x[0], new_stelements_last_elements)
            if lastStelement[0] not in newLastIndices:
                for i in range(len(self.allStelements)):
                    if self.allStelements[i] == lastStelement[1]:
                        if i not in self.lostIndices:
                            self.lostIndices.append(i)

        # Now determine if the new stelement is a continuation of a prior 
        # stelement. If so then just update. If not then append.
        # The indices of the prior element of the new_stelement are compared to 
        # element indices of the prior stelement to establish this.
        self.newIndex = -1
        # However, two new stelements may have the same last element, 
        # so we need to keep the details:
        allocationDetails = {}
        for i in range(len(new_stelements)):
            new_stelementLastElementIndex = new_stelements_last_elements[i][0]
            new_stelement = new_stelements[i]
            new_stelements_info_str = new_stelements_info_strs[i]
            found = False
            for j in range(len(self.lastStelements)):
                lastStelementElementIndex = last_stelement_element_indices[j]
                lastStelement = self.lastStelements[j][1]
                if new_stelementLastElementIndex == lastStelementElementIndex:
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
                self._add_new_stelement(new_stelement[1], new_stelements_info_str)
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
                    self._update_stelement(new_stelement[1], new_stelements_info_str,
                                          k)
                else:
                    k = allocationDetails[j][0]
                    orig_stelement = allocationDetails[j][1]
                    if self._is_latest_stelement_closer(new_stelement[1], 
                                                     self.allStelements[k], 
                                                     orig_stelement): 
                        #Swap them
                        self._add_new_stelement(self.allStelements[k], 
                                              self.allStelementsHist[k])
                        self._update_stelement(new_stelement[1], 
                                              new_stelements_info_str, k)
                    else:
                        self._add_new_stelement(new_stelement[1], 
                                              new_stelements_info_str)                    

        self.lastStelements = new_stelements

        stelements = 0
        new_stelements = 0
        lostStelements = 0
        allStelementsLabels = []
        for i in range(len(self.allStelements)):
            stelements += 1
            lbl = "REP"
            if self.newIndex!=-1 and i>=self.newIndex:
                lbl = "NEW"
                new_stelements += 1

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

    def _update_for_previous_sets(self, si, i, element, new_stelements,
                                  new_stelements_last_elements, 
                                  new_stelements_info_strs,
                                  last_stelement_element_indices):
        cmpElement = element
        isStelement = True
        hist = [(si, i)]
        firstStep = True
        repeatStelement = False
        for k in reversed(range(si-self.cfsteps, si)):
            cmpElementSet = self.allSets[k]
            smallestDiff = None
            if len(cmpElementSet) > 0:
                for j in range(len(cmpElementSet)):
                    cmpElement2 = cmpElementSet[j]
                    cdiff = self.ratcmp.get_complex_diff(cmpElement, cmpElement2)
                    diff = num.abs_diff(cmpElement, cmpElement2) 
                    if self.ratcmp.check_complex_diff(cdiff, self.dist_thres):
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
                        (firstStep and lastIndex in last_stelement_element_indices):
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
            new_stelements.append((i,element))
            new_stelements_last_elements.append((lastIndex,lastSmallestCmpElement))
            new_stelements_info_strs.append(hist)

    def _add_new_stelement(self, new_stelement, new_stelements_info_str):
        self.allStelements.append(new_stelement)
        self.allStelementsHist.append(new_stelements_info_str)
        #Record when we start adding new stelements
        if self.newIndex == -1:
            self.newIndex = len(self.allStelements)-1

    def _update_stelement(self, new_stelement, new_stelements_info_str, k):
        self.allStelements[k] = new_stelement
        self.allStelementsHist[k] = new_stelements_info_str

    def _is_latest_stelement_closer(self, new_stelement, old_stelement, 
                                    orig_stelement):
        newDiff = self.ratcmp.get_complex_diff(new_stelement, orig_stelement)
        oldDiff = self.ratcmp.get_complex_diff(old_stelement, orig_stelement)
        return abs(newDiff) < abs(oldDiff)
