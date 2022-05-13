import numpy as np


def read_csv(filepath, ignore_header=True, delimiter=",", usecols=None, factor=None, function=None):
    _ignore = 0 if ignore_header is False else 1

    data = np.genfromtxt(filepath, delimiter=delimiter, skip_header=_ignore, usecols=usecols)

    if factor is not None:
        _shape = data.shape

        if len(_shape) == 1:
            data *= factor
        else:
            for t in range(_shape[0]):
                data[t, :] *= factor

    # apply user-defined function to data (should modify the provided array object)
    if function is not None:
        function(data)

    return data


def downsample(data, data_rate_in, frequency):

    data_rate_out = 1 / frequency

    # step to downsample the array
    _step = data_rate_out / data_rate_in
    i = 0

    _old_size = data.shape[0]

    _new = []

    for t in range(_old_size):
        if i % _step == 0:
            _new.append(data[t])
            # print(t, "sampling")
        # else:
            # print(t, "discarding")
        i += 1

    return np.array(_new)


def swap_columns(arr, start_index, last_index):
    """
    swap columns start_index and last_index.
    Example:
        Original Array :
        > my array = [[ 0  1  2]
                    [ 3  4  5]
                    [ 6  7  8]
                    [ 9 10 11]]
        > swap_columns(my_array, 0, 1)
        > After Swapping :
            [[ 1  0  2]
             [ 4  3  5]
             [ 7  6  8]
             [10  9 11]]
    """
    arr[:, [start_index, last_index]] = arr[:, [last_index, start_index]]
