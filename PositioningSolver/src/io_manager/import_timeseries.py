from PositioningSolver.src.data_types.basics.Epoch import Epoch


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
