# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from astropy.wcs import WCS

__all__ = [
    'WCSGeometry',
]


class WCSGeometry:
    """Container for WCS object and image shape.

    Parameters
    ----------
    wcs : `~astropy.wcs.WCS`
        WCS projection object
    shape : tuple
        Shape of the image
    """

    def __init__(self, wcs: WCS, shape: tuple) -> None:
        self._wcs = wcs
        self._shape = shape

    @property
    def shape(self) -> None:
        """Shape of the image (`None`)."""
        return self._shape

    @property
    def wcs(self) -> None:
        """WCS object containing FITS image header (`None`)."""
        return self._wcs

    @classmethod
    def create(cls, projection: str='AIT', cdelt: float=1.0, crpix: float=1., shape: tuple) -> 'WCSGeometry':
        """Read from HiPS description file (`WCSGeometry`).

        Parameters
        ----------
        projection : `str`
            Project of the WCS object
        cdelt : `str`
        crpix : `str`
        shape : `tuple`
            Image shape
        """
        # TODO
        pass
