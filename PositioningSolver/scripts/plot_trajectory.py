import os

from PositioningSolver.src.ins.gravity import *
from PositioningSolver.src.io_manager.import_timeseries.read_tm import read_csv, downsample
from PositioningSolver.src.math_utils.Constants import Constant
from PositioningSolver.src.plots.plot_manager import plot_3D_trajectory, show_all

WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")

from PositioningSolver.src.ins.attitude import *

lla = np.array([np.pi/2,-1.5, 1000])

print("gravity 1 is ", geo_param(lla)[2])

pos = np.array(Geodetic2Cartesian(*lla))
g = acceleration(pos)


m = matrix_ecef2ned(lla[0], lla[1])
g = m @ g
print("gravity 2 is", g, " norm is ", np.linalg.norm(g))
exit()

def main():
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"

    position = read_csv(WORKSPACE+ref_pos_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, 1])
    time = read_csv(WORKSPACE+ref_time_file, True, delimiter=",")
    euler = read_csv(WORKSPACE + ref_att_file, True, delimiter=",")
    # TODO change euler from yaw,pitch,roll to roll,pitch,yaw...
    position = downsample(position, 100)

    #lla2ecef(position)

    plot_3D_trajectory(position)

    show_all()

if __name__ == "__main__":
    # example
    main()
