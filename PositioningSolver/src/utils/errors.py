"""Common errors declarations
"""


class PositioningSolver(Exception):
    """Generic error"""

    pass


class _Unknown(PositioningSolver):
    """Generic error for unknown argument"""

    def __init__(self, name):
        self.name = name

    @property
    def type(self):
        return self.__class__.__name__[7:].lower()

    def __str__(self):
        return f"Unknown {self.type} '{self.name}'"


class DateError(PositioningSolver):
    pass


class UnknownWarning(Warning):
    pass


class ParseError(ValueError):
    pass


class UnknownConstellation(_Unknown):
    """GPS, BDS, GAL or GLO"""

    pass


class UnknownService(_Unknown):
    pass


class UnknownFrequency(_Unknown):
    """for GPS: 1, 2 or 5"""

    pass


class UnknownDatatype(_Unknown):
    """for GPS: 1, 2 or 5"""

    pass


class NotImplemented(PositioningSolver):
    pass


class FileError(PositioningSolver):
    pass


class TimeSystemWarning(Warning):
    pass


class UnknownConstellationCode(Warning):
    pass


class OrbitError(PositioningSolver):
    pass


class FrameError(PositioningSolver):
    pass


class FormError(PositioningSolver):
    pass


class ConfigError(PositioningSolver):
    pass


class UnimplementationError(PositioningSolver):
    pass


class TimeSeriesError(PositioningSolver):
    pass


class NonExistentObservable(PositioningSolver):
    pass


class PVTComputationFail(PositioningSolver):
    pass


class PreprocessorError(PositioningSolver):
    pass


class EmptyObservationData(PositioningSolver):
    pass


class UnknownConversion(PositioningSolver):
    pass
