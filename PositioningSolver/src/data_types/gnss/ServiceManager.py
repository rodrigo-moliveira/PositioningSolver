from ...utils.errors import UnknownService
from ...data_types.gnss.ServicesUtils import GPSAvailableServices, GALAvailableServices
from ...data_types.gnss.Satellite import SatelliteSystem


class ServiceManager:
    """
    Class ServiceManager
    Manages the user-defined services to process in the GNSS PVT (Position Velocity Time) solution
    A service is understood as the list of frequencies and channels to be processed
    Ex: in GPS it is common to process:
        * 1C and 2P or 1C and 2W
        * 1P and 2P or 1W and 2W
        In Galileo:
            Open Service: 1C and 5Q
            Safety of Life: 1C and 7Q
            Commercial Service: 1C and 6C
            PRS: 1A and 6A

    Attributes
        ----------
        _services : dict
            The available services defined by the user. Following the RINEX convention, a service is specified by two
            parameters: constellation and frequency-attribute/tracking mode.
            For more information regarding services, please see https://files.igs.org/pub/data/format/rinex303.pdf pp.20

    Methods
        -------
        add_service(constellation, services)
            Adds a new service or list of to process for a given constellation
    """

    def __init__(self):
        self._services = {"GPS": set(),
                          "GAL": set()}

    def add_service(self, constellation: SatelliteSystem, services):
        """
        Method to add a new service to be processed in the PVT

        Args:
            constellation (SatelliteSystem):
                with the constellation to add
            services (str, list):
                services to add, either a string (single service), or a list / tuple of string services
        """

        if not isinstance(constellation, SatelliteSystem):
            raise TypeError("add_service() first argument should be of type SatelliteSystem")
        if not isinstance(services, list) and not isinstance(services, str) and not isinstance(services, tuple):
            raise TypeError("add_service() second argument should be either a list with services or a string with the "
                            "single service. Provided: {}".format(type(services)))

        availableServicesPerConst = None
        if constellation.upper() == "GPS":
            availableServicesPerConst = GPSAvailableServices
        elif constellation.upper() == "GAL":
            availableServicesPerConst = GALAvailableServices

        # if services is a string, convert to tuple
        if isinstance(services, str):
            services = tuple(services.split(","))

        # iterate over all services
        for service in services:

            # remove white spaces, if any
            service = service.replace(" ", "")

            # validate service
            if service in availableServicesPerConst:

                # append to internal tuple if not there yet
                if service not in self._services[constellation]:
                    self._services[constellation].add(service)

            else:
                # unknown service
                raise UnknownService("Unknown service{} for constellation  {}. Should be one of {}".
                                     format(service, constellation, availableServicesPerConst))

    @property
    def services(self):
        return self._services

    def items(self):
        return self.services.items()

    def getServicesForGPS(self):
        return self._services["GPS"]

    def getServicesForGAL(self):
        return self._services["GAL"]

    def has_service(self, constellation, service):
        print(self._services[constellation])
        return service in self._services[constellation]

    def __getitem__(self, key):
        return self._services[key]

    def __repr__(self):
        _repr = "----Printing available services----\n"
        for constellation, services in self._services.items():
            if len(services) != 0:
                _repr += constellation + " -> " + str(services) + "\n"
        return _repr

    def __str__(self):
        return str(self._services)

