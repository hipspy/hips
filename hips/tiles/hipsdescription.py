# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS description class -- provides methods for parsing the HiPS file properties."""

__all__ = [
    'HipsDescription',
]

from collections import OrderedDict


class HipsDescription:
    """This class provides method for parsing the HiPS properties file.
       It also provides various getters around the commonly used properties.
    """

    def __init__(self, properties: str) -> None:
        super(HipsDescription, self).__init__()
        self.properties = self.parse_file_properties(properties)

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
        dict_properties : OrderedDict
        """
        properties = properties.split('\n')
        dict_properties = {}
        for property in properties:
            key_value = property.split('=')
            try:
                dict_properties[key_value[0].strip()] = key_value[1].strip()
            except:
                pass
        return OrderedDict(dict_properties)

    def get_properties(self) -> OrderedDict:
        """OrderedDict: Returns the ordered dictionary containing the HiPS properties."""
        return self.properties

    def get_base_url(self) -> [str, None]:
        """str: Returns the base url from the HiPS file properties."""
        try:
            return self.properties['hips_service_url']
        except:
            return None

    def get_title(self) -> str:
        """str: Returns the title from the HiPS file properties."""
        return self.properties['obs_title']

    def get_hips_version(self) -> float:
        """float: Returns the HiPS version from the HiPS file properties."""
        return float(self.properties['hips_version'])

    def get_hips_frame(self) -> str:
        """str: Returns the HiPS frame from the HiPS file properties."""
        return self.properties['hips_frame']

    def get_hips_order(self) -> int:
        """int: Returns the HiPS order from the HiPS file properties."""
        return int(self.properties['hips_order'])

    def get_tile_format(self) -> str:
        """str: Returns the HiPS tile format from the HiPS file properties."""
        return self.properties['hips_tile_format']