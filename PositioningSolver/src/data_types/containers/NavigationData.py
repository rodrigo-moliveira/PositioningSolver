from collections import OrderedDict
from ...utils.errors import TimeSeriesError
from ...data_types.basics.Epoch import Epoch
from ...data_types.gnss.Satellite import Satellite
from .TimeSeries import TimeSeries
from .Container import Container


# Note: currently only GPS navigation messages are allowed.


class NavigationHeader(Container):
    """
    NavigationHeader class, inherits from Container
    stores relevant data from the header section of a navigation file
    """
    __slots__ = ["rinex_version", "satellite_system",
                 "iono_corrections", "leap_seconds", "first_epoch"]

    def __init__(self):
        super().__init__()
        for attr in self.__slots__:
            setattr(self, attr, None)
        self.iono_corrections = {}


class NavigationPointGPS(Container):
    """
    NavigationPointGPS class, inherits from Container
    stores the data contained in a single navigation message for GPS satellites
    """
    __slots__ = ["satellite", "toc", "af0", "af1", "af2",
                 "IODE", "crs", "deltaN", "M0",
                 "cuc", "eccentricity", "cus", "sqrtA",
                 "cic", "RAAN0", "cis",
                 "i0", "crc", "omega", "RAANDot",
                 "iDot", "codesL2", "toe", "flagL2",
                 "SV_URA", "SV_health", "TGD", "IODC",
                 "TransmissionTime"]

    def __init__(self):
        super().__init__()
        for attr in self.__slots__:
            setattr(self, attr, None)

    def __str__(self):
        _allAttrs = ""
        for atr in self.__slots__:
            if atr == "satellite" or atr == "toc":
                continue
            _allAttrs += atr + "=" + str(getattr(self, atr)) + ", "
        _allAttrs = _allAttrs[0:-2]
        return f'{type(self).__name__}({_allAttrs})'


class NavigationDataMap:
    """
    NavigationDataMap
    this class stores data from rinex navigation files
    """

    def __init__(self):
        self._data = OrderedDict()
        self._header = TimeSeries()

    def __str__(self):
        myStr = "Navigation Header:\n" + str(self._header)

        myStr += "\nNavigation Data:\n"
        for sat, data in self._data.items():
            myStr += str(sat) + " ->\n"
            myStr += str(data)
            myStr += "\n"

        return myStr

    def set_data(self, epoch: Epoch, satellite: Satellite, navMessage: NavigationPointGPS):
        """
        method to set a navigation data point for a given epoch and satellite
        Args:
            epoch (Epoch)
            satellite (Satellite)
            navMessage (NavigationPointGPS)
        """

        if not isinstance(epoch, Epoch):
            raise AttributeError(f'First argument should be a valid Epoch object. Type {type(epoch)} was provided '
                                 f'instead')
        if not isinstance(satellite, Satellite):
            raise AttributeError(f'Second argument should be a valid Satellite object. Type {type(satellite)} '
                                 f'was provided instead')
        if not issubclass(type(navMessage), NavigationPointGPS):
            raise AttributeError(f'Third argument should be a valid NavigationData object. Type {type(navMessage)} '
                                 f'was provided instead')

        if satellite in self._data:
            self._data[satellite].set_data(epoch, navMessage)
        else:
            timeseries = TimeSeries()
            timeseries.set_data(epoch, navMessage)
            self._data[satellite] = timeseries

    def set_header(self, navHeader: NavigationHeader):
        """
        method to set the navigation header.
        Note: the header is valid from the first epoch to the last. Multiple files can be used to increase the cover
        Args:
            navHeader (NavigationHeader)
        """
        if not issubclass(type(navHeader), NavigationHeader):
            raise AttributeError(f'Third argument should be a valid NavigationData object. Type {type(navHeader)} '
                                 f'was provided instead')

        self._header.set_data(navHeader.first_epoch, navHeader)

    # Getters
    def get_data(self):
        return self._data

    def get_sat_data(self, sat):
        try:
            return self._data[sat]
        except KeyError:
            raise KeyError(f"Satellite {str(sat)} has no available navigation data")

    def get_sat_data_for_epoch(self, sat, epoch):
        """
        gets navigation message closest to the provided epoch

        Args:
            sat (Satellite)
            epoch (Epoch)
        Return:
            NavigationPointGPS: navigation data for the given satellite closest to the provided epoch
        Raises:
            TimeSeriesError
        """
        try:
            _epoch = self._data[sat].get_closest_epoch(epoch)
            return self._data[sat].get_data_for_epoch(_epoch)
        except TimeSeriesError as e:
            raise TimeSeriesError(f"satellite {str(sat)} has no available navigation data for epoch {repr(epoch)}, {e}")

    def get_header_data(self, epoch):
        """
        gets navigation header closest to the provided epoch

        Args:
            epoch (Epoch)
        Return:
            NavigationHeader: returns the navigation header valid for the provided epoch
        Raises:
            TimeSeriesError
        """
        try:
            _epoch = self._header.get_closest_epoch(epoch)
            return self._header.get_data_for_epoch(_epoch)
        except TimeSeriesError as e:
            raise TimeSeriesError(f"epoch {str(epoch)} has no available navigation header data , {e}")
