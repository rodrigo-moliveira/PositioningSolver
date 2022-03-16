# Statevector class adapted from Beyond Package https://pypi.org/project/beyond/

import numpy as np

from ...utils.errors import OrbitError, FrameError, FormError
from .utils import Geodetic2Cartesian, Cartesian2Geodetic, ECEF2ENU, ENU2ECEF


def validate_frame(frame):
    """
    Supported frames:
        * ECEF
        * ENU
    To convert between them, an observer (the gnss receiver) is needed

    Args:
        frame (str):
            frame to verify. Should be 'ECEF' or 'ENU'

    Raises:
        FrameError : if the provided frame is not one of the above
    """
    if not (frame == "ECEF" or frame == "ENU"):
        raise FrameError(f"Provided frame {frame} should either be 'ECEF' or 'ENU' ")


def validate_form(form):
    """
    Supported forms for Position vectors:
        * cartesian
        * geodetic

    Args:
        form (str):
            form to verify. Should be one of the above

    Raise:
        FormError : if the provided frame is not verified
    """
    if not (form == "cartesian" or form == "geodetic"):
        raise FormError(f"Provided form {form} should either be 'cartesian' or 'geodetic'")


class _StateVector(np.ndarray):
    """Coordinate representation"""

    def __new__(cls, coord, frame, form, **kwargs):
        """
        Args:
            coord (list): state vector array
            form (str): Name of the form of the state vector
            frame (str): Name of the frame of reference of the state vector
        """
        length = len(cls._forms[form])
        if len(coord) != length:
            raise OrbitError(f"Should be {length} in length")

        validate_frame(frame)
        validate_form(form)

        obj = np.ndarray.__new__(
            cls, (length,), buffer=np.array([float(x) for x in coord]), dtype=float
        )
        obj._data = kwargs

        obj._data["frame"] = frame
        obj._data["form"] = form
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

    def copy(self, form=None, frame=None):
        """
        Provide a new object of the same point in space-time. Optionally,
        allow for frame and form conversion
        Args:
            form (str): Form to convert the new instance into
            frame (str): Frame to convert the new instance into
        Return:
            _StateVector : cloned object
        """

        new_compl = {}
        for k, v in self._data.items():
            new_compl[k] = v.copy() if hasattr(v, "copy") else v

        new_obj = self.__class__(self.base, **new_compl)

        if frame and frame != self.frame:
            new_obj.frame = frame

        if form and form != self.form:
            new_obj.form = form

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
                for name, arg in zip(self._forms[self.form], self)
            ]
        )

        fmt = f"""
StateVector =
  frame = {self.frame}
  form = {self.form}
  coord = 
{coord_str}
  state = {self.state_str}
"""

        return fmt

    @property
    def to_numpy(self):
        return np.array(self)


class PositionGNSS(_StateVector):
    """
    class Position, derived from _StateVector

    Can be represented either in cartesian or geodetic form, ECEF or ENU frame

    Example of usage:
        > position = Position([2333323, 2033003, 7065943], 0, "ECEF", "cartesian")
        > observer = Position([238738, -4373283, 9238322], 0, "ECEF", "cartesian")
        > position.observer = observer
        > position.frame = "ENU"
        > print(repr(position))

        > position = Position([2333323, 2033003, 7065943], 0, "ECEF", "cartesian")
        > position.form = "geodetic"
        > print(repr(position))
    """
    _forms = {"cartesian": ["x", "y", "z"],
              "geodetic": ["lat", "long", "alt"]}
    state_str = "position"

    @property
    def observer(self):
        return self._data["observer"]

    @observer.setter
    def observer(self, observer):
        self._data["observer"] = observer

    @property
    def form(self):
        return self._data["form"]

    @form.setter
    def form(self, new_form):
        # convert between forms
        old_form = self.form
        validate_form(new_form)

        if new_form == old_form:
            return

        # only transform when frame is ECEF (makes no sense to transform to geodetic if the position is in ENU coords)
        self.frame = "ECEF"

        if new_form == "cartesian" and old_form == "geodetic":
            new_coord = Geodetic2Cartesian(self[0], self[1], self[2])

        elif new_form == "geodetic" and old_form == "cartesian":
            new_coord = Cartesian2Geodetic(self[0], self[1], self[2])

        else:
            return  # when you force a form which is already selected

        self.base.setfield(new_coord, dtype=float)
        self._data["form"] = new_form

    @property
    def frame(self):
        return self._data["frame"]

    @frame.setter
    def frame(self, new_frame):

        # convert between frames
        old_frame = self.frame
        validate_frame(new_frame)

        if old_frame == new_frame:
            return

        # conversion requires cartesian form
        self.form = "cartesian"

        if "observer" not in self._data:
            raise TypeError(f"An observer must be provided in order to convert between ECEF and ENU")
        self.observer.form = "geodetic"

        if old_frame == "ECEF" and new_frame == "ENU":
            new_coord = ECEF2ENU(self[0],
                                 self[1],
                                 self[2],
                                 self.observer[0],
                                 self.observer[1],
                                 self.observer[2])

        elif old_frame == "ENU" and new_frame == "ECEF":
            new_coord = ENU2ECEF(self[0],
                                 self[1],
                                 self[2],
                                 self.observer[0],
                                 self.observer[1],
                                 self.observer[2])

        else:
            return  # when you force a frame which is already selected

        self.base.setfield(new_coord, dtype=float)
        self._data["frame"] = new_frame

