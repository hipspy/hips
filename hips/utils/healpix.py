# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library.
"""
from typing import Tuple
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
from .wcs import WCSGeometry

__all__ = [
    'healpix_skycoord_to_theta_phi',
    'healpix_theta_phi_to_skycoord',
    'healpix_pixel_corners',
    'healpix_pixels_in_sky_image',
    'get_hips_order_for_resolution',
]

__doctest_skip__ = [
    'healpix_pixel_corners',
]

HIPS_HEALPIX_NEST = True
"""HiPS always uses the nested HEALPix pixel numbering scheme."""


def healpix_skycoord_to_theta_phi(skycoord: SkyCoord) -> Tuple[float, float]:
    """Convert SkyCoord to theta / phi as used in healpy."""
    theta = np.pi / 2 - skycoord.data.lat.radian
    phi = skycoord.data.lon.radian
    return theta, phi


def healpix_theta_phi_to_skycoord(theta: float, phi: float, frame: str) -> SkyCoord:
    """Convert theta/phi as used in healpy to SkyCoord."""
    return SkyCoord(phi, np.pi / 2 - theta, unit='radian', frame=frame)


def healpix_pixel_corners(order: int, ipix: int, frame: str) -> SkyCoord:
    """Returns an array containing the angle (theta and phi) in radians.

    This function calls `healpy.boundaries` to compute the four corners of a HiPS tile.

    It's not documented, but apparently the order of the corners is always as follows:

    1. North (N)
    2. West (W)
    3. South (S)
    4. East (E)

    Parameters
    ----------
    order : int
        HEALPix ``order`` parameter
    ipix : int
        HEALPix pixel index
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame

    Returns
    -------
    corners : `~astropy.coordinates.SkyCoord`
        Sky coordinates (array of length 4).

    Examples
    --------
    >>> import numpy as np
    >>> from astropy.coordinates import SkyCoord
    >>> from hips.utils import healpix_pixel_corners
    >>> theta, phi = healpix_pixel_corners(nside=8, pix=450)
    >>> SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')
    <SkyCoord (ICRS): (ra, dec) in deg
    [( 264.375, -24.62431835), ( 258.75 , -30.        ),
     ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """
    nside = hp.order2nside(order)
    boundary_coords = hp.boundaries(nside, ipix, nest=HIPS_HEALPIX_NEST)
    theta, phi = hp.vec2ang(np.transpose(boundary_coords))
    return healpix_theta_phi_to_skycoord(theta, phi, frame)


def healpix_pixels_in_sky_image(wcs_geometry: WCSGeometry, order: int, healpix_frame: str) -> np.ndarray:
    """Compute HEALPix pixels within a given sky image.

    The algorithm used is as follows:

    * compute the sky position of every pixel in the image using the given ``geometry``
    * compute the HEALPix pixel index for every pixel using `healpy.pixelfunc.ang2pix`
    * compute the unique set of HEALPix pixel values that occur via `numpy.unique`

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
    >>> from hips.utils import healpix_pixels_in_sky_image
    >>> skycoord = SkyCoord(10, 20, unit="deg")
    >>> wcs_geometry = WCSGeometry.create(
    ...     skydir=skycoord, shape=(10, 20),
    ...     coordsys='CEL', projection='AIT',
    ...     cdelt=1.0, crpix=(1., 1.),
    ... )
    >>> healpix_pixels_in_sky_image(wcs_geometry, order=3, healpix_frame='galactic')
    array([321, 611, 614, 615, 617, 618, 619, 620, 621, 622])
    """
    nside = hp.order2nside(order)
    pixel_coords = wcs_geometry.pixel_skycoords.transform_to(healpix_frame)
    theta, phi = healpix_skycoord_to_theta_phi(pixel_coords)
    ipix = hp.ang2pix(nside, theta, phi, nest=HIPS_HEALPIX_NEST)
    return np.unique(ipix)


def get_hips_order_for_resolution(tile_width: int, resolution: float) -> int:
    """Find the best HiPS order by looping through all possible options.

    Parameters
    ----------
    tile_width : int
        HiPS tile width
    resolution : float
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
