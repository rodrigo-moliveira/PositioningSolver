import numpy as np
from .process import StochasticProcessGen


class WhiteNoise(StochasticProcessGen):

    def __init__(self, dim, std):
        # std is discrete time standard deviation
        super().__init__(dim)
        self._name = "WhiteNoise"

        self._std = std

    def compute(self):
        return np.random.normal(scale=self._std, size=self._dim)
