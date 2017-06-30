# Licensed under a 3-clause BSD style license - see LICENSE.rst
from collections import namedtuple
from typing import Tuple
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.wcs.utils import pixel_to_skycoord

__all__ = [
    'WCSGeometry',
]

__doctest_skip__ = ['WCSGeometry']

Shape = namedtuple('Shape', ['ny', 'nx'])
"""Helper for 2-dim image shape, to make it clearer what value is x and y."""


class WCSGeometry:
    """Container for WCS object and image shape.

    Parameters
    ----------
    wcs : `~astropy.wcs.WCS`
        WCS projection object
    shape : tuple
        Shape of the image

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> from hips.utils import WCSGeometry
    >>> skycoord = SkyCoord(10, 20, unit='deg')
    >>> wcs_geometry = WCSGeometry.create(
    ...     skydir=skycoord, shape=(10, 20),
    ...     coordsys='CEL', projection='AIT',
    ...     cdelt=1.0, crpix=(1., 1.),
    ... )
    >>> wcs_geometry.wcs
    Number of WCS axes: 2
    CTYPE : 'RA---AIT'  'DEC--AIT'
    CRVAL : 10.0  20.0
    CRPIX : 1.0  1.0
    PC1_1 PC1_2  : 1.0  0.0
    PC2_1 PC2_2  : 0.0  1.0
    CDELT : -1.0  1.0
    NAXIS : 0  0
    >>> wcs_geometry.shape
    Shape(ny=10, nx=20)
    """
    WCS_ORIGIN_DEFAULT = 0
    """Default WCS transform origin, to be used in all WCS pix <-> world calls."""

    def __init__(self, wcs: WCS, shape: tuple) -> None:
        self.wcs = wcs
        self.shape = Shape(*shape)

    @property
    def center_pix(self) -> Tuple[float, float]:
        """Image center in pixel coordinates (tuple of x, y)."""
        x = float(self.shape.nx - 1) / 2
        y = float(self.shape.ny - 1) / 2
        return x, y

    @property
    def pixel_skycoords(self) -> SkyCoord:
        """Grid of sky coordinates of the image pixels (`~astropy.coordinates.SkyCoord`)."""
        y, x = np.indices(self.shape)
        return self.pix_to_sky(x, y)

    @property
    def center_skycoord(self) -> SkyCoord:
        """Image center in sky coordinates (`~astropy.coordinates.SkyCoord`)."""
        return self.pix_to_sky(*self.center_pix)

    def pix_to_sky(self, x, y) -> SkyCoord:
        """Helper function to convert pix to sky coordinates."""
        return pixel_to_skycoord(x, y, self.wcs, self.WCS_ORIGIN_DEFAULT)

    @classmethod
    def create(cls, skydir: SkyCoord, shape: tuple, coordsys: str = 'CEL',
               projection: str = 'AIT', cdelt: float = 1.0, crpix: tuple = (1., 1.)) -> 'WCSGeometry':
        """Create WCS object programmatically (`WCSGeometry`).

        Parameters
        ----------
        skydir : `~astropy.coordinates.SkyCoord`
            Sky coordinate of the WCS reference point
        shape : `tuple`
            Shape of the image (Numpy axis order: y, x)
        coordsys : `str`
            Coordinate system
        projection : `str`
            Projection of the WCS object
        cdelt : `float`
            Coordinate increment at reference point
        crpix : `tuple`
            Pixel coordinates of reference point
            (WCS axis order: x, y and FITS convention origin=1)
        """

        w = WCS(naxis=2)

        if coordsys == 'CEL':
            w.wcs.ctype[0] = f'RA---{projection}'
            w.wcs.ctype[1] = f'DEC--{projection}'
            w.wcs.crval[0] = skydir.icrs.ra.deg
            w.wcs.crval[1] = skydir.icrs.dec.deg
        elif coordsys == 'GAL':
            w.wcs.ctype[0] = f'GLON-{projection}'
            w.wcs.ctype[1] = f'GLAT-{projection}'
            w.wcs.crval[0] = skydir.galactic.l.deg
            w.wcs.crval[1] = skydir.galactic.b.deg
        else:
            raise ValueError('Unrecognized coordinate system.')  # pragma: no cover

        w.wcs.crpix[0] = crpix[0]
        w.wcs.crpix[1] = crpix[1]

        w.wcs.cdelt[0] = -cdelt
        w.wcs.cdelt[1] = cdelt

        w = WCS(w.to_header())

        return cls(w, shape)
