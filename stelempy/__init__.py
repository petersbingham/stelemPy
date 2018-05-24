from stelemfind import *
from stelemconverge import *

from sets import Set

default_rtol = 0.001
default_start_rtol = 0.01

def _combine_grps(old_conv_grps, new_conv_grps):
    combined_conv_grps = {}
    for i in old_conv_grps:
        stelement = old_conv_grps[i]
        if stelement[2]!="LOST":
            combined_conv_grps[i] = stelement
    for i in new_conv_grps:
        stelement = new_conv_grps[i]
        if stelement[2]!="LOST":
            combined_conv_grps[i] = stelement
    return combined_conv_grps

# Two returns. First is group where close groups have been amalgamated.
# Second is the groups that have been amalgamated.
def _amalgamate(distinct_conv_grps, ratcmp):
    new_distinct_conv_grps = []
    combined_conv_grps = []
    combined_indices = []
    for i in range(len(distinct_conv_grps)):
        if i not in combined_indices:
            if i<len(distinct_conv_grps)-1:
                maxi1 = _get_max_index(distinct_conv_grps[i][0])
                cmpk_val1 = distinct_conv_grps[i][0][maxi1][0]
                i_repeat = False
                for j in range(i+1, len(distinct_conv_grps)):
                    maxi2 = _get_max_index(distinct_conv_grps[j][0])
                    cmpk_val2 = distinct_conv_grps[j][0][maxi2][0]
                    if ratcmp.is_close(cmpk_val1, cmpk_val2):
                        if not i_repeat:
                            combined_conv_grps.append(distinct_conv_grps[i])
                            i_repeat = True
                        combined_conv_grps.append(distinct_conv_grps[j])
                        combined_indices.append(j)
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
            new_distinct_conv_grps.append(distinct_conv_grps[i])
    return new_distinct_conv_grps, combined_conv_grps

def _combine_indices(a, b):
    return list(Set(a).union(Set(b)))

def _calculate_QIs_from_range(conv_grps, rtols):  
    QIs = []
    conv_grps.sort(key=lambda x: x[1], reverse=True)
    
    for conv_grp in conv_grps:
        smallestdk = rtols[max(conv_grp[3])]
        maxi = _get_max_index(conv_grp[0])
        QIs.append([conv_grp[0][maxi][0], smallestdk, conv_grp[2]])
    return QIs

def _get_distinct_conv_grp_index(distinct_conv_grps, conv_grp):
    for i in range(len(distinct_conv_grps)):
        filt_distinct_conv_grp = _filt_out_lost(distinct_conv_grps[i][0])
        filt_indices = filt_distinct_conv_grp.keys()
        filt_stelements = map(lambda x: x[0], filt_distinct_conv_grp.values())
        found = True
        for j in sorted(conv_grp.keys()):
            stelements = conv_grp[j]
            if stelements[2]=="LOST":
                break
            elif j not in filt_indices or stelements[0] not in filt_stelements:
                found = False
                break
        if found:
            return i
    return -1

def _filt_out_lost(conv_grp):
    non_lost_stelements = {}
    for i in conv_grp:
        stelement = conv_grp[i]
        if stelement[2]!="LOST":
            non_lost_stelements[i] = stelement
    return non_lost_stelements

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

def create_default_ratcmp():
    return num.RationalCompare1(default_rtol)

########################################################################   
######################### Public Interface #############################
########################################################################

def calculate_stelements(sets, ratcmp=None, cfsteps=default_cfsteps):
    if ratcmp is None:
        ratcmp = create_default_ratcmp()
    s = StelemFind(ratcmp, cfsteps)
    return s.add_sets(sets)

def calculate_convergence_groups(sets, stelements_results):
    s = StelemConverger(sets, stelements_results)
    convergence_groups = s.create_convergence_groups()
    s.write_prior_elements(convergence_groups)
    s.set_closest_element_to_lost(convergence_groups)
    return convergence_groups

def calculate_QIs(sets, ratcmp=None, start_rtol=default_start_rtol,
                  end_rtol=None, cfsteps=default_cfsteps, amalg_ratcmp=None):
    if ratcmp is None:
        ratcmp = create_default_ratcmp()
    ret = calculate_convergence_groups_range(sets, ratcmp, start_rtol, end_rtol,
                                             cfsteps)
    return calculate_QIs_from_range(ret, amalg_ratcmp)


# Following two functions are the two steps used for the calculate_QIs. They
# have been made public since the intermediate calculations may be of interest.
def calculate_convergence_groups_range(sets, ratcmp=None,
                                       start_rtol=default_start_rtol,
                                       end_rtol=None, cfsteps=default_cfsteps):
    if ratcmp is None:
        ratcmp = create_default_ratcmp()
    tab_counts = []
    convergence_groups_range = []
    rtols = []

    rtol = start_rtol    
    while True:
        rtols.append(rtol)
        ratcmp.set_rtol(rtol)
        sf = StelemFind(ratcmp, cfsteps)   
        stelements_results = sf.add_sets(sets)
        tab_counts.append((sf.tot_stelements, sf.tot_lost_stelements))

        sc = StelemConverger(sets, stelements_results)
        convergence_groups = sc.create_convergence_groups()
        sc.write_prior_elements(convergence_groups)
        sc.set_closest_element_to_lost(convergence_groups)
        convergence_groups_range.append(convergence_groups)

        stop = (end_rtol is not None and rtol < end_rtol*1.1)
        if sf.tot_stelements != 0 and not stop:
            rtol /= 10.0
        else:
            break

    return convergence_groups_range, tab_counts, rtols

def calculate_QIs_from_range(convergence_groups_range_ret, amalg_ratcmp=None):
    convergence_groups_range = convergence_groups_range_ret[0]
    rtols = convergence_groups_range_ret[2]
    
    distinct_conv_grps = []
    for i_dt in range(len(rtols)):
        conv_grps = convergence_groups_range[i_dt]
        if len(conv_grps) > 0:
            conv_lens =  map(lambda conv_grp: _get_conv_len(conv_grp), 
                             conv_grps)
            tot_conv_len = sum(conv_lens)

            for conv_grp,conv_len in zip(conv_grps,conv_lens):
                conv_len_ratio = float(conv_len)/tot_conv_len
                
                i = _get_distinct_conv_grp_index(distinct_conv_grps, conv_grp)
                if i == -1:
                    distinct_conv_grp = [conv_grp, conv_len_ratio, conv_len, 
                                         [i_dt]]
                    distinct_conv_grps.append( distinct_conv_grp )
                else:
                    #Update set:
                    old_conv_grp = distinct_conv_grps[i][0]
                    conv_len_ratio += distinct_conv_grps[i][1]
                    conv_len += distinct_conv_grps[i][2]
                    dt_indices = distinct_conv_grps[i][3]
                    if i_dt not in dt_indices:
                        dt_indices.append(i_dt)
                    distinct_conv_grps[i][0] = _combine_grps(old_conv_grp, 
                                                             conv_grp)
                    distinct_conv_grps[i][1] = conv_len_ratio
                    distinct_conv_grps[i][2] = conv_len
                    distinct_conv_grps[i][3] = dt_indices
    if amalg_ratcmp:
        distinct_conv_grps, combined_conv_grps = _amalgamate(distinct_conv_grps, 
                                                             amalg_ratcmp)
    ret_a = _calculate_QIs_from_range(distinct_conv_grps, rtols)
    ret_b = None
    if amalg_ratcmp:
        ret_b = _calculate_QIs_from_range(combined_conv_grps, rtols)
    return ret_a, ret_b
