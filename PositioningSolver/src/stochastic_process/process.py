import numpy as np


class StochasticProcessGen:
    def __init__(self, dim=1, axis=1):
        self._dim = dim
        self._axis = axis
        self._name = "General Process"

    def __repr__(self):
        return f"StochasticProcess({self._name}, dim = {self._dim}, axis = {self._axis})"

    def __str__(self):
        return self._name

    @property
    def axes(self):
        return self._axis

    def compute(self, *args):
        return np.zeros((self._dim, self._axis))
