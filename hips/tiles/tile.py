# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .description import HipsDescription
import numpy as np

__all__ = [
    'HipsTile',
]


class HipsTile:
    """HiPS tile container.

    """

    def __init__(self, hips_description: HipsDescription, order: int, ipix: int, format: str) -> None:
        self.hips_description = hips_description
        self.order = order
        self.ipix = ipix
        self.format = format

    @property
    def base_url(self) -> str:
        """HiPS tile base url (`str`)."""
        return self.base_url

    @property
    def data(self) -> list:
        """HiPS tile data (`list`)."""
        return self.data

    @property
    def tile_url(self) -> str:
        """HiPS tile url (`str`)."""
        directory = np.around(self.ipix, decimals=-(len(str(self.ipix)) - 1))
        return ''.join([self.base_url, '/Norder', str(self.order), '/Dir', str(directory), '/Npix', str(self.ipix), '.', self.format])

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        """Set the HiPS tile base url (`None`)."""
        self._base_url = base_url

    @data.setter
    def data(self, data: list) -> None:
        """Set the HiPS tile data (`None`)."""
        self.data = data
