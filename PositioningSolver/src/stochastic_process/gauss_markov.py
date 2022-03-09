import numpy as np
from .process import StochasticProcessGen


class GaussMarkov(StochasticProcessGen):

    def __init__(self, dim=1, std=1, correlation_time=1, axis=1, initial=None, sampling_time=1):
        # std is discrete time standard deviation
        super().__init__(dim=dim, axis=axis)
        self._name = "GaussMarkov"

        self._std = np.array(std)
        self._sampling_time = sampling_time
        self._correlation_time = correlation_time
        if initial is not None:
            if len(initial) != axis:
                raise TypeError(f"Initial value for the stochastic process has dim={len(initial)}, which is not "
                                f"consistent with the provided axes length={axis}")
            self._initial = initial
        else:
            self._initial = np.zeros(axis)

    def compute(self):
        gm_process = np.zeros((self._dim, self._axis))

        # set initial condition
        gm_process[0, :] = self._initial

        beta = 1 / self._correlation_time

        # time loop (start at t = 1)
        for t in range(1, self._dim):
            # generate gaussian noise for this epoch and all required axes
            std = self._std * np.sqrt(1.0 - np.exp(-2*beta*self._sampling_time))
            noise = np.random.normal(scale=std, size=self._axis)
            gm_process[t, :] = np.exp(-beta*self._sampling_time) * gm_process[t-1, :] + noise

        return gm_process
