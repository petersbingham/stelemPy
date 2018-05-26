# stelempy
Python package to find and quantify stable elements over a number of sets.

## Installation

Clone the repository and install with the following commands:

    git clone https://github.com/petersbingham/stelempy.git
    cd stelempy
    python setup.py install
    
## Dependencies
Author packages (these will have their own dependencies):
 - pynumutil https://github.com/petersbingham/pynumutil
    
## Overview
For a number of successive sets, that don't necessarily have the same cardinality, stelempy provides the following:
 1. Determines, within user provided criteria, the elements (either real or complex) that are deemed close to one another across the successive sets. Collectively, the set of close elements (one from each qualifying set) are referred to as a stelement (stable- or static- element) and are often labelled with the value of the element in the final contributing set. The RationalCompare1 in the pynumutil is used for the comparison.
 2. Creates tables showing the behaviour of the elements comprising the stelements across all relevant sets as well as sorting and quantifing the stelements according to how prevalent their elements are across all of the sets and to their degree of 'closeness'.

### Finding the stelements

For example, consider the following sets (using python list notation): 
```python
[[ 0.345435, 100.456652, 3.234432 ], 
[ 1.543873, 3.234098, 58.384072, 894.873620 ],
[ 894.834506, 3.234091, 0.345871 ]]
```

We can see that there is an element close to 3.234 in all three sets and one close to 894.8 in the final two sets. There is an element close to 0.345 in the first and last sets. However, this is discounted since the requirement is that the close elements must be in successive sets.

The criteria used to find stelements are as follows:

 1. The `rtol`. This is the value over which the elements are regarded as distinct.
 2. `cfsteps`. This is the number of steps over successive sets between which elements must be located within the `rtol` to be regarded as comprising, or contributing to a stelement. In the example, for `rtol` of 0.1 and `cfsteps` of 2, 3.234091 would be the only located stelement. If `cfsteps` is lowered to 1 then 0.345871 would also be located as a stelement.

### Sorting the stelements
Once all the stelements have been found we may wish to sort them by how prevalent they are across all of the sets and to their degree of 'closeness'. In the example if we have a `cfsteps` of 1 then 3.234 will be identified twice and 0.345 once. Also, some stelements may have elements that are, on average, closer to one another than the elements comprising other stelements. The routine calculates quality indicators as follows:
 1. It locates all stelements for `rtol`s starting at a specified value and then decreasing by factors of 10 until no more stelements are located. Thus each stelement can be allocated a smallest `rtol`.
 2. The total number of steps for all `rtol`s that the stelement was located.

In addition, the package also shows the elements, arranged in order of initial sets comprising each of the stelements.

## Usage

For the comparison tests carried out the user can provide an optional interface that is referred to as `ratcmp` in the parameter lists below. An example of this, which may be used, is the `RationalCompare1` class in the pynumutil. Basically the following functions must be implemented: `set_rtol(rtol)`, `is_close(cval1, cval2)`, `get_complex_diff(cval1, cval2)` and `check_complex_diff(cdiff)`. If the `ratcmp` is not supplied then a `RationalCompare1` will be created with an `rtol=0.001`

There are three main public functions, `calculate_stelements`, `calculate_convergence_groups` and `calculate_QIs`. The first two of these functions are designed to be used together to find stelements and their characteristics. The third function is used to calculate stelements, without the details but with a couple of numbers to quantify their 'quality'. There are two additional functions `calculate_convergence_groups_range` and `calculate_QIs_from_range` which are provided in the case that the intermediate calculations for `calculate_QIs` are required.

#### `calculate_stelements` and `calculate_convergence_groups`

`calculate_stelements(sets, ratcmp=None, cfsteps=default_cfsteps)` performs the functionality described in the section titled 'Finding the stelements'. It takes as input the sets as a list of lists. The user can optionally supply a `ratcmp` and the number of steps over which closeness of elements must be obtained before they can qualify and contribute to a stelement. As output it returns a structure containing the stelements and their description. For example, with a `cfsteps` equal to 1:

Input:
```python
[[1.01,2.01,3.,4.,5],[6.,2.001,1.001,7.,8.],
 [9.,10.,1.0001,11.,2.0001],[12.,13.,1.00001,14.,15.]]
```
Output: 
```python
[([], [], []),

 ([2.001, 1.001],
  [[(1, 1), (0, 1)],[(1, 2), (0, 0)]],
  ['NEW', 'NEW']),

 ([2.0001, 1.0001],
  [[(2, 4), (1, 1)],[(2, 2), (1, 2)]],
  ['REP', 'REP']),

 ([2.0001, 1.00001],
  [[(2, 4), (1, 1)],[(3, 2), (2, 2)]],
  ['LOST', 'REP'])
]
```
The meaning of the input should be obvious, it is the supplied sets. The output has four tuples in a list, one respectively for each of the inputted sets. Essentially the tuples describe the stelements located for that particular set. The first tuple `([], [], [])` tells us that no stelements have been found for the first set; as expected since we've yet to compare it to anything. The first list element of the second tuple `[2.001, 1.001]` tells us that two stelements have been located and has conveyed them using the values in the respective set. The second list element `[[(1, 1), (0, 1)],[(1, 2), (0, 0)]]` shows the contribution history for the two stelements (in respective order). For the list tuples `[(1, 1), (0, 1)]` the first elements refer to the set index and the second the index of the element in that set. So `(1, 1)` means that 2.001 exists in set index 1 at index 1 in that set. The second tuple `(0, 1)` refers to the preceeding set within which the element close to 2.001 was found, ie the location of 2.01 in the first set. The number of tuples in the contribution history list will be equal to `cfsteps+1`. The final list in the outer tuple (eg `['NEW', 'NEW']`) shows the status of the stelements (again in respective order). The status can be either `NEW`, `REP` or `LOST`. `NEW` means the stelement has been located for the first time in that set, `REP` means that it's a continuation of an already discovered stelement and `LOST` means that a previously discovered stelement was not continued to this set.

