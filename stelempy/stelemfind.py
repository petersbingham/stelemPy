import pynumutil as num

default_cfsteps = 1

class StelemFind:
    def __init__(self, ratcmp, cfsteps=default_cfsteps):
        self.ratcmp = ratcmp
        self.cfsteps = cfsteps

        self.last_set = []
        self.all_sets = []

        self.all_stelements = []
        self.all_stelements_hist = []

        self.last_stelements = []
        self.lost_indices = []
        self.tot_stelements = 0
        self.tot_lost_stelements = 0
        self.new_index = -1

    def add_sets(self, sets):
        result_sets = []
        for set in sets:
            result_sets.append(self._locate_stelements(set))
        return result_sets

    def add_set(self, set):
        return self._locate_stelements(set)

#######################################################
#######################################################

    def _locate_stelements(self, set):
        si = len(self.all_sets)
        new_stelements = []
        new_stelements_last_elements = []
        new_stelements_info_strs = []
        last_stelement_element_indices = ()
        if len(self.last_stelements) > 0:
            last_stelement_element_indices = zip(*self.last_stelements)[0]
        if si >= self.cfsteps:  
            for i in range(len(set)):
                element = set[i]
                self._update_for_previous_sets(si, i, element, new_stelements,
                                               new_stelements_last_elements,
                                               new_stelements_info_strs,
                                               last_stelement_element_indices)
        self.all_sets.append(set)

        #Determine if lost stelement. If so then note.
        for last_stelement in self.last_stelements:
            new_last_indices = map(lambda x : x[0], 
                                   new_stelements_last_elements)
            if last_stelement[0] not in new_last_indices:
                for i in range(len(self.all_stelements)):
                    if self.all_stelements[i] == last_stelement[1]:
                        if i not in self.lost_indices:
                            self.lost_indices.append(i)

        # Now determine if the new stelement is a continuation of a prior 
        # stelement. If so then just update. If not then append.
        # The indices of the prior element of the new_stelement are compared to 
        # element indices of the prior stelement to establish this.
        self.new_index = -1
        # However, two new stelements may have the same last element, 
        # so we need to keep the details:
        allocation_details = {}
        for i in range(len(new_stelements)):
            new_stelement_last_element_index = new_stelements_last_elements[i][0]
            new_stelement = new_stelements[i]
            new_stelements_info_str = new_stelements_info_strs[i]
            found = False
            for j in range(len(self.last_stelements)):
                last_stelement_element_index = last_stelement_element_indices[j]
                last_stelement = self.last_stelements[j][1]
                if new_stelement_last_element_index == last_stelement_element_index:
                    if j not in allocation_details.keys():
                        # Uninitialised. Will contain index in the 
                        # self.all_stelements that this maps to, last stelement 
                        # value that was replaced. We need to keep these because
                        # if a new stelement has the same maps then need to 
                        # compared both to the original last stelement value.
                        allocation_details[j] = None 
                    found = True
                    break

            if not found:
                self._add_new_stelement(new_stelement[1], 
                                        new_stelements_info_str)
            else:
                if allocation_details[j] is None: 
                    # We dont know where it is so have to search.
                    found = False
                    for k in range(len(self.all_stelements)):
                        if last_stelement==self.all_stelements[k]:
                            if k not in self.lost_indices:
                                allocation_details[j] = [k, self.all_stelements[k]]
                                found = True
                                break
                    if not found:
                        assert False # Could not find stelement to update
                    self._update_stelement(new_stelement[1],
                                           new_stelements_info_str, k)
                else:
                    k = allocation_details[j][0]
                    orig_stelement = allocation_details[j][1]
                    if self._is_latest_stelement_closer(new_stelement[1], 
                                                        self.all_stelements[k], 
                                                        orig_stelement): 
                        #Swap them
                        self._add_new_stelement(self.all_stelements[k], 
                                                self.all_stelements_hist[k])
                        self._update_stelement(new_stelement[1], 
                                               new_stelements_info_str, k)
                    else:
                        self._add_new_stelement(new_stelement[1], 
                                                new_stelements_info_str)                    

        self.last_stelements = new_stelements

        stelements = 0
        new_stelements = 0
        lost_stelements = 0
        all_stelements_labels = []
        for i in range(len(self.all_stelements)):
            stelements += 1
            lbl = "REP"
            if self.new_index!=-1 and i>=self.new_index:
                lbl = "NEW"
                new_stelements += 1

            for j in range(len(self.lost_indices)):
                if i == self.lost_indices[j]:
                    lbl = "LOST"
                    stelements -= 1
                    lost_stelements += 1
                    break

            all_stelements_labels.append(lbl)

        self.tot_stelements = stelements+lost_stelements
        self.tot_lost_stelements = lost_stelements

        return list(self.all_stelements),\
               list(self.all_stelements_hist),\
               list(all_stelements_labels)

    def _update_for_previous_sets(self, si, i, element, new_stelements,
                                  new_stelements_last_elements, 
                                  new_stelements_info_strs,
                                  last_stelement_element_indices):
        cmp_element = element
        is_stelement = True
        hist = [(si, i)]
        first_step = True
        repeat_stelement = False
        for k in reversed(range(si-self.cfsteps, si)):
            cmp_element_set = self.all_sets[k]
            smallest_diff = None
            if len(cmp_element_set) > 0:
                for j in range(len(cmp_element_set)):
                    cmp_element2 = cmp_element_set[j]
                    cdiff = self.ratcmp.get_complex_diff(cmp_element,
                                                         cmp_element2)
                    diff = num.abs_diff(cmp_element, cmp_element2) 
                    if self.ratcmp.check_complex_diff(cdiff):
                        if smallest_diff is None or diff < smallest_diff:
                            hist_temp = (k, j)
                            smallest_diff = diff
                            smallest_cmp_element2 = cmp_element2
                            if first_step:
                                last_index = j
                                last_smallest_cmp_element = smallest_cmp_element2
                    if j==len(cmp_element_set)-1:
                        if smallest_diff is None:
                            is_stelement = False
                        elif repeat_stelement or\
                        (first_step and last_index in last_stelement_element_indices):
                            repeat_stelement = True
            else:
                is_stelement = False
            first_step = False
            if not is_stelement:
                break
            else:
                cmp_element = smallest_cmp_element2
                hist.append(hist_temp)

        if is_stelement:    
            new_stelements.append((i,element))
            new_stelements_last_elements.append((last_index,last_smallest_cmp_element))
            new_stelements_info_strs.append(hist)

    def _add_new_stelement(self, new_stelement, new_stelements_info_str):
        self.all_stelements.append(new_stelement)
        self.all_stelements_hist.append(new_stelements_info_str)
        #Record when we start adding new stelements
        if self.new_index == -1:
            self.new_index = len(self.all_stelements)-1

    def _update_stelement(self, new_stelement, new_stelements_info_str, k):
        self.all_stelements[k] = new_stelement
        self.all_stelements_hist[k] = new_stelements_info_str

    def _is_latest_stelement_closer(self, new_stelement, old_stelement, 
                                    orig_stelement):
        new_diff = self.ratcmp.get_complex_diff(new_stelement, orig_stelement)
        old_diff = self.ratcmp.get_complex_diff(old_stelement, orig_stelement)
        return abs(new_diff) < abs(old_diff)
