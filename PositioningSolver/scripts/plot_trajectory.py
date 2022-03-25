import os

from PositioningSolver.src.io_manager.import_timeseries.read_tm import read_csv, downsample
from PositioningSolver.src.math_utils.Constants import Constant
from PositioningSolver.src.plots.plot_manager import plot_3D_trajectory, show_all

WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")


def main():
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"

    # Read Reference PVAT
    position = read_csv(WORKSPACE+ref_pos_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, 1])
    time = read_csv(WORKSPACE+ref_time_file, True, delimiter=",")
    # euler = read_csv(WORKSPACE + ref_att_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, 1],
    #                 function=lambda x: swap_columns(x, 0, 2))

    period = time[1] - time[0]
    frequency = 1  # output frequency, in Hz

    position = downsample(position, period, frequency)
    time = downsample(time, period, frequency)
    # euler = downsample(euler, period, frequency)

    plot_3D_trajectory(position)

    show_all()


if __name__ == "__main__":
    main()
