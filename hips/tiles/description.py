# Licensed under a 3-clause BSD style license - see LICENSE.rst
from collections import OrderedDict

__all__ = [
    'HipsDescription',
]


class HipsDescription:
    """HiPS properties container.

    Parameters
    ----------
    properties : `~collections.OrderedDict`
        HiPS description properties
    """

    def __init__(self, properties: OrderedDict) -> None:
        self.properties = properties

    @classmethod
    def read(cls, filename: str) -> 'HipsDescription':
        """Read from HiPS description file (`HipsDescription`).

        Parameters
        ----------
        filename : str
            HiPS properties filename
        """
        with open(filename) as fh:
            text = fh.read()

        return cls.parse(text)

    @classmethod
    def parse(cls, text: str) -> 'HipsDescription':
        """Parse HiPS description text (`HipsDescription`).

        Parameters
        ----------
        text : str
            HiPS properties text
        """
        properties = OrderedDict()
        for line in text.split('\n'):
            # Skip empty or comment lines
            if line == '' or line.startswith('#'):
                continue

            try:
                key, value = [_.strip() for _ in line.split('=')]
                properties[key] = value
            except ValueError:
                # Skip bad lines (silently, might not be a good idea to do this)
                continue

        return cls(properties)

    @property
    def base_url(self) -> str:
        """HiPS service base URL (`str`)."""
        return self.properties['hips_service_url']

    @property
    def title(self) -> str:
        """HiPS title (`str`)."""
        return self.properties['obs_title']

    @property
    def hips_version(self) -> str:
        """HiPS version (`str`)."""
        return self.properties['hips_version']

    @property
    def hips_frame(self) -> str:
        """HiPS coordinate frame (`str`)."""
        return self.properties['hips_frame']

    @property
    def hips_order(self) -> int:
        """HiPS order (`int`)."""
        return int(self.properties['hips_order'])

    @property
    def tile_format(self) -> str:
        """HiPS tile format (`str`)."""
        return self.properties['hips_tile_format']
