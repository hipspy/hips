# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord

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
    def create(cls, skydir: SkyCoord, shape: tuple, coordsys: str='CEL', projection: str='AIT', cdelt: float=1.0, crpix: float=1.) -> 'WCSGeometry':
        """Read from HiPS description file (`WCSGeometry`).

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
        crpix : `float`
            Pixel coordinate of reference point
        """

        naxis = 2
        if shape is not None:
            naxis += len(shape)

        w = WCS(naxis=naxis)

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
            raise ValueError('Unrecognized coordinate system.')

        try:
            w.wcs.crpix[0] = crpix[0]
            w.wcs.crpix[1] = crpix[1]
        except:
            w.wcs.crpix[0] = crpix
            w.wcs.crpix[1] = crpix
        w.wcs.cdelt[0] = -cdelt
        w.wcs.cdelt[1] = cdelt

        w = WCS(w.to_header())

        return cls(w, shape)
