import numpy as np
import ampworks as amp


def test_combinations():

    names = ['a', 'b']
    values = [np.array([0., 1.]), np.array([3., 4.])]

    combinations_nonames = amp.mathutils.combinations(values)
    combinations_names = amp.mathutils.combinations(values, names)

    no_names = []
    with_names = []
    for a in values[0]:
        new_nonames, new_names = {}, {}
        new_nonames[0], new_names['a'] = a, a
        for b in values[1]:
            new_nonames[1], new_names['b'] = b, b

            no_names.append(new_nonames.copy())
            with_names.append(new_names.copy())

    assert combinations_nonames == no_names
    assert combinations_names == with_names
