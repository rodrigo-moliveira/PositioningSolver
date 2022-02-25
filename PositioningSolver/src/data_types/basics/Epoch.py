import datetime
from ...math_utils.Constants import Constant


class Epoch:
    """
    Class Epoch

    DISCLAIMER: To simplify this class, I always assume a GPS time system representation, and store the epochs in
    GPS time and format ´´tuple(gps week number, seconds in week)´´
    In the future I may need a more complex implementation -> either use datetime.datetime directly, astropy.date,
    beyond.Date, or similar...
    """

    # parser to convert between an Epoch instance and a time tag string
    TIME_TAG_PARSER = "%Y-%m-%d %H:%M:%S"

    TIME_TAG_PARSER_WITH_MICRO = "%Y-%m-%d %H:%M:%S.%f"

    # first epoch of fist GPS week time system
    GPS_REF_TIME = datetime.datetime.strptime("1980-01-06 00:00:00", TIME_TAG_PARSER)

    # immutable objects
    __slots__ = ["week", "seconds"]

    def __init__(self, date, time_system="gps", leap_seconds=0):
        """
        Initialize an Epoch object

        Parameters:
            ----------
            date (datetime.datetime, str, dict, or list/tuple):
                Data info to initialize the Epoch instance:
                    * datetime object
                    * string to parse in format '%Y-%m-%d %H:%M:%S', e.g.: '1980-01-06 00:00:00'
                    * dict with keys to construct a datetime object having keys
                            ('year', 'month', 'day', 'hour', 'minute', 'seconds')
                    * tuple or list (gps week number, seconds in week)

            time_system (str) :
                optional. Either 'gps' or 'utc'. If 'utc' time system is chosen,
                then leap_seconds must be provided

            leap_seconds (int)
                Optional. Leap seconds, must be provided if time_system = 'utc'
        """

        # check time system
        if time_system.upper() != "GPS" and time_system.upper() != "UTC":
            raise TypeError(f'unknown time system {repr(time_system)} It must be one of ("gps", "utc")')

        # check type of param date
        if isinstance(date, datetime.datetime):
            week, seconds = self._from_datetime(date, leap_seconds)

        elif isinstance(date, str):
            date = datetime.datetime.strptime(date, Epoch.TIME_TAG_PARSER)
            week, seconds = self._from_datetime(date, leap_seconds)

        elif isinstance(date, dict):
            date = datetime.datetime(year=date["year"],
                                     month=date["month"],
                                     day=date["day"],
                                     hour=date["hour"],
                                     minute=date["minute"],
                                     second=date["second"]
                                     )
            week, seconds = self._from_datetime(date, leap_seconds)

        elif isinstance(date, tuple) or isinstance(date, list) and len(date) == 2:
            week = date[0]
            seconds = date[1]

        else:
            raise TypeError(f'Unknown constructor of Epoch instance. '
                            f'See documentation')

        self.week = week
        self.seconds = seconds

    # copy() method
    def copy(self):
        """
        Clone this Epoch object

        Return:
            Epoch: cloned epoch object
        """
        other = Epoch((self.week, self.seconds))
        return other

    def fix_week(self):
        """
        This method fixes the current gps week, that is, forces self.seconds to be in the right
        interval [0, 604800], and updates self.week accordingly
        """
        if self.seconds > Constant.SECONDS_IN_GPS_WEEK:
            while self.seconds > Constant.SECONDS_IN_GPS_WEEK:
                self.seconds -= Constant.SECONDS_IN_GPS_WEEK
                self.week += 1
        elif self.seconds < 0:
            while self.seconds < 0:
                self.seconds += Constant.SECONDS_IN_GPS_WEEK
                self.week -= 1

    # Methods to export Epoch objects to other formats
    def to_time_stamp(self, leap_seconds: int = 0):
        """
        Convert Epoch instance to a time stamp string.

        Args:
            leap_seconds (int): Leap seconds to be considered
        Return:
            str: string with time stamp in format '%Y-%m-%d %H:%M:%S'
        """
        elapsed = datetime.timedelta(days=(self.week * Constant.DAYS_PER_WEEK),
                                     seconds=(self.seconds - leap_seconds))
        if elapsed.microseconds == 0:
            return datetime.datetime.strftime(Epoch.GPS_REF_TIME + elapsed, Epoch.TIME_TAG_PARSER)
        else:
            return datetime.datetime.strftime(Epoch.GPS_REF_TIME + elapsed, Epoch.TIME_TAG_PARSER_WITH_MICRO)

    def to_datetime(self, leap_seconds: int = 0):
        """
        Convert Epoch instance to a datetime object.

        Args:
            leap_seconds (int): Leap seconds to be considered
        Return:
            datetime.datetime
        """

        elapsed = datetime.timedelta(days=(self.week * Constant.DAYS_PER_WEEK),
                                     seconds=(self.seconds - leap_seconds))

        return Epoch.GPS_REF_TIME + elapsed

    def to_DOY(self):
        """
        Computes the associated day of the year

        Return:
             int: day of year
        """
        return datetime.datetime.strptime(self.to_time_stamp(), Epoch.TIME_TAG_PARSER).timetuple().tm_yday

    # Import Epoch objects from datetime objects
    @staticmethod
    def _from_datetime(date: datetime.datetime, leap_seconds: int = 0):
        """
        Returns the GPS week, the GPS day, and the seconds
        and microseconds since the beginning of the GPS week
        Used to initialize an Epoch object from a datetime object

        Args:
            date (datetime.datetime)
        leap_seconds (int), optional: Leap seconds. Use zero if not required
        Return:
             tuple: tuple with (gps_week, gps_secs) -> ('int', 'int')
        """
        t_diff = date - Epoch.GPS_REF_TIME + datetime.timedelta(seconds=leap_seconds)

        gps_week = t_diff.days // Constant.DAYS_PER_WEEK
        # gps_days = t_diff.days - 7 * gps_week
        gps_secs = t_diff.seconds + Constant.SECONDS_IN_DAY * (t_diff.days - Constant.DAYS_PER_WEEK * gps_week)

        return gps_week, gps_secs

    # Getters
    def get_week_number(self):
        return self.week

    def get_seconds_in_week(self):
        return self.seconds

    #####################
    # ! Magic Methods ! #
    #####################

    # algebraic operations
    def __add__(self, time_diff):
        """
        Operator add:
            other = self + time_diff
        """
        other = self.copy()
        if not isinstance(time_diff, float) and not isinstance(time_diff, int):
            raise TypeError(f"Epoch objects can only be added with floats or ints (time differences/deltas), "
                            f"type {type(time_diff)} was provided instead: {time_diff}")

        other.seconds += time_diff
        other.fix_week()
        return other

    def __iadd__(self, time_diff):
        """
        Operator iadd:
            self = self + time_diff
        """
        if not isinstance(time_diff, float) and not isinstance(time_diff, int):
            raise TypeError(f"Epoch objects can only be added with floats or ints (time differences/deltas), "
                            f"type {type(time_diff)} was provided instead: {time_diff}")
        self.seconds += time_diff
        self.fix_week()
        return self

    def __sub__(self, other):
        """
        subtract current epoch with other to get the time difference
            time_diff = self - other
        NOTE: time_diff is positive if self is ahead of other in time
        """
        if isinstance(other, type(self)):
            diff_weeks = int(other.week) - int(self.week)
            if diff_weeks == 0:
                return self.seconds - other.seconds
            else:
                # convert other.secs to the current gps week of self
                other_secs = other.seconds + diff_weeks * Constant.SECONDS_IN_GPS_WEEK
                return self.seconds - other_secs
        else:
            raise TypeError(f"Epoch objects can only be subtracted with other epoch objects")

    # conditional comparisons

    def __eq__(self, other) -> bool:
        """
        Method to compare two instances of class Epoch

        Args:
            other (Epoch) : instance of class Epoch to make the comparison
        Return:
            bool: True if epochs coincide, false otherwise
        """
        if isinstance(other, Epoch):
            return self.week == other.week and self.seconds == other.seconds
        else:
            raise TypeError(f'Comparison must be between two Epoch instances, but type {format(type(other))} '
                            f'was provided instead')

    def __gt__(self, other):
        """
        Operator self > other
        """

        # fix weeks for both objects
        self.fix_week()
        other.fix_week()

        if self.week > other.week:
            return True
        if self.week < other.week:
            return False
        # else, self.gps_week = other.gps_week
        return self.seconds > other.seconds

    def __ge__(self, other):
        """
        Operator self >= other
        """
        return self > other or self == other

    def __le__(self, other):
        """
        Operator self <= other
        """
        return not self > other

    def __lt__(self, other):
        """
        Operator self < other
        """
        return not self >= other

    # utility magic methods
    def __hash__(self):
        """ hash(epoch)
        Hash is obtained with tuple of (week, seconds)
        """
        return hash((self.week, self.seconds))

    def __str__(self):
        """str(Epoch)"""
        return "Epoch(week={}, seconds_in_week={})".format(self.week, self.seconds)

    def __repr__(self):
        """repr(Epoch)"""
        return "Epoch({}, {})".format(self.to_time_stamp(), "GPS")
