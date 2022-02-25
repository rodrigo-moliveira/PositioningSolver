from ...data_types.gnss.ServicesUtils import AvailableConstellations, ConstellationToCodeMap
from ...utils.errors import UnknownConstellation


class SatelliteSystem(str):
    """
    Class SatelliteSystem, inherits from string
    Represents a constellation system (GPS / GAL)
    This class is a sub-class of str with special utility methods
    """

    def __new__(cls, content):

        if content.upper() in AvailableConstellations:
            return super(SatelliteSystem, cls).__new__(cls, content.upper())
        else:
            raise ValueError("Unknown Satellite System {}. Possible systems are GPS or GAL".format(content.upper()))

    def __repr__(self):
        """A repr is useful for debugging"""
        return f'{type(self).__name__}({super().__repr__()})'

    def __getattribute__(self, name):
        if name in dir(str):  # only handle str methods here

            def method(self, *args, **kwargs):
                value = getattr(super(), name)(*args, **kwargs)
                # not every string method returns a str:
                if isinstance(value, str):
                    return type(self)(value)
                elif isinstance(value, list):
                    return [type(self)(i) for i in value]
                elif isinstance(value, tuple):
                    return tuple(type(self)(i) for i in value)
                else:  # dict, bool, or int
                    return value

            return method.__get__(self)  # bound method
        else:  # delegate to parent
            return super().__getattribute__(name)

    def is_GPS(self):
        return self == "GPS"

    def is_GAL(self):
        return self == "GAL"

    def get_system(self):
        return type(self)(self)

    def get_system_short(self):
        """
        Return:
            str : "G" for gps and "E" for galileo
        """
        return ConstellationToCodeMap.get(self, "UNKNOWN")


GPS = SatelliteSystem("GPS")
GAL = SatelliteSystem("GAL")
UNKNOWN = SatelliteSystem("UNKNOWN")


def SatelliteSystemFactory(system: str):
    """
    Method to return the SatelliteSystem objects.

    Args:
        system (str) : short name for the constellation
    Return:
        SatelliteSystem : the corresponding system object
    """
    if system.upper() == "GPS" or system.upper() == "G":
        return GPS
    elif system.upper() == "GAL" or system.upper() == "E":
        return GAL
    else:
        raise UnknownConstellation(
            "No Satellite System matched the descriptor {}.".format(system))
