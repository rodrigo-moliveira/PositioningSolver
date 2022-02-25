from numpy import sqrt

from ..src.io_manager.import_timeseries import read_timeseries
from ..src.plots.plot_manager import *
from ..src.config import config


def main(file):
    config.read_configure_json(file)

    pt_ax = rms_ax = enu_ax = dop_ax = None

    for name, path in config.items():

        pt_file = rms_file = enu_file = dop_file = ""

        # Clock bias vs time plot
        try:
            pt_file = path + "/output/PositionTime.txt"
            time, data = read_timeseries(pt_file, 0, 7)

            pt_ax = plot_1D(time, data[0], label=name, x_label="Time", y_label="Clock bias [s]",
                            title="Receiver Clock Bias", set_legend=True, ax=pt_ax)
        except Exception as e:
            print(f"Error reading file {pt_file} due to exception {e}")

        # 3D RMS vs Time plot
        try:
            rms_file = path + "/output/RMS_ECEF.txt"
            time, (x, y, z) = read_timeseries(rms_file, 0, 1, 2, 3)
            rms = [sqrt(x[i] ** 2 + y[i] ** 2 + z[i] ** 2) for i in range(len(x))]

            rms_ax = plot_1D(time, rms, label=name, x_label="Time", y_label="RMS [m]", title="Estimation RMS error",
                             set_legend=True, ax=rms_ax)
        except Exception as e:
            print(f"Error reading file {rms_file} due to exception {e}")

        # Horizontal error: East vs North scatter plot
        try:
            enu_file = path + "/output/RMS_ENU.txt"
            time, (east, north, up) = read_timeseries(enu_file, 0, 1, 2, 3)

            enu_ax = plot_2D_trajectory(east, north, label=name, x_label="East [m]", y_label="North [m]",
                                        title="Horizontal error", set_legend=True, ax=enu_ax)
        except Exception as e:
            print(f"Error reading file {enu_file} due to exception {e}")

        # Geometry DOP vs Time plot
        try:
            dop_file = path + "/output/DOPs.txt"
            time, geometry = read_timeseries(dop_file, 0, 1)

            dop_ax = plot_1D(time, geometry[0], label=name, x_label="Time", y_label="DOP [m]", title="Geometry DOP",
                             set_legend=True, ax=dop_ax)
        except Exception as e:
            print(f"Error reading file {dop_file} due to exception {e}")

    # plotting true static position
    plot_2D_trajectory([0], [0], label="True Position", x_label="East [m]", y_label="North [m]",
                       title="Horizontal error", set_legend=True, ax=enu_ax, marker="*")
    show_all()
