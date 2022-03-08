import numpy as np

class StochasticProcessGen:
    def __init__(self, dim):
        self._dim = dim
        self._name = "General Process"

    def __str__(self):
        return f"StochasticProcess({self._name}, dim = {self._dim})"

    def compute(self):
        return np.zeros(self._dim)
