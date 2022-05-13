from PositioningSolver.src.stochastic_process import WhiteNoise, RandomConstant, RandomWalk, GaussMarkov, \
    power_spectral_density, StochasticProcessGen, allan_variance
import numpy as np
from PositioningSolver.src.plots.plot_manager import plot_1D, show_all, grid, loglog

###############################
# globals / control variables #
###############################
fs = 100  # sample frequency in [Hz]
t0 = 0  # first time instance of simulation in [s]
tf = 1800  # last time instance of simulation in [s]

###############################
# User Def / Configurations  ##
###############################
units = "rad/s"  # units of the measured variable
b_rw = False  # Simulate Random Walk
b_gm = True  # Simulate Gauss Markov
b_wh = False  # Simulate White Noise
b_rc = False  # Simulate Random Constant

sigma_rw = [1]  # random walk sigma
sigma_gm = [1.69684788e-05]  # gauss markov sigma
tau_gm = 100  # gauss markov correlation time
sigma_wn = [1]  # white noise sigma
sigma_rc = [1]  # random constant sigma


def plots(name, axes, trajectory, psd, allan_var):
    # unpacking data
    time, process = trajectory
    f, power = psd
    tau, a_var = allan_var

    a_dev = np.sqrt(a_var)

    # 2D trajectory
    if axes == 2:
        plot_1D(process[:, 0], process[:, 1], marker='o', markersize=4, linewidth=0.5, x_label=f"Axis 0 [{units}]",
                y_label=f"Axis 1 [{units}]",
                title=f"2D trajectory of {str(name)}", equal=True)
        grid()

    # plot timeseries
    ax = None
    for i in range(axes):
        ax = plot_1D(time, process[:, i], ax=ax, label=f"Axis {i}", x_label="Time [s]",
                     y_label=f"process [{units}]",
                     title=f"Time series of {str(name)}", set_legend=True)
    grid()

    # plot power spectral density
    ax = None
    for i in range(axes):
        ax = loglog(f, power[:, i], ax=ax, label=f"Axis {i}", x_label="Frequency [Hz]",
                    y_label=f"Power ({units})^2/Hz",
                    title=f"Power Spectral Density of {str(name)}", set_legend=True,
                    )
    grid()

    # plot allan deviation
    ax = None
    for i in range(axes):
        ax = loglog(tau, a_dev[:, i], ax=ax, label=f"Axis {i}", x_label="Tau [s]",
                    y_label=f"ADEV [{units}]",
                    title=f"Allan Deviation of {str(name)}", set_legend=True)
    grid()


def analyze_process(time, gen: StochasticProcessGen, sampling_time):
    axes = gen.axes

    # process series
    process = gen.compute(sampling_time)

    # power spectral density
    power, f = power_spectral_density(process, fs)

    # allan variance
    a_var, tau = allan_variance(process, fs)

    plots(str(gen), axes, (time, process), (f, power), (tau, a_var))

    print(f"### Statistics of the simulated realization of process {repr(gen)} ###")
    print(f"\tmean = {process.mean(axis=0)} [{units}]")
    print(f"\tstd = {process.std(axis=0)} [{units}]")
    print(f"\tmean power = {power.mean(axis=0)} [({units})^2/Hz]")
    print("")

    show_all()


def main():
    # get time vector
    time = np.arange(t0, tf, step=1 / fs)

    # Gauss Markov generator
    if b_gm:
        gauss_markov_gen = GaussMarkov(dim=len(time), std=sigma_gm, axis=len(sigma_gm),
                                       correlation_time=tau_gm)
        analyze_process(time, gauss_markov_gen, 1/fs)

    # Random Walk generator
    if b_rw:
        random_walk_gen = RandomWalk(dim=len(time), std=sigma_rw, axis=len(sigma_rw))
        analyze_process(time, random_walk_gen, 1/fs)

    # White Noise generator
    if b_wh:
        white_noise_gen = WhiteNoise(dim=len(time), std=sigma_wn, axis=len(sigma_wn))
        analyze_process(time, white_noise_gen, 1/fs)

    # Random Constant generator
    if b_rc:
        random_constant_gen = RandomConstant(dim=len(time), std=sigma_rc, axis=len(sigma_rc))
        analyze_process(time, random_constant_gen, 1/fs)


if __name__ == "__main__":
    # example
    main()
