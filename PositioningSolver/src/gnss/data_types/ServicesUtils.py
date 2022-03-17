from PositioningSolver.src.data_types.basics.DataType import DataTypeFactory

"""
Utility maps and dicts to deal with the constellations and services.
-> Available constellations: Galileo and GPS
"""

AvailableConstellations = {"GPS", "GAL", "UNKNOWN"}

# Rinex format
GPSAvailableServices = {'1C', '1S', '1L', '1X', '1P', '1W', '1Y', '1M',
                        '2C', '2D', '2S', '2L', '2X', '2P', '2W', '2Y', '2M',
                        '5I', '5Q', '5X'}
GALAvailableServices = {'1A', '1B', '1C', '1X', '1Z',
                        '5I', '5Q', '5X',
                        '7I', '7Q', '7X',
                        '8I', '8Q', '8X',
                        '6A', '6B', '6C', '6X', '6Z'}

ConstellationToCodeMap = {"GPS": "G", "GAL": "E", "UNKNOWN": "U"}


CodeToConstellationMap = {"G": "GPS",
                          "E": "GAL"}


def get_code_type_from_service(services, constellation):
    datatypes = []

    if constellation == "GPS":
        for service in services:
            if service in GPSAvailableServices:
                datatypes.append(DataTypeFactory("C" + service[0]))

    elif constellation == "GAL":
        for service in services:
            if service in GALAvailableServices:
                datatypes.append(DataTypeFactory("C" + service[0]))

    return datatypes


def get_carrier_type_from_service(services, constellation):
    datatypes = []

    if constellation == "GPS":
        for service in services:
            if service in GPSAvailableServices:
                datatypes.append(DataTypeFactory("L" + service[0]))

    elif constellation == "GAL":
        for service in services:
            if service in GALAvailableServices:
                datatypes.append(DataTypeFactory("L" + service[0]))

    return datatypes
