from typing import Any


class Searchable:

    def get(self, key, value) -> Any:
        """
        Gets a value from the configuration.

        :param key: key to get from the config.
        :param value: default value to return if the key is not present or no value is available.
        :return: the value corresponding
        """
        return self.__dict__.get(key, value)

    def extract(self, key: str, value: Any = None, default: Any = None):
        """
        Multi-level value getter, the first value found (e.g. not None) in the given list will be returned:
        1. provided value in the arguments.
        2. this class's dictionary key.
        3. default value.

        :param key: key to get from the grid configuration's dictionary
        :param value: current value to be returned with priority
        :param default: default value to be returned if all else fails
        :return: the first value which is not None, default value otherwise.
        """
        nvalue = value
        if not value:
            nvalue = self.get(key, value)
        if not nvalue:
            nvalue = default
        return nvalue
