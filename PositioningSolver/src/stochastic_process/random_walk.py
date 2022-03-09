import numpy as np
from .process import StochasticProcessGen


class RandomWalk(StochasticProcessGen):

    def __init__(self, dim=1, std=1, axis=1, initial=None):
        # std is discrete time standard deviation
        super().__init__(dim=dim, axis=axis)
        self._name = "RandomWalk"

        self._std = std
        if initial is not None:
            if len(initial) != axis:
                raise TypeError(f"Initial value for the stochastic process has dim={len(initial)}, which is not "
                                f"consistent with the provided axes length={axis}")
            self._initial = initial
        else:
            self._initial = np.zeros(axis)

    def compute(self):
        walk = np.zeros((self._dim, self._axis))

        # set initial condition
        walk[0, :] = self._initial

        # time loop (start at t = 1)
        for t in range(1, self._dim):
            # generate gaussian noise for this epoch and all required axes
            n = np.random.normal(scale=self._std, size=self._axis)
            walk[t, :] = walk[t-1, :] + n

        return walk
