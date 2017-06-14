# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Classes and functions to manage HiPS tiles."""


from .description import HipsDescription
import numpy as np

__all__ = [
    'Hips',
]


class Hips:
    """HiPS base url container.

    """

    def __init__(self) -> None:
        pass

    @property
    def base_url(self) -> str:
        """HiPS base url (`str`)."""
        return self.base_url

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        """Set the HiPS base url (`None`)."""
        self.base_url = base_url

    def get_tile_url(self, order: int, ipix: int, format: str) -> str:
        """HiPS tile url (`str`)."""
        directory = np.around(ipix, decimals=-(len(str(ipix)) - 1))
        return ''.join([self.base_url, '/Norder', str(order), '/Dir', str(directory), '/Npix', str(ipix), '.', format])
