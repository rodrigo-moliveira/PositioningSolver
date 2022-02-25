from collections import OrderedDict
from ...utils.errors import TimeSeriesError


class TimeSeries(OrderedDict):
    """
    TimeSeries class, inherits from OrderedDict

    Stores a time series. This class inherits from OrderedDict (dict ordered by insertion order), but
    a feature to sort it by keys is introduced. This is suitable for time series, where keys represent time instants
    (epochs).

    """

    def __init__(self):
        super().__init__()
        self._epochs = []
        self._sorted = True

    # methods to set data
    def set_data(self, epoch, epoch_data):
        super().__setitem__(epoch, epoch_data)

        if epoch not in self._epochs:
            self._epochs.append(epoch)
            self._sorted = False
        # else: overwriting some epoch which was already there

    def __setitem__(self, key, value):
        self.set_data(key, value)

    # method to remove data
    def remove_data(self, epoch):

        if epoch not in self.epochs:
            raise KeyError(f"Key {epoch} not in TimeSeries")

        self.epochs.remove(epoch)
        return self.pop(epoch)

    # getters
    def get_all_epochs(self):
        self.sort()
        return self.epochs

    def get_data_for_epoch(self, epoch):
        self.sort()
        return self[epoch]

    def get_closest_epoch(self, epoch):

        self.sort()

        if len(self.epochs) == 0:
            raise TimeSeriesError(f"TimeSeries is empty.")

        if epoch < self.epochs[0]:
            raise TimeSeriesError(f"Epoch {str(epoch)} is no inside TimeSeries interval "
                                  f"{[repr(i) for i in self.epochs]}")

        # at this point, we can safely assume that vEpochs[0] <= epoch
        prev_epoch = self.epochs[0]
        for this_epoch in self.epochs:
            if this_epoch > epoch:
                return prev_epoch
            prev_epoch = this_epoch

        return prev_epoch

    @staticmethod
    def get_common_epochs(series1, series2):
        """
        Method to align the two time series to a common time interval
        returns a list with the common epochs for both series

        Parameters:
            ----------
            series1 (TimeSeries):
                time series 1

            series2 (TimeSeries):
                time series 2

        Return:
            list : A list with the common epochs
        """
        # series1.sort()
        # series2.sort()

        # print(series1.epochs[0], series1.epochs[-1])
        # print(series2.epochs[0], series2.epochs[-1])

        epochs = []
        for key in series1.epochs:
            if key in series2.epochs:
                epochs.append(key)

        return epochs

    # utility methods

    def sort(self):
        if self.sorted is False:
            self._epochs = sorted(self.epochs)
            new_dct = OrderedDict((key, self[key]) for key in self.epochs)

            self.clear()
            self.update(new_dct)

            self._sorted = True

    def __repr__(self):
        self.sort()

        myStr = "Time Series:\n"
        for epc, obs in self.items():
            myStr += "\t" + repr(epc) + " -> " + str(obs) + "\n"
        return myStr

    def copy(self):
        self.sort()
        # create new object
        _copy = TimeSeries()

        # clone data to new object
        for epoch, value in self.items():

            # try to create a clone of the value object (if possible)
            if hasattr(value, "copy"):
                _copy.set_data(epoch, value.copy())
            else:
                _copy.set_data(epoch, value)

        return _copy

    def has_epoch(self, epoch):
        if epoch in self.epochs:
            return True
        else:
            return False

    # def get_sub(self, n):
    #    tmOut = []
    #
    #    for i in range(n):
    #        tmSeries = TimeSeries()
    #        for epoch, obs in self._data.items():
    #            tmSeries.setEpochData(epoch, obs[i])
    #        tmOut.append(tmSeries)
    #
    #    return tmOut

    # properties
    @property
    def epochs(self):
        return self._epochs

    @property
    def sorted(self):
        return self._sorted

    def export2time_data(self):
        self.sort()
        return list(self.keys()), list(self.values())

    def is_empty(self):
        return len(self.get_all_epochs()) == 0


if __name__ == "__main__":
    # example
    pass
