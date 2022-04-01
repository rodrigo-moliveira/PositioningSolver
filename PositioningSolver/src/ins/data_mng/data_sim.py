from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit


class SimulatedData:
    """
    Simulated data
    """
    def __init__(self, name, description, units=None, output_units=None, legend=None):
        """
        Set up data properties (input/output data). All data are stored in a TimeSeries, numpy array, scalar: self.data.
        * In case of numpy array, it is of shape (m,n)
            m is the time dimension
            n is the length of the vector for each epoch (may be scalar, tri-dimensional, etc.)
        * In case of TimeSeries see PositioningSolver.src.data_types.containers.TimeSeries.TimeSeries
        * In case of scalar, it is just a constant scalar (no timeseries associated)

        Args:
            name: string name of the data
            description: string description of the data
            units: a tuple or list of strings to specify units of data that is going to be used in internal computations
                The length of units must be consisted with the provided data in self.data
            output_units: a tuple or list of strings to specify units of data when being plotted or saved to file
                If this is set to None, output_units will be the same as units, and no unit conversion is needed.
            legend: tuple or list of strings to specify legend of data
                To be stored in the first line of output csv files
                The length of units is the same as columns of each set of data in self.data.
        """
        self.name = name
        self.description = description
        # units of self.data
        if units is None:
            self.units = ['']
        else:
            self.units = list(units)
        # output units should have same length as units
        if output_units is None:
            self.output_units = self.units
        else:
            self.output_units = list(output_units)
            len_in = len(self.units)
            len_out = len(self.output_units)
            if len_in != len_out:
                raise ValueError(f"units {units} and output units {output_units} should have the same dimension")

        if len(legend) != len(units):
            raise ValueError(f"legend {legend} and units {units} should have the same dimension")
        self.legend = legend

        self.data = None

    def add_data(self, data, units=None):
        """
        Add data to SimulatedData.
        Args:
            data: a scalar, a numpy array or TimeSeries of the above two.
            units: Units of the input data. If you know clearly no units convertion is needed, set
                units to None. If you do not know what units are used in the class InsDataMgr,
                you'd better provide the units of the data. Units convertion will be done
                automatically here.
                If data is a scalar, units should be a list of one string to define its unit.
                If data is a numpy of size(m,n), units should be a list of n strings
                to define the units.
                If data is a dict, units should be the same as the above two depending on if
                each value in the dict is a scalr or a numpy array.
        """
        if units is not None:
            units = list(units)
            if len(units) == len(self.units):
                if units != self.units:
                    # data units are different from units in the manager, need to be converted
                    # TODO: log message...
                    data = convert_unit(data, units, self.units)
            else:
                raise ValueError(f'Units {units} and {self.units} are of different lengths. Error')

        self.data = data
