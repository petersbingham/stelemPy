from stelemfind import *
from stelemconverge import *

from sets import Set

default_starting_dist_thres = 0.01

def _combine_grps(old_conv_grps, new_conv_grps):
    combinedConvGrps = {}
    for i in old_conv_grps:
        stelement = old_conv_grps[i]
        if stelement[2]!="LOST":
            combinedConvGrps[i] = stelement
    for i in new_conv_grps:
        stelement = new_conv_grps[i]
        if stelement[2]!="LOST":
            combinedConvGrps[i] = stelement
    return combinedConvGrps

# Two returns. First is group where close groups have been amalgamated.
# Second is the groups that have been amalgamated.
def _amalgamate(distinct_conv_grps, amalg_thres, ratcmp):
    if ratcmp is None:
        ratcmp = num.RationalCompare1(10**(-default_zeroValExp), amalg_thres)
    newDistinctConvGrps = []
    combinedConvGrps = []
    combinedIndices = []
    for i in range(len(distinct_conv_grps)):
        if i not in combinedIndices:
            if i<len(distinct_conv_grps)-1:
                maxi1 = _get_max_index(distinct_conv_grps[i][0])
                cmpkVal1 = distinct_conv_grps[i][0][maxi1][0]
                iRepeat = False
                for j in range(i+1, len(distinct_conv_grps)):
                    maxi2 = _get_max_index(distinct_conv_grps[j][0])
                    cmpkVal2 = distinct_conv_grps[j][0][maxi2][0]
                    if ratcmp.is_close(cmpkVal1, cmpkVal2):
                        if not iRepeat:
                            combinedConvGrps.append(distinct_conv_grps[i])
                            iRepeat = True
                        combinedConvGrps.append(distinct_conv_grps[j])
                        combinedIndices.append(j)
                        if maxi1 > maxi2:
                            conv_grp = distinct_conv_grps[i][0]
                        else:
                            conv_grp = distinct_conv_grps[j][0]
                        # Update calculations, using higher N:
                        dt_indices1 = distinct_conv_grps[i][3]
                        dt_indices2 = distinct_conv_grps[j][3]
                        dt_indices = _combine_indices(dt_indices1, dt_indices2)
                        u1 = distinct_conv_grps[i][1]+distinct_conv_grps[j][1]
                        u2 = distinct_conv_grps[i][2]+distinct_conv_grps[j][2]
                        distinct_conv_grps[i] = [conv_grp, u1, u2, dt_indices]
            newDistinctConvGrps.append(distinct_conv_grps[i])
    return newDistinctConvGrps, combinedConvGrps

def _combine_indices(a, b):
    return list(Set(a).union(Set(b)))

def _calculate_QIs_from_range(conv_grps, dist_thress):  
    QIs = []
    conv_grps.sort(key=lambda x: x[1], reverse=True)
    
    for conv_grp in conv_grps:
        smallestdk = dist_thress[max(conv_grp[3])]
        maxi = _get_max_index(conv_grp[0])
        QIs.append([conv_grp[0][maxi][0], smallestdk, conv_grp[2]])
    return QIs

def _get_distinct_conv_grp_index(distinct_conv_grps, conv_grp):
    for i in range(len(distinct_conv_grps)):
        filtDistinctConvGrp = _filt_out_lost(distinct_conv_grps[i][0])
        filtIndices = filtDistinctConvGrp.keys()
        filtStelements = map(lambda x: x[0], filtDistinctConvGrp.values())
        found = True
        for j in sorted(conv_grp.keys()):
            stelements = conv_grp[j]
            if stelements[2]=="LOST":
                break
            elif j not in filtIndices or stelements[0] not in filtStelements:
                found = False
                break
        if found:
            return i
    return -1

def _filt_out_lost(conv_grp):
    nonLostStelements = {}
    for i in conv_grp:
        stelement = conv_grp[i]
        if stelement[2]!="LOST":
            nonLostStelements[i] = stelement
    return nonLostStelements

def _is_conv(stelement):
    return stelement[2]!="LOST" and stelement[2]!="PRE"

def _get_conv_len(conv_grp):
    return sum(_is_conv(stelement) for stelement in conv_grp.values())
    
def _get_max_index(conv_grp):
    imax = 0
    for i in conv_grp:
        stelement = conv_grp[i]
        if _is_conv(stelement) and i>imax:
            imax = i
    return imax

