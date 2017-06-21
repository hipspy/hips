# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from astropy.wcs import WCS
from collections import namedtuple
from astropy.coordinates import SkyCoord

__doctest_skip__ = ['WCSGeometry']

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

    Examples
    --------
    ::

        >>> from hips.utils import WCSGeometry
        >>> from astropy.coordinates import SkyCoord
        >>> skycoord = SkyCoord(10, 20, unit="deg")
        >>> wcs_geometry = WCSGeometry.create(skydir=skycoord, shape=(10, 20), \
coordsys='CEL', projection='AIT', \
cdelt=1.0, crpix=1.)
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
        (10, 20)
    """

    def __init__(self, wcs: WCS, shape: tuple) -> None:
        self.wcs = wcs
        self.Shape = namedtuple('Shape', ['ny', 'nx'])(*shape)

    @classmethod
    def create(cls, skydir: SkyCoord, shape: tuple, coordsys: str='CEL',
        projection: str='AIT', cdelt: float=1.0, crpix: tuple=(1., 1.)) -> 'WCSGeometry':
        """Create WCS object programmatically (`WCSGeometry`).

        Parameters
        ----------
        skydir : `~astropy.coordinates.SkyCoord`
            Sky coordinate of the WCS reference point
        shape : `tuple`
            Shape of the image
        coordsys : `str`
            Coordinate system
        projection : `str`
            Projection of the WCS object
        cdelt : `float`
            Coordinate increment at reference point
        crpix : `tuple`
            Pixel coordinates of reference point
        """

        w = WCS(naxis=2)

        if coordsys == 'CEL':
            w.wcs.ctype[0] = 'RA---{}'.format(projection)
            w.wcs.ctype[1] = 'DEC--{}'.format(projection)
            w.wcs.crval[0] = skydir.icrs.ra.deg
            w.wcs.crval[1] = skydir.icrs.dec.deg
        elif coordsys == 'GAL':
            w.wcs.ctype[0] = 'GLON-{}'.format(projection)
            w.wcs.ctype[1] = 'GLAT-{}'.format(projection)
            w.wcs.crval[0] = skydir.galactic.l.deg
            w.wcs.crval[1] = skydir.galactic.b.deg
        else:
            raise ValueError('Unrecognized coordinate system.') # pragma: no cover

        w.wcs.crpix[0] = crpix[0]
        w.wcs.crpix[1] = crpix[1]

        w.wcs.cdelt[0] = -cdelt
        w.wcs.cdelt[1] = cdelt

        w = WCS(w.to_header())

        return cls(w, shape)
