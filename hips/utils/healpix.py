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
    'get_hips_order_for_resolution'
]

__doctest_skip__ = ['boundaries', 'compute_healpix_pixel_indices']


def _skycoord_to_theta_phi(skycoord: SkyCoord) -> Tuple[float, float]:
    """Convert SkyCoord to theta / phi as used in healpy."""
    theta = np.pi / 2 - skycoord.data.lat.radian
    phi = skycoord.data.lon.radian
    return theta, phi


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


def compute_healpix_pixel_indices(wcs_geometry: WCSGeometry, order: int, healpix_frame: str) -> np.ndarray:
    """Compute HEALPix pixels within a minimal disk covering a given WCSGeometry.

    This function computes pixel coordinates for the given WCS object and
    then calls `healpy.pixelfunc.ang2pix` and `numpy.unique` to compute
    HEALPix pixel indices, which will be used in tile drawing.

    Parameters
    ----------
    wcs_geometry : `WCSGeometry`
        Container for WCS object and image shape
    order : int
        The order of the HEALPix
    healpix_frame : {'icrs', 'galactic', 'ecliptic'}
        Coordinate system frame in which to compute the HEALPix pixel indices

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
    >>> compute_healpix_pixel_indices(wcs_geometry, order=3, healpix_frame='galactic')
    array([321, 611, 614, 615, 617, 618, 619, 620, 621, 622])
    """
    nside = hp.order2nside(order)
    pixel_coords = wcs_geometry.pixel_skycoords.transform_to(healpix_frame)
    theta, phi = _skycoord_to_theta_phi(pixel_coords)
    ipix = hp.ang2pix(nside, theta, phi, nest=True)
    return np.unique(ipix)


def get_hips_order_for_resolution(tile_width: int, resolution: int) -> int:
    """Find the best HiPS order by looping through all possible options.

    Parameters
    ----------
    tile_width : int
        HiPS tile width
    resolution : int
        Sky image angular resolution (pixel size in degrees)

    Returns
    -------
    candidate_tile_order : int
        Best HiPS tile order
    """
    tile_order = np.log2(tile_width)
    full_sphere_area = 4 * np.pi * np.square(180 / np.pi)
    # 29 is the maximum order supported by healpy and 3 is the minimum order
    for candidate_tile_order in range(3, 29 + 1):
        tile_resolution = np.sqrt(full_sphere_area / 12 / 4 ** (candidate_tile_order + tile_order))
        # Finding the smaller tile order with a resolution equal to or better than geometric resolution
        if tile_resolution <= resolution:
            break

    return candidate_tile_order