`calculate_convergence_groups(sets, stelements_results)`

This function supplements `calculate_stelements` by showing a detailed history of the obtained stelements. It takes the same `sets` input that was supplied to `calculate_stelements` as well as the output from that function as the `stelements_results` parameter. ie both the input and outputs described in the previous section. The output of this function using the input sets and output from the previous example will be:
```python
[{0: [2.01, None, 'PRE'], 
  1: [2.001, [(1, 1), (0, 1)], 'NEW'], 
  2: [2.0001, [(2, 4), (1, 1)], 'REP'], 
  3: [1.00001, None, 'LOST']},

 {0: [1.01, None, 'PRE'], 
  1: [1.001, [(1, 2), (0, 0)], 'NEW'], 
  2: [1.0001, [(2, 2), (1, 2)], 'REP'], 
  3: [1.00001, [(3, 2), (2, 2)], 'REP']}]
```
There are two dictionaries returned, one for each of the discovered stelements. The key of the dictionary refers to the set index. The value of the dictionary is a list showing the value of the contributing element in that set, the contribution history and the status. The `PRE` indicates that the stelement had not been identified in this set and the value given is the element at its historical index (eg 2.01 corresponds to (0, 1) in the subsequent set's contribution history). When the stelement has been `LOST` the closest element in that set to the last contributing element is shown as the value, hence the 1.00001 for `3: [1.00001, None, 'LOST']` for the first stelement. The `LOST` values are for information only and do not comprise the stelement.

#### `calculate_QIs`

This performs the functionality described in the section titled 'Sorting the stelements'. The aim of this function is to return a list of stelements, each accompanied with two quantities representing the 'quality' of the stelement. The signature looks like:
`calculate_QIs(sets, ratcmp=None, start_rtol=default_start_rtol, end_rtol=None, cfsteps=default_cfsteps, amalg_ratcmp=None)`, where `default_start_rtol = 0.01` and `default_cfsteps = 1`. The optional parameters are an `ratcmp`, a number of steps, the rtol that the routine starts at, an optional end rtol (default is to continue until no more stelements are found), a qualifying number of steps and an amalgamation `ratcmp`. The amalgamation `ratcmp` is used when there are several elements in a set that are all very close together. More details on this below. 

The set used for the previous example:
```python
[[1.01,2.01,3.,4.,5],[6.,2.001,1.001,7.,8.],
 [9.,10.,1.0001,11.,2.0001],[12.,13.,1.00001,14.,15.]]
```
will give the following output from `calculate_QIs` using the default parameters:
```python
([[1.00001, 0.0001, 6], [2.0001, 0.001, 3]], None)
```
the second element `None` can be ignored for now (it's only relevant for non-zero `amalg_rtol`s). The first tuple element gives the two stelements with their QIs, so for the first stelement, `[1.00001, 0.0001, 6]`,  1.00001 is the value of the element in the last set which contributed to the stelement, 0.0001 is the lowest `rtol` at which the stelement was detected and 6 is the total number of steps across all sets and all `rtol`s where the stelement was detected.

When an amalgamation `ratcmp` is provided then once all stelements have been initially located those that are deemed close by the `amalg_ratcmp` are merged and the QIs adjusted accordingly. The first element of the returned tuple will contain the analgamated stelements and the summed QIs. The second element (`None` in the example above) is very much secondary and will contain the stelements that were merged to give the first element of the tuple.

#### `calculate_convergence_groups_range` and `calculate_QIs_from_range` 
These functions split the `calculate_QIs` into two function calls, with intermediate calculations being outputted from `calculate_convergence_groups_range`. The signatures look like:
`calculate_convergence_groups_range(sets, ratcmp=None, start_rtol=default_start_rtol, end_rtol=None, cfsteps=default_cfsteps)` and `calculate_QIs_from_range(convergence_groups_range_ret, amalg_ratcmp=None)`
The output from `calculate_convergence_groups_range` is a tuple of three lists. The first list contains all the results from `calculate_convergence_groups` for all of the `rtol`s, the second list are tuples containing the total number of stelements and the number of lost stelements for all of the `rtol`s and the third list contains all the `rtol`s at which a calculation was performed. This returned tuple can then be passed to `calculate_QIs_from_range` to perform the equivalent calculation provided by `calculate_QIs`.
