import numpy as np
from .process import StochasticProcessGen


class WhiteNoise(StochasticProcessGen):

    def __init__(self, dim=1, std=1, axis=1):
        # std is discrete time standard deviation
        super().__init__(dim=dim, axis=axis)
        self._name = "White Noise"

        self._std = std

    def compute(self):
        return np.random.normal(scale=self._std, size=(self._dim, self._axis))
