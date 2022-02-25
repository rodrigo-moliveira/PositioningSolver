import numpy as np

from ..data_types.containers.TimeSeries import TimeSeries


def compute_RMS_dynamic(vEpochs, series1: TimeSeries, series2: TimeSeries):
    RMS = TimeSeries()

    for epoch in vEpochs:
        vector1 = series1.get_data_for_epoch(epoch)
        vector2 = series2.get_data_for_epoch(epoch)

        # make sure both vectors have the same size
        if len(vector1) != len(vector2):
            raise TypeError(f"Error in RMS computation: both time series should have the same size:"
                            f" series 1 = {vector1}, series 2 = {vector2}")

        # compute rms for each epoch
        diff = vector1 - vector2
        rms = np.linalg.norm(diff)
        RMS.set_data(epoch, rms)

    return RMS


def compute_error_dynamic(vEpochs, series1: TimeSeries, series2: TimeSeries):
    x = TimeSeries()
    y = TimeSeries()
    z = TimeSeries()

    for epoch in vEpochs:
        vector1 = series1.get_data_for_epoch(epoch)
        vector2 = series2.get_data_for_epoch(epoch)

        # make sure both vectors have the same size
        if len(vector1) != len(vector2):
            raise TypeError(f"Error in RMS computation: both time series should have the same size:"
                            f" series 1 = {vector1}, series 2 = {vector2}")

        # compute rms for each epoch
        diff = vector1 - vector2
        x.set_data(epoch, diff[0])
        y.set_data(epoch, diff[1])
        z.set_data(epoch, diff[2])

    return x, y, z


def compute_error_static(rms, receiver_pos: TimeSeries, true_pos, frame):
    vEpochs = receiver_pos.get_all_epochs()

    for epoch in vEpochs:
        if frame == "ECEF":
            receiver = receiver_pos.get_data_for_epoch(epoch).copy()
            error = true_pos - receiver

            rms.set_rms_data(epoch, error)

        elif frame == "ENU":
            receiver = receiver_pos.get_data_for_epoch(epoch).copy()
            receiver.observer = true_pos
            receiver.frame = "ENU"

            rms.set_rms_data(epoch, receiver)


def compute_RMS_stats_static(error_series: TimeSeries):

    vEpochs = error_series.get_all_epochs()
    rms_x = rms_y = rms_z = rms_2d = rms_3d = 0

    for epoch in vEpochs:
        error = error_series.get_data_for_epoch(epoch)

        rms_x += error.x * error.x
        rms_y += error.y * error.y
        rms_z += error.z * error.z

        rms_2d += error.x * error.x + error.y * error.y
        rms_3d += error.x * error.x + error.y * error.y + error.z * error.z

    # 1D RMS stats
    rms_x = np.sqrt(1 / len(vEpochs) * rms_x)
    rms_y = np.sqrt(1 / len(vEpochs) * rms_y)
    rms_z = np.sqrt(1 / len(vEpochs) * rms_z)

    # 2D RMS stats
    rms_2d = np.sqrt(1 / len(vEpochs) * rms_2d)

    # 3D RMS stats
    rms_3d = np.sqrt(1 / len(vEpochs) * rms_3d)

    return {"x": rms_x,
            "y": rms_y,
            "z": rms_z,
            "2D": rms_2d,
            "3D": rms_3d
            }
