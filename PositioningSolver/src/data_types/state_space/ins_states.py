import numpy as np


class _StateVector(np.ndarray):
    """Coordinate representation"""

    def __new__(cls, coord, **kwargs):
        """
        Args:
            coord (list): state vector array
        """
        length = len(coord)

        obj = np.ndarray.__new__(
            cls, (length,), buffer=np.array([float(x) for x in coord]), dtype=float
        )
        obj._data = kwargs

        obj._data["state_str"] = cls.state_str

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

        self._data = obj._data.copy()

    def __reduce__(self):
        """For pickling
        see http://stackoverflow.com/questions/26598109
        """
        reconstruct, clsinfo, state = super().__reduce__()

        new_state = {
            "basestate": state,
            "inputs": self._data,
        }

        return reconstruct, clsinfo, new_state

    def __setstate__(self, state):
        """For pickling
        see http://stackoverflow.com/questions/26598109
        """
        super().__setstate__(state["basestate"])
        self._data = state["inputs"]

    def copy(self, **kwargs):
        """
        Provide a new object of the same point in space-time. Optionally,
        allow for frame and form conversion
        Return:
            _StateVector : cloned object
        """

        new_compl = {}
        for k, v in self._data.items():
            new_compl[k] = v.copy() if hasattr(v, "copy") else v

        new_obj = self.__class__(self.base, **new_compl)

        return new_obj

    def __getattr__(self, name):

        if name in self._data.keys():
            res = self._data[name]
        else:
            raise AttributeError(f"'{self.__class__}' object has no attribute {name!r}")

        return res

    def __getitem__(self, key):

        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        else:
            try:
                return self.__getattr__(key)
            except AttributeError as err:
                raise KeyError(str(err))

    def __str__(self):  # pragma: no cover
        return str(self.base)

    def __repr__(self):  # pragma: no cover
        coord_str = "\n".join(
            [
                "    %s = %s" % (name, arg)
                for name, arg in zip(self.form, self)
            ]
        )

        fmt = f"""
StateVector =
  coord = 
{coord_str}
  state = {self.state_str}
"""

        return fmt

    @property
    def to_numpy(self):
        return np.array(self)


class Velocity(_StateVector):
    form = ["x", "y", "z"]
    state_str = "velocity"


class Position(_StateVector):
    form = ["x", "y", "z"]
    state_str = "position"


class Attitude(_StateVector):
    form = ["roll", "pitch", "yaw"]
    state_str = "attitude"

