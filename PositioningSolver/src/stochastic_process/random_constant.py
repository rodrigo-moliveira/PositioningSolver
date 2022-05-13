import numpy as np
from .process import StochasticProcessGen


class RandomConstant(StochasticProcessGen):

    def __init__(self, dim=1, std=1, axis=1):
        # std is discrete time standard deviation
        super().__init__(dim=dim, axis=axis)
        self._name = "Random Constant"

        self._std = std

    def compute(self, *args):
        val = np.random.normal(scale=self._std, size=self._axis)

        return np.ones((self._dim, self._axis)) * val
