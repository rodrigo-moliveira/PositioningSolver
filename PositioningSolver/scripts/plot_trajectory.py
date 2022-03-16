import os

from PositioningSolver.src.data_types.state_space.utils import *
from PositioningSolver.src.io_manager.import_timeseries.read_tm import read_csv, resample
from PositioningSolver.src.algorithms.ins.geo_utils import *
from PositioningSolver.src.plots.plot_manager import plot_3D_trajectory, show_all

WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")


def main():
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"

    position = read_csv(WORKSPACE+ref_pos_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, 1])
    time = read_csv(WORKSPACE+ref_time_file, True, delimiter=",")
    euler = read_csv(WORKSPACE + ref_att_file, True, delimiter=",")

    print(position.shape)
    position = resample(position, 100)
    print(position.shape)

    #lla2ecef(position)

    plot_3D_trajectory(position)

    show_all()

if __name__ == "__main__":
    # example
    main()
