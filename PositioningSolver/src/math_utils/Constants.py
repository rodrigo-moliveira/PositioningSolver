
class Constant:
    # PI
    PI = 3.1415926535898
    DEG2RAD = 0.01745329251994
    RAD2DEG = 57.2957795130823

    # GPS Frequencies
    L1_FREQ = 1575.42e6
    L1_WAVELENGTH = 0.1902936727984
    L2_FREQ = 1227.60e6
    L2_WAVELENGTH = 0.2442102134246
    L5_FREQ = 1176.45e6
    L5_WAVELENGTH = 0.2548280487909

    # Time
    SECONDS_IN_DAY = 86400  # In a Julian day
    MINUTES_IN_DAY = 1440  # In a Julian day
    MINUTES_IN_HOUR = 60.0  # In a Julian day
    HOURS_IN_DAY = 24.0
    SECONDS_IN_GPS_WEEK = 604800
    DAYS_PER_WEEK = 7
    AVERAGE_DAYS_IN_YEAR = 365.25
    SECONDS_IN_HOUR = 3600

    # Orbital Mechanics constants (WGS84 values)
    # ref - [WGS84], Table 3-1
    MU = 3.986005E14  # [m^3/sec^2]
    EARTH_ROTATION = 7.292115E-5  # [rad/sec]
    SPEED_OF_LIGHT = 299792458  # [m/s]

    EARTH_FLATNESS = 1 / 298.257223563
    EARTH_ECCENTRICITY_SQ = 2 * EARTH_FLATNESS - EARTH_FLATNESS * EARTH_FLATNESS
    EARTH_SEMI_MAJOR_AXIS = 6378137.0  # [m]  Equatorial radius Re
    EARTH_J2 = 1.08262668355315130e-3  # J2 harmonic
    EARTH_MASS = 5.97237e24  # [kg]
    EARTH_G0 = 9.80665  # [m/s^2] standard value cf. https://www.convertunits.com/from/g-unit/to/m/s%5E2
