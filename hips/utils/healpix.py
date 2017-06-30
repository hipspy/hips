# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library.
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
from typing import Tuple

from .wcs import WCSGeometry

__all__ = [
    'boundaries',
    'compute_healpix_pixel_indices',
    'frames'
]

__doctest_skip__ = ['boundaries', 'compute_healpix_pixel_indices']


def _skycoord_to_theta_phi(skycoord: SkyCoord) -> Tuple[float, float]:
    """Convert SkyCoord to theta / phi as used in healpy."""
    theta = np.pi / 2 - skycoord.data.lat.radian
    phi = skycoord.data.lon.radian
    return theta, phi


def _skycoord_to_vec(skycoord: SkyCoord) -> np.ndarray:
    """Convert SkyCoord to vec as used in healpy."""
    return hp.ang2vec(*_skycoord_to_theta_phi(skycoord))


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


def compute_healpix_pixel_indices(wcs_geometry: WCSGeometry, order: int) -> np.ndarray:
    """Compute HEALPix pixels within a minimal disk covering a given WCSGeometry.

    This function calls `healpy.pixelfunc.ang2vec` and `healpy.query_disc`
    to compute the HEALPix pixel indices, which will be used in tile drawing.

    Parameters
    ----------
    wcs_geometry : `WCSGeometry`
        Container for WCS object and image shape
    order : int
        The order of the HEALPix

    Returns
    -------
    pixels : `numpy.ndarray`
        HEALPix pixel numbers

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> from hips.utils import WCSGeometry
    >>> from hips.utils import compute_healpix_pixel_indices
    >>> skycoord = SkyCoord(10, 20, unit="deg")
    >>> wcs_geometry = WCSGeometry.create(
    ...     skydir=skycoord, shape=(10, 20),
    ...     coordsys='CEL', projection='AIT',
    ...     cdelt=1.0, crpix=(1., 1.),
    ... )
    >>> compute_healpix_pixel_indices(wcs_geometry, order=3)
    array([176, 207, 208, 239, 240, 271, 272])
    """
    center_coord = wcs_geometry.center_skycoord
    pixel_coords = wcs_geometry.pixel_skycoords
    separation = center_coord.separation(pixel_coords)
    radius = np.nanmax(separation.rad)

    vec = _skycoord_to_vec(center_coord)
    nside = hp.order2nside(order)
    return hp.query_disc(nside, vec, radius)

def frames() -> dict:
    """A dictionary mapping commonly used frames"""
    return dict({'equatorial': 'icrs', 'galactic': 'galactic', 'ecliptic': 'ecliptic'})
