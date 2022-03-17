import numpy as np

from ...data_types.basics.Epoch import Epoch


def read_timeseries(filepath, time_col, *args, ignore_header=True, delimiter=","):
    """

    :param filepath:
    :param time_col:
    :param args:
    :param ignore_header:
    :param delimiter:
    :return:
    """
    line = " "
    time = []
    dim = len(args)
    data = []

    # initialize data output list
    for i in range(dim):
        data.append([])

    with open(filepath, 'r') as f:

        # ignore fist line (with header)
        if ignore_header:
            f.readline()

        while line:
            line = f.readline()
            if len(line.strip()) == 0:
                continue

            tokens = line.split(delimiter)

            try:
                time.append(Epoch(tokens[time_col]))

                for list_index, file_col in zip(range(dim), args):
                    parsed = float(tokens[file_col])
                    (data[list_index]).append(parsed)

            except:
                raise ValueError(f"problem parsing line {line[0:-1]}")

    return time, data


def read_csv(filepath, ignore_header=True, delimiter=",", usecols=None, factor=None):
    _ignore = 0 if ignore_header is False else 1

    data = np.genfromtxt(filepath, delimiter=delimiter, skip_header=_ignore, usecols=usecols)

    if factor is not None:
        _time, _len = data.shape

        for t in range(_time):
            data[t, :] *= factor

    return data


def downsample(data, rate):
    _old_size, _len = data.shape

    _new = []

    for t in range(_old_size):
        if t % rate == 0:
            _new.append(data[t])
            print(t, "sampling")
        else:
            print(t, "discarding")

    return np.array(_new)
