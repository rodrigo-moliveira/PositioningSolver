from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit
from PositioningSolver.src.ins.mechanization import lld2ecef
from PositioningSolver.src.plots.plot_manager import plot_1D, show_all, plot_3D_trajectory


class INSQualityManager:

    # main function of QualityManager
    @staticmethod
    def process(data_manager, data_dir, alg_name, performance, plot, separate_axis):

        if performance:
            # call performance evaluation..
            summary = f"----Error statistics for algorithm {alg_name}----"
            summary += data_manager.performance_evaluation()
            if data_dir is not None:
                # save summary file
                text_file = open(data_dir + "/summary.txt", "w")
                text_file.write(summary)
                text_file.close()
            print(summary)

        if plot:
            INSQualityManager.plot(data_manager, separate_axis)

    @staticmethod
    def plot(data_manager, separate_axis):
        print("plotting")
        time = getattr(data_manager, "time")

        pos = getattr(data_manager, "pos", None)
        ref_pos = getattr(data_manager, "ref_pos", None)
        INSQualityManager.plot_pos(time, pos, ref_pos)

        att = getattr(data_manager, "att", None)
        ref_att = getattr(data_manager, "ref_att", None)
        INSQualityManager.plot_generic(time, att, ref_att, separate_axis)

        vel = getattr(data_manager, "vel", None)
        ref_vel = getattr(data_manager, "ref_vel", None)
        INSQualityManager.plot_generic(time, vel, ref_vel, separate_axis)

        gyro = getattr(data_manager, "gyro", None)
        ref_gyro = getattr(data_manager, "ref_gyro", None)
        INSQualityManager.plot_generic(time, gyro, ref_gyro, separate_axis)

        accel = getattr(data_manager, "accel", None)
        ref_accel = getattr(data_manager, "ref_accel", None)
        INSQualityManager.plot_generic(time, accel, ref_accel, separate_axis)

        show_all()

    @staticmethod
    def plot_pos(time, pos, ref_pos):
        ax_latlon = None
        ax_alt = None
        ax_3d = None

        if not pos.is_empty():
            _data_matrix = convert_unit(pos.data, pos.units, pos.output_units)

            # LLD plot
            ax_latlon = plot_1D(time.data, _data_matrix[:, 0], label="lat")
            ax_latlon = plot_1D(time.data, _data_matrix[:, 1], ax=ax_latlon, title="Latitude, Longitude", label="long",
                                set_legend=True, y_label=pos.output_units[0])
            ax_alt = plot_1D(time.data, _data_matrix[:, 2], title="Altitude", label="alt", set_legend=True,
                             y_label=pos.output_units[2])

            # 3D plot
            ecef = lld2ecef(pos.data)
            ax_3d = plot_3D_trajectory(ecef, label="estimated")

            # ECEF plot

        if not ref_pos.is_empty():
            _data_matrix = convert_unit(ref_pos.data, ref_pos.units, ref_pos.output_units)

            # LLD plot
            ax_latlon = plot_1D(time.data, _data_matrix[:, 0], ax=ax_latlon, label="ref_lat")
            plot_1D(time.data, _data_matrix[:, 1], ax=ax_latlon, title="Latitude, Longitude",
                    label="ref_long", y_label=pos.output_units[0],
                    set_legend=True)
            plot_1D(time.data, _data_matrix[:, 2], title="Altitude", ax=ax_alt, label="ref_alt",
                    set_legend=True, y_label=pos.output_units[2])

            # 3D plot
            ref_ecef = lld2ecef(ref_pos.data)
            plot_3D_trajectory(ref_ecef, label="reference", ax=ax_3d)

            # ECEF plot


    @staticmethod
    def plot_generic(time, est_data, ref_data, separate_axis):
        ax = [None, None, None]

        if not est_data.is_empty():
            _data_matrix = convert_unit(est_data.data, est_data.units, est_data.output_units)
            ax[0] = plot_1D(time.data, _data_matrix[:, 0], ax=ax[0], label=est_data.legend[0],
                            title=est_data.title,
                            x_label=f"{time.description} {time.units}", y_label=est_data.output_units[0],
                            set_legend=True)
            if not separate_axis:
                ax = [ax[0], ax[0], ax[0]]
            ax[1] = plot_1D(time.data, _data_matrix[:, 1], ax=ax[1], label=est_data.legend[1],
                            title=est_data.title,
                            x_label=f"{time.description} {time.units}", y_label=est_data.output_units[1],
                            set_legend=True)
            ax[2] = plot_1D(time.data, _data_matrix[:, 2], ax=ax[2], label=est_data.legend[2],
                            title=est_data.title,
                            x_label=f"{time.description} {time.units}", y_label=est_data.output_units[2],
                            set_legend=True)

        if not ref_data.is_empty():
            _data_matrix = convert_unit(ref_data.data, ref_data.units, ref_data.output_units)
            ax[0] = plot_1D(time.data, _data_matrix[:, 0], ax=ax[0], label=ref_data.legend[0],
                            title=ref_data.title,
                            x_label=f"{time.description} {time.units}", y_label=ref_data.output_units[0],
                            set_legend=True)
            if not separate_axis:
                ax = [ax[0], ax[0], ax[0]]
            ax[1] = plot_1D(time.data, _data_matrix[:, 1], ax=ax[1], label=ref_data.legend[1],
                            title=ref_data.title,
                            x_label=f"{time.description} {time.units}", y_label=ref_data.output_units[1],
                            set_legend=True)
            ax[2] = plot_1D(time.data, _data_matrix[:, 2], ax=ax[2], label=ref_data.legend[2],
                            title=ref_data.title,
                            x_label=f"{time.description} {time.units}", y_label=ref_data.output_units[2],
                            set_legend=True)
