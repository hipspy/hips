# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Classes and functions to manage HiPS tiles."""


from collections import OrderedDict

__all__ = [
    'HipsDescription',
]

class HipsDescription:
    """This class provides methods for parsing the HiPS properties file.

    It also provides multiple getters around the commonly used HiPS properties.

    Parameters
    ----------
    properties : OrderedDict
        An ordered dictionary containing the HiPS file properties
    """

    def __init__(self, properties: OrderedDict) -> None:
        self.properties = properties

    @classmethod
    def read_file(cls, filename: str) -> OrderedDict:
        """Reads text from a file and returns an ordered dictionary containing the HiPS file properties.

        This method reads a file given by the parameter and returns an ordered dictionary
        containing the HiPS file properties by calling the `parse_file_properties` method.

        Parameters
        ----------
        filename : str
            Name of the file containing HiPS file properties

        Returns
        -------
        dict_properties : OrderedDict
        """
        with open(filename) as file:
            text = file.read()
        return cls.parse_file_properties(text)

    @classmethod
    def parse_file_properties(cls, properties: str) -> OrderedDict:
        """Returns an ordered dictionary containing the HiPS file properties.

        This method parses the HiPS file properties and loads it in a dictionary,
        then is casts it to `collections.OrderedDict` type.

        Parameters
        ----------
        properties : str
            HiPS file properties

        Returns
        -------
        list_properties : OrderedDict
        """
        properties_lines = properties.split('\n')
        list_properties = []
        for property in properties_lines:
            key_value = property.split('=')
            try:
                list_properties.append((key_value[0].strip(), key_value[1].strip()))
            except IndexError: # the case where a property contains a comment or a blank line
                pass
        return cls(OrderedDict(list_properties))

    @property
    def base_url(self) -> str:
        """Returns the base url from the HiPS file properties (`str`)."""
        return self.properties['hips_service_url']

    @property
    def title(self) -> str:
        """Returns the title from the HiPS file properties (`str`)."""
        return self.properties['obs_title']

    @property
    def hips_version(self) -> float:
        """Returns the HiPS version from the HiPS file properties (`float`)."""
        return float(self.properties['hips_version'])

    @property
    def hips_frame(self) -> str:
        """Returns the HiPS frame from the HiPS file properties (`str`)."""
        return self.properties['hips_frame']

    @property
    def hips_order(self) -> int:
        """Returns the HiPS order from the HiPS file properties (`int`)."""
        return int(self.properties['hips_order'])

    @property
    def tile_format(self) -> str:
        """Returns the HiPS tile format from the HiPS file properties (`str`)."""
        return self.properties['hips_tile_format']
