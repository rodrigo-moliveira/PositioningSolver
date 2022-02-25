class Container:
    """
    Class Container
    Base class for container classes, which are useful for storing data, for example, epoch-wise data
    Data is stored in the class __dict__

    Attributes
        ----------
        __slots__ : list (defined in subclasses)
            List with the data keys to store
    """

    def __init__(self):
        pass

    def __setattr__(self, name, val):
        # Verification if the variable is available in the current form
        if name in self.__slots__:
            self.__dict__[name] = val
        else:
            raise AttributeError(f"'{self.__class__}' object has no attribute {name!r}")

    def __getattr__(self, name):
        # Verification if the variable is available in the current form
        if name in self.__slots__:
            return self.__dict__[name]
        else:
            raise AttributeError(f"'{self.__class__}' object has no attribute {name!r}")

    def __str__(self):
        # print all attributes to string format
        _allAttrs = ""
        for atr in self.__slots__:
            _allAttrs += atr + "=" + str(getattr(self, atr)) + ", "
        _allAttrs = _allAttrs[0:-2]
        return f'{type(self).__name__}({_allAttrs})'
