# Licensed under a 3-clause BSD style license - see LICENSE.rst
from collections import namedtuple
from typing import Tuple
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.coordinates import Angle
from astropy.wcs.utils import pixel_to_skycoord, wcs_to_celestial_frame

__all__ = [
    'WCSGeometry',
]

__doctest_skip__ = [
    '*',
]

Shape = namedtuple('Shape', ['height', 'width'])
"""Helper for 2-dim image shape, to make it clearer what value is width and height."""


class WCSGeometry:
    """Container for WCS object and image shape.

    Parameters
    ----------
    wcs : `~astropy.wcs.WCS`
        WCS projection object
    width, height : int
        Width and height of the image in pixels

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> from hips.utils import WCSGeometry
    >>> skycoord = SkyCoord(10, 20, unit='deg')
    >>> wcs_geometry = WCSGeometry.create(
    ...     skydir=skycoord, width=20, height=10,
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
    Shape(width=20, height=10)
    """
    WCS_ORIGIN_DEFAULT = 0
    """Default WCS transform origin, to be used in all WCS pix <-> world calls."""

    def __init__(self, wcs: WCS, width: int, height: int) -> None:
        self.wcs = wcs
        self.shape = Shape(width=width, height=height)

    @property
    def center_pix(self) -> Tuple[float, float]:
        """Image center in pixel coordinates (tuple of x, y)."""
        x = float(self.shape.width - 1) / 2
        y = float(self.shape.height - 1) / 2
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
    def create(cls, skydir: SkyCoord, width: int, height: int, coordsys: str = 'icrs',
               projection: str = 'AIT', cdelt: float = 1.0, crpix: tuple = (1., 1.)) -> 'WCSGeometry':
        """Create WCS object programmatically (`WCSGeometry`).

        Parameters
        ----------
        skydir : `~astropy.coordinates.SkyCoord`
            Sky coordinate of the WCS reference point
        width, height : int
            Width and height of the image in pixels
        coordsys : {'icrs', 'galactic'}
            Coordinate system
        projection : str
            Projection of the WCS object.
            To see list of supported projections
            visit: http://docs.astropy.org/en/stable/wcs/#supported-projections
        cdelt : `float`
            Coordinate increment at reference point
        crpix : `tuple`
            Pixel coordinates of reference point
            (WCS axis order: x, y and FITS convention origin=1)
        """
        w = WCS(naxis=2)

        if coordsys == 'icrs':
            w.wcs.ctype[0] = f'RA---{projection}'
            w.wcs.ctype[1] = f'DEC--{projection}'
            w.wcs.crval[0] = skydir.icrs.ra.deg
            w.wcs.crval[1] = skydir.icrs.dec.deg
        elif coordsys == 'galactic':
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

        return cls(w, width, height)

    @classmethod
    def create_simple(cls, skydir: SkyCoord, width: int, height: int, fov: {str, Angle},
                      coordsys: str = 'icrs', projection: str = 'AIT') -> 'WCSGeometry':
        """Create WCS object programmatically using field of view (`WCSGeometry`).

        Parameters
        ----------
        skydir : `~astropy.coordinates.SkyCoord`
            Sky coordinate of the WCS reference point
        width, height : int
            Width and height of the image in pixels
        fov: `str` or Angle
            Field of view
        coordsys : {'icrs', 'galactic'}
            Coordinate system
        projection : `str`
            Projection of the WCS object.
            To see list of supported projections
            visit: http://docs.astropy.org/en/stable/wcs/#supported-projections

        Examples
        --------
        >>> from astropy.coordinates import SkyCoord
        >>> from hips.utils import WCSGeometry
        >>> skycoord = SkyCoord(10, 20, unit='deg')
        >>> wcs_geometry = WCSGeometry.create_simple(
        ...     skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
        ...     width=2000, height=1000, fov="3 deg",
        ...     coordsys='galactic', projection='AIT'
        ... )
        >>> wcs_geometry.wcs
        Number of WCS axes: 2
        CTYPE : 'GLON-AIT'  'GLAT-AIT'
        CRVAL : 0.0  0.0
        CRPIX : 500.0  1000.0
        PC1_1 PC1_2  : 1.0  0.0
        PC2_1 PC2_2  : 0.0  1.0
        CDELT : -0.0015  0.0015
        NAXIS : 0  0
        >>> wcs_geometry.shape
        Shape(width=2000, height=1000)
        """
        fov = Angle(fov)
        crpix = float(width / 2), float(height / 2)
        cdelt = float(fov.degree) / float(max(width, height))

        return cls.create(skydir, width, height, coordsys, projection, cdelt, crpix)

    @property
    def celestial_frame(self) -> str:
        """Celestial frame for the given WCS (str).

        Calls `~astropy.wcs.utils.wcs_to_celestial_frame`.
        """
        return wcs_to_celestial_frame(self.wcs)

    @property
    def fits_header(self) -> 'astropy.io.fits.Header':
        """FITS header for the given WCS (`~astropy.io.fits.Header`)."""
        return self.wcs.to_header()