########################################################################   
######################### Public Interface #############################
########################################################################

def calculate_stelements(sets, dist_thres=default_dist_thres, 
                         cfsteps=default_cfsteps, ratcmp=None):
    s = StelemFind(dist_thres, cfsteps, ratcmp)
    return s.add_sets(sets)
    
def calculate_convergence_groups(sets, stelements_results):
    s = StelemConverger(sets, stelements_results)
    convergenceGroups = s.create_convergence_groups()
    s.write_prior_elements(convergenceGroups)
    s.set_closest_element_to_lost(convergenceGroups)
    return convergenceGroups

def calculate_QIs(sets, starting_dist_thres=default_starting_dist_thres,
                  end_dist_thres=None, cfsteps=default_cfsteps, amalg_thres=0.,
                  ratcmp=None):
    ret = calculate_convergence_groups_range(sets, starting_dist_thres, end_dist_thres,
                                          cfsteps, ratcmp)
    return calculate_QIs_from_range(ret, amalg_thres, ratcmp)


# Following two functions are the two steps used for the calculate_QIs. They have
# been made public since the intermediate calculations may be of interest.
def calculate_convergence_groups_range(sets, 
                                starting_dist_thres=default_starting_dist_thres, 
                                end_dist_thres=None, cfsteps=default_cfsteps, 
                                ratcmp=None):
    tabCounts = []
    convergenceGroupsRange = []
    dist_thress = []

    dist_thres = starting_dist_thres    
    while True:
        dist_thress.append(dist_thres)

        sf = StelemFind(dist_thres, cfsteps, ratcmp)   
        stelements_results = sf.add_sets(sets)
        tabCounts.append((sf.totStelements, sf.totLostStelements))

        sc = StelemConverger(sets, stelements_results)
        convergenceGroups = sc.create_convergence_groups()
        sc.write_prior_elements(convergenceGroups)
        sc.set_closest_element_to_lost(convergenceGroups)
        convergenceGroupsRange.append(convergenceGroups)

        stop = (end_dist_thres is not None and dist_thres < end_dist_thres*1.1)
        if sf.totStelements != 0 and not stop:
            dist_thres /= 10.0
        else:
            break

    return convergenceGroupsRange, tabCounts, dist_thress

def calculate_QIs_from_range(convergence_groups_range_ret, amalg_thres=0., 
                             ratcmp=None):
    convergenceGroupsRange = convergence_groups_range_ret[0]
    dist_thress = convergence_groups_range_ret[2]
    
    distinct_conv_grps = []
    for i_dt in range(len(dist_thress)):
        conv_grps = convergenceGroupsRange[i_dt]
        if len(conv_grps) > 0:
            convLens =  map(lambda conv_grp: _get_conv_len(conv_grp), conv_grps)
            totConvLen = sum(convLens)

            for conv_grp,convLen in zip(conv_grps,convLens):
                convLenRatio = float(convLen)/totConvLen
                
                i = _get_distinct_conv_grp_index(distinct_conv_grps, conv_grp)
                if i == -1:
                    distinctConvGrp = [conv_grp, convLenRatio, convLen, [i_dt]]
                    distinct_conv_grps.append( distinctConvGrp )
                else:
                    #Update set:
                    oldConvGrp = distinct_conv_grps[i][0]
                    convLenRatio += distinct_conv_grps[i][1]
                    convLen += distinct_conv_grps[i][2]
                    dt_indices = distinct_conv_grps[i][3]
                    if i_dt not in dt_indices:
                        dt_indices.append(i_dt)
                    distinct_conv_grps[i][0] = _combine_grps(oldConvGrp, conv_grp)
                    distinct_conv_grps[i][1] = convLenRatio
                    distinct_conv_grps[i][2] = convLen
                    distinct_conv_grps[i][3] = dt_indices
    if amalg_thres > 0.:
        distinct_conv_grps, combinedConvGrps = _amalgamate(distinct_conv_grps, 
                                                         amalg_thres, ratcmp)
    ret_a = _calculate_QIs_from_range(distinct_conv_grps, dist_thress)
    ret_b = None
    if amalg_thres > 0.:
        ret_b = _calculate_QIs_from_range(combinedConvGrps, dist_thress)
    return ret_a, ret_b