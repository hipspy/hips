# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library.
"""
import numpy as np
import healpy as hp
from .wcs import WCSGeometry

__all__ = [
    'boundaries',
    'compute_healpix_pixel_indices',
]

__doctest_skip__ = ['boundaries', 'compute_healpix_pixel_indices']


def boundaries(nside: int, pix: int, nest: bool = True) -> tuple:
    """Returns an array containing the angle (theta and phi) in radians.

    This function calls `healpy.boundaries` and `healpy.pixelfunc.vec2ang`
    and computes the four corners of a HiPS tile. The order of the returned
    corners is: N, W, S, E where N (resp. W, S, E) is the corner roughly
    pointing towards the North (resp. West, South and East).

    Parameters
    ----------
    nside : int
        The nside of the HEALPix map
    pix : int
        Pixel identifier
    nest : bool, optional
        If True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    theta, phi : float, array
        Returns the angle (theta and phi) in radians

    Examples
    --------
    >>> import numpy as np
    >>> from astropy.coordinates import SkyCoord
    >>> from hips.utils import boundaries
    >>> theta, phi = boundaries(nside=8, pix=450)
    >>> SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')
    <SkyCoord (ICRS): (ra, dec) in deg
    [( 264.375, -24.62431835), ( 258.75 , -30.        ),
     ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """
    boundary_coords = hp.boundaries(nside, pix, nest=nest)
    theta, phi = hp.vec2ang(np.transpose(boundary_coords))
    return theta, phi


def compute_healpix_pixel_indices(wcs_geometry: WCSGeometry, nside: int) -> np.ndarray:
    """Compute HEALPix pixels within a minimal disk covering a given WCSGeometry.

    This function calls `healpy.pixelfunc.ang2vec` and `healpy.query_disc`
    to compute the HEALPix pixel indices, which will be used in tile drawing.

    Parameters
    ----------
    wcs_geometry : WCSGeometry
        Container for WCS object and image shape
    nside : int
        The nside of the HEALPix map

    Returns
    -------
    pixels : `numpy.ndarray`
        HEALPix pixel numbers

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> import healpy as hp
    >>> from hips.utils import WCSGeometry
    >>> from hips.utils import compute_healpix_pixel_indices
    >>> skycoord = SkyCoord(10, 20, unit="deg")
    >>> wcs_geometry = WCSGeometry.create(
    ...     skydir=skycoord, shape=(10, 20),
    ...     coordsys='CEL', projection='AIT',
    ...     cdelt=1.0, crpix=(1., 1.),
    ... )
    >>> nside = hp.order2nside(order=3)
    >>> compute_healpix_pixel_indices(wcs_geometry, nside)
    array([176, 207, 208, 239, 240, 271, 272])
    """
    center_coord = wcs_geometry.center_skycoord
    pixel_coords = wcs_geometry.pixel_skycoords
    separation = center_coord.separation(pixel_coords)
    radius = np.nanmax(separation.rad)

    vec = hp.ang2vec(center_coord.data.lon.deg, center_coord.data.lat.deg, lonlat=True)

    return hp.query_disc(nside, vec, radius)
