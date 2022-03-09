from PositioningSolver.src.stochastic_process import WhiteNoise, RandomConstant, RandomWalk, GaussMarkov
import numpy as np
from PositioningSolver.src.plots.plot_manager import plot_1D, show_all

# globals
fs = 10  # sample frequency in [Hz]
t0 = 0  # first time instance of simulation in [s]
tf = 25000  # last time instance of simulation in [s]


def main():
    time = np.arange(t0, tf, step=1 / fs)

    gauss_markov = GaussMarkov(dim=len(time), std=[1], axis=1, sampling_time=1 / fs,
                               correlation_time=50)

    random_walk = RandomWalk(dim=len(time), std=[1], axis=1)

    process = random_walk.compute()
    plot_1D(time, process)
    show_all()


if __name__ == "__main__":
    # example
    main()
