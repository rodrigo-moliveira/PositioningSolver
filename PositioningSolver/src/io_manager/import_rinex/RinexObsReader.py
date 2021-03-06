from math import floor

from ...data_types.basics.Epoch import Epoch
from ...data_types.gnss.Satellite import SatelliteFactory
from ...data_types.basics.DataType import DataTypeFactory
from ...data_types.containers.ObservationData import ObservationData, Header, ObservationHeader
from ...data_types.gnss.ServiceManager import ServiceManager

from .RinexUtils import RinexUtils
from ...utils.errors import ConfigError

"""
Example of File Rinex Observation File V3.03 (header + data):

     3.03           OBSERVATION DATA    M                   RINEX VERSION / TYPE
BNC 2.12.7          rtproc              20190114 061443 UTC PGM / RUN BY / DATE
PORTIONS OF THIS HEADER GENERATED BY BKG AT 13-Jan-19 22:51 COMMENT
FROM SITELOG brux_20181112.log                              COMMENT
OBS TYPES from mgex.igs-ip.net/BRUX7                        COMMENT
RTCM_3 mgex.igs-ip.net/BRUX7                                COMMENT
BRUX                                                        MARKER NAME
13101M010                                                   MARKER NUMBER
                                                            MARKER TYPE
                    ROB                                     OBSERVER / AGENCY
3001376             SEPT POLARX4TR      2.9.6-extref3       REC # / TYPE / VERS
00464               JAVRINGANT_DM   NONE                    ANT # / TYPE
  4027881.6280   306998.5370  4919498.9840                  APPROX POSITION XYZ
        0.4689        0.0000        0.0010                  ANTENNA: DELTA H/E/N
C    8 C2I L2I D2I S2I C7I L7I D7I S7I                      SYS / # / OBS TYPES
  2019     1    14     6    15    0.0000000     GPS         TIME OF FIRST OBS
C L2I  0.00000                                              SYS / PHASE SHIFT
                                                            GLONASS COD/PHS/BIS
  0                                                         GLONASS SLOT / FRQ #
                                                            END OF HEADER
> 2019 01 14 06 15  0.0000000  0 38
G01  21169746.382   111247790.951       -2243.909          50.312    21169747.722    86686606.781       -1748.496       
G03  20117572.110   105718568.842         -56.216          52.562    20117572.459    82378113.879         -43.804       
G06  24672708.738   129655962.943        3502.867          34.812    24672709.605   101030618.321        2729.501       
G09  24340277.158   127909023.750        3857.075          37.188    24340277.445    99669361.012        3005.518       
G11  22588136.367   118701482.987       -3606.968          43.000    22588134.063    92494648.097       -2810.626       

"""


