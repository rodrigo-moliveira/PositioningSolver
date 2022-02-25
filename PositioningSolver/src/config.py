"""Configuration handler
The configuration is a simple dictionary, with possible fallbacks
"""

from .utils.errors import ConfigError


class Config(dict):
    """Config class
        inherits from dict class
    """

    _instance = None

    def get(self, *keys, fallback=None):
        """Retrieve a value in the config, if the value is not available
        give the fallback value specified.
        """

        fullkeys = list(keys).copy()

        section, *keys = keys
        out = super().get(section, fallback)

        key = ""

        while isinstance(out, dict):
            key = keys.pop(0)
            out = out.get(key, fallback)

        if keys and out is not fallback:
            raise ConfigError(
                "Dict structure mismatch : Looked for '{}', stopped at '{}'".format(
                    ".".join(fullkeys), key
                )
            )

        return out

    def set(self, *args):
        """Set a value in the config dictionary
        The last argument is the value to set

        Example
            config.set('aaa', 'bbb', True)

            # config = {'aaa': {'bbb': True}}
        """

        # split arguments in keys and value
        *first_keys, last_key, value = args

        subdict = self
        for k in first_keys:
            subdict.setdefault(k, {})
            subdict = subdict[k]

        subdict[last_key] = value

    def read_configure_json(self, filename):
        # importing the module
        import json

        # Opening JSON file
        with open(filename) as json_file:
            data = json.load(json_file)

            self.update(data)


config = Config()


def validate_config(algorithm_code):
    from ..src.algorithms import __algorithms_config_info__

    try:
        config_info = __algorithms_config_info__[algorithm_code]
    except KeyError:
        raise ConfigError(f"key '{algorithm_code}' is not a valid algorithm code. Valid ones are "
                          f"{list(__algorithms_config_info__.keys())}")

    # raise ConfigError(f"Missing parameter 'output1'")
