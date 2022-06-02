from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit
from PositioningSolver.src.ins.mechanization import lld2ecef
from PositioningSolver.src.plots.plot_manager import plot_1D, show_all, plot_3D_trajectory


class INSQualityManager:

    # main function of QualityManager
    @staticmethod
    def process(data_manager, data_dir, alg_name, performance, plot):

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
            INSQualityManager.plot(data_manager)

    @staticmethod
    def plot(data_manager):
        print("plotting")
        time = getattr(data_manager, "time")

        pos = getattr(data_manager, "pos", None)
        ref_pos = getattr(data_manager, "ref_pos", None)
        INSQualityManager.plot_pos(time, pos, ref_pos)

        att = getattr(data_manager, "att", None)
        ref_att = getattr(data_manager, "ref_att", None)
        INSQualityManager.plot_att(time, att, ref_att)

        vel = getattr(data_manager, "vel", None)
        ref_vel = getattr(data_manager, "ref_vel", None)
        INSQualityManager.plot_vel(time, vel, ref_vel)


        show_all()

    @staticmethod
    def plot_pos(time, pos, ref_pos):
        ax_latlon = None
        ax_alt = None
        ax_3d = None

        if not pos.is_empty():
            _data_matrix = convert_unit(pos.data, pos.units, pos.output_units)
            ax_latlon = plot_1D(time.data, _data_matrix[:, 0], label="lat")
            ax_latlon = plot_1D(time.data, _data_matrix[:, 1], ax=ax_latlon, title="Latitude, Longitude", label="long",
                                set_legend=True)
            ax_alt = plot_1D(time.data, _data_matrix[:, 2], title="Altitude", label="alt", set_legend=True)
            ecef = lld2ecef(pos.data)
            ax_3d = plot_3D_trajectory(ecef, label="estimated")

        if not ref_pos.is_empty():
            _data_matrix = convert_unit(ref_pos.data, ref_pos.units, ref_pos.output_units)
            ax_latlon = plot_1D(time.data, _data_matrix[:, 0], ax=ax_latlon, label="ref_lat")
            ax_latlon = plot_1D(time.data, _data_matrix[:, 1], ax=ax_latlon, title="Latitude, Longitude", label="ref_long",
                                set_legend=True)
            ax_alt = plot_1D(time.data, _data_matrix[:, 2], title="Altitude", ax=ax_alt, label="ref_alt", set_legend=True)
            ecef = lld2ecef(ref_pos.data)
            ax_3d = plot_3D_trajectory(ecef, label="reference", ax=ax_3d)

    @staticmethod
    def plot_att(time, att, ref_att):
        ax = None

        if not att.is_empty():
            _data_matrix = convert_unit(att.data, att.units, att.output_units)
            ax = plot_1D(time.data, _data_matrix[:, 0], ax=ax, label="roll")
            ax = plot_1D(time.data, _data_matrix[:, 1], ax=ax, label="pitch")
            ax = plot_1D(time.data, _data_matrix[:, 2], ax=ax, label="yaw", title="Attitude (Euler Angles)",
                         set_legend=True)

        if not ref_att.is_empty():
            _data_matrix = convert_unit(ref_att.data, ref_att.units, ref_att.output_units)
            ax = plot_1D(time.data, _data_matrix[:, 0], ax=ax, label="ref_roll")
            ax = plot_1D(time.data, _data_matrix[:, 1], ax=ax, label="ref_pitch")
            ax = plot_1D(time.data, _data_matrix[:, 2], ax=ax, label="ref_yaw", title="Attitude (Euler Angles)",
                         set_legend=True)

    @staticmethod
    def plot_vel(time, vel, ref_vel):
        ax = None

        if not vel.is_empty():
            _data_matrix = convert_unit(vel.data, vel.units, vel.output_units)
            ax = plot_1D(time.data, _data_matrix[:, 0], ax=ax, label="v_N")
            ax = plot_1D(time.data, _data_matrix[:, 1], ax=ax, label="v_E")
            ax = plot_1D(time.data, _data_matrix[:, 2], ax=ax, label="v_D", title="NED Velocity", set_legend=True)

        if not ref_vel.is_empty():
            _data_matrix = convert_unit(ref_vel.data, ref_vel.units, ref_vel.output_units)
            ax = plot_1D(time.data, _data_matrix[:, 0], ax=ax, label="ref_v_N")
            ax = plot_1D(time.data, _data_matrix[:, 1], ax=ax, label="ref_v_E")
            ax = plot_1D(time.data, _data_matrix[:, 2], ax=ax, label="ref_v_D", title="NED Velocity", set_legend=True)

    @staticmethod
    def plot_gyro(time, gyro):
        ax = None
        # TODO continuar aqui
        if not gyro.is_empty():
            _data_matrix = convert_unit(gyro.data, gyro.units, gyro.output_units)
            ax = plot_1D(time.data, _data_matrix[:, 0], ax=ax, label="w_x")
            ax = plot_1D(time.data, _data_matrix[:, 1], ax=ax, label="w_y")
            ax = plot_1D(time.data, _data_matrix[:, 2], ax=ax, label="w_z", title="NED Velocity", set_legend=True)