class RinexObsReader:
    """
    Class RinexObsReader

    Attributes
        ----------
        file (str) : f
        service_manager : ServiceManager
        cObsData : ObservationData
        header : ObservationHeader (composed of attributes rinex_version, satellite_system, time_system,
                                    receiver_position, leap_seconds, first_epoch, last_epoch)
        log : logging
        first_arc_epoch : initial arc epoch to read
        last_arc_epoch : final arc epoch to read

    """

    def __init__(self, file, services: ServiceManager, cObsData: ObservationData, obs_header: ObservationHeader, log,
                 first_arc_epoch=None, last_arc_epoch=None, snr_control_check=0):
        if not isinstance(services, ServiceManager):
            raise AttributeError(f'argument ??services?? should be of type ServiceManager')
        if not isinstance(cObsData, ObservationData):
            raise AttributeError(f'argument ??cObsData?? should be of type ObservationData')

        # instance variables
        self.file = file
        self.service_manager = services
        self._map = {}
        self.cObsData = cObsData
        self.header = Header()
        self.log = log
        self.snr_control_check = snr_control_check

        # first and final arc epochs to read, if not None
        self.first_arc_epoch = first_arc_epoch
        self.last_arc_epoch = last_arc_epoch

        cFile = open(self.file, "r")

        # read header
        self._read_header(cFile)
        obs_header.set_header(self.header)

        self._validate_requested_observations()

        # read inputs
        self._read_obs(cFile)

        cFile.close()

    def _read_header(self, cFile):
        """
        Method to read header data and store it in container self.header (@ObservationHeader)

        Tags to look for:
            * RINEX VERSION / TYPE  -> rinex_version and satellite_system
            * APPROX POSITION XYZ   -> receiver_position
            * LEAP SECONDS          -> leap_seconds
            * TIME OF FIRST OBS     -> first_epoch
            * TIME OF LAST OBS      -> last_epoch
            * SYS / # / OBS TYPES   -> fill attribute self._map (map between data types and columns in file)
            * END OF HEADER         -> end of header section
        """
        line = " "

        while line:
            line = cFile.readline()
            # print(line)

            if "RINEX VERSION / TYPE" in line:
                self.header.rinex_version = float(line[5:10])
                if self.header.rinex_version < 3:
                    from src.utils.errors import FileError
                    raise FileError("The provided rinex file {} is of version {}. Only version 3.00 or "
                                    "higher is supported. Error!".format(self.file, self.header.rinex_version))

                rinexType = line[20]
                if rinexType != 'O':
                    from src.utils.errors import FileError
                    raise FileError("Rinex File {} should be a GNSS Observation Data File. Instead, "
                                    "a {} was provided (code {})".format(self.file,
                                                                         RinexUtils.RINEX_FILE_TYPES.get
                                                                         (rinexType, "Unknown Data File"), rinexType))

                self.header.satellite_system = line[40]

            elif "APPROX POSITION XYZ" in line:
                data = line[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER]
                # static antenna position in ECEF frame (static receiver)
                self.header.receiver_position = tuple(map(float, data.split()))

            elif "LEAP SECONDS" in line:
                data = line[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER].split()
                self.header.leap_seconds = int(data[0])

            elif "TIME OF FIRST OBS" in line:
                data = line[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER]
                self._set_time_system(data[48:51].upper())

                data = data.split()
                time_dict = {"year": int(data[0]),
                             "month": int(data[1]),
                             "day": int(data[2]),
                             "hour": int(data[3]),
                             "minute": int(data[4]),
                             "second": floor(float(data[5]))}

                self.header.first_epoch = Epoch(time_dict, time_system=self.header.time_system)

            elif "TIME OF LAST OBS" in line:
                data = line[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER].split()
                time_dict = {"year": int(data[0]),
                             "month": int(data[1]),
                             "day": int(data[2]),
                             "hour": int(data[3]),
                             "minute": int(data[4]),
                             "second": floor(float(data[5]))}

                self.header.last_epoch = Epoch(time_dict, time_system=self.header.time_system)

            elif "SYS / # / OBS TYPES" in line:
                data = line[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER].split()
                constellationCode = line[0]
                nmbOfObs = int(data[1])

                if nmbOfObs > len(data[2:]):
                    line2 = cFile.readline()[:RinexUtils.RINEX_OBS_END_OF_DATA_HEADER].split()
                    data += line2

                # iterate over all constellations
                for constellation, services in self.service_manager.items():
                    if RinexUtils.RINEX_SATELLITE_SYSTEM.get(constellationCode, "") == constellation:
                        _map = {}

                        # iterate over all available observation codes for this constellation
                        for this_obsCode in data[2:]:
                            if len(this_obsCode) == 3:
                                this_service = this_obsCode[1:]
                                if this_service in services:
                                    this_DTtype = this_obsCode[0]
                                    if this_DTtype in RinexUtils.RINEX_OBS_TYPES_TO_READ:
                                        _map[this_obsCode] = data[2:].index(this_obsCode)
                        self._map[constellation] = _map

            elif "END OF HEADER" in line:
                break

    def _validate_requested_observations(self):
        for constellation, services in self.service_manager.items():
            if constellation in self._map:
                services_read = [x[1:] for x in self._map[constellation]]
                services_read = list(dict.fromkeys(services_read))

                for service in services:
                    if service not in services_read:
                        raise ConfigError(f"User-selected service '{service}' does not exist in provided Observation File")

    def _set_time_system(self, time_system: str):

        # set default time system (according to the provided satellite system)
        if not time_system or time_system.isspace():
            self.header.time_system = RinexUtils.RINEX_SATELLITE_SYSTEM.get(self.header.satellite_system, "GPS")
        else:
            self.header.time_system = time_system

        # NOTE: currently, this software only interprets GPS time system!!!
        if self.header.time_system != "GPS":
            self.log.warn("Time system `{}?? will be interpreted internally as GPS"
                          .format(self.header.time_system))
            self.header.time_system = "GPS"

    def _read_obs(self, cFile):
        """
        Read observation data

        Each observation is stored in a fixed field of 14 characters and
        with three trailing digits after the decimal point. Carrier phase
        and pseudorange observations are furthermore complemented by an
        optional loss-of-lock indicator (0, blank, or 1) and/or a
        single-digit signal-strength indicator in the two cells adjacent
        to the actual measurement value. Although the RINEX format supports
        the loss-of lock indicator for each observation type, it is common
        practice to only indicate it on the phase observations. Likewise,
        the single-digit signal-strength field is often omitted if the
        signal strength (in dB-Hz) is explicitly provided as an observation
        type.

        Epoch (example):
            > 2019 01 14 06 15  0.0000000  0 38
        if the epoch flag is different from zero, this epoch is ignored

        Data line:
        G01  21169746.382   111247790.951       -2243.909          50.312    21169747.722    86686606.781       -1748.49

        NOTE: if signal strength bit is < 5, then the observation is discarded
        """

        line = " "
        this_epoch = None
        ignoring = False

        while line:
            line = cFile.readline()

            if not line.strip():
                # look for empty lines
                break

            if line[0] == ">":
                # Reading new epoch
                ignoring = False
                data = line[1:].split()
                time_dict = {"year": int(data[0]),
                             "month": int(data[1]),
                             "day": int(data[2]),
                             "hour": int(data[3]),
                             "minute": int(data[4]),
                             "second": floor(float(data[5]))}
                epochFlag = int(data[6])
                # nmbOfSats = data[7]

                if epochFlag != 0:
                    ignoring = True
                    self.log.debug(f"Discarding all data for {this_epoch.to_time_stamp()} due to bad epoch flag")
                    continue

                this_epoch = Epoch(time_dict, time_system=self.header.time_system)

                # check initial and final arc intervals
                if self.first_arc_epoch:
                    if self.first_arc_epoch > this_epoch:
                        ignoring = True
                        continue
                if self.last_arc_epoch:
                    if this_epoch > self.last_arc_epoch:
                        ignoring = True
                        continue

            else:
                if ignoring:
                    continue
                # Reading observations
                # Each observation word is 16 characters: 14 (observation) + 1 (loss-of-lock indicator) + 1
                # (signal strength).
                # the last two are optional -> may be blank. Here they will be discarded.
                constellation_code = line[0]

                constellation = RinexUtils.RINEX_SATELLITE_SYSTEM[constellation_code]
                if constellation in self._map:

                    # get satellite
                    this_sat = SatelliteFactory(line[0:3])
                    this_map = self._map[constellation]

                    # get available observations in the current line of the file
                    obs_str = line[3:]
                    observations = [obs_str[i:i + 16] for i in range(0, len(obs_str), 16)]
                    for this_obsCode, this_index in this_map.items():
                        this_type = DataTypeFactory(this_obsCode[0:2])

                        # get observable
                        try:
                            this_str = observations[this_index]
                            if this_str.isspace():
                                continue

                            observable = float(this_str[0:-2])
                            signal_strength = this_str[-1]

                            try:
                                signal_strength = int(signal_strength)
                                if signal_strength < self.snr_control_check:
                                    self.log.debug(f"Discarding observable {this_type} at {this_epoch.to_time_stamp()} "
                                                   f"for {this_sat} due to low signal strength: {signal_strength} < "
                                                   f"{self.snr_control_check}")
                                    continue
                            except ValueError:
                                pass

                            # set observable
                            self.cObsData.set_observable(this_epoch, this_sat, this_type, observable)
                            # print("Setting observable", this_epoch.to_time_stamp(), this_sat, this_type, observable)

                        except (ValueError, IndexError) as e:
                            self.log.debug("problem parsing line {} for index {}: {}".format(line, this_index, e))

