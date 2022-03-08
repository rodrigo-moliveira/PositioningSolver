import numpy as np
from .process import StochasticProcessGen


class RandomConstant(StochasticProcessGen):

    def __init__(self, dim, std):
        # std is discrete time standard deviation
        super().__init__(dim)
        self._name = "RandomConstant"

        self._std = std

    def compute(self):
        val = np.random.normal(scale=self._std, size=1)
        return np.ones(self._dim) * val
