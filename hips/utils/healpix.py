# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library
"""

__all__ = [
    'boundaries', 'compute_image_pixels'
]

import healpy as hp
import numpy as np
from astropy.coordinates.angle_utilities import angular_separation
from astropy.wcs import WCS


def boundaries(nside: int, pix: int, nest: bool=True) -> tuple:
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
    ::

        >>> import numpy as np
        >>> from hips.utils import boundaries
        >>> from astropy.coordinates import SkyCoord
        >>> nside = 8
        >>> pix = 450
        >>> theta, phi = boundaries(nside, pix)
        >>> SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')
        <SkyCoord (ICRS): (ra, dec) in deg
        [( 264.375, -24.62431835), ( 258.75 , -30.        ),
         ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """

    boundary_coords = hp.boundaries(nside, pix, nest=nest)
    theta, phi = hp.vec2ang(np.transpose(boundary_coords))
    return theta, phi

def compute_image_pixels(nside: int, shape: tuple, wcs: WCS) -> np.ndarray:
    """Returns an array containing the pixels corresponding to an image.

    This function calls `healpy.pixelfunc.ang2vec`, `healpy.query_disc`, and
    `astropy.coordinates.angle_utilities.angular_separation` to compute
    the pixel values, which will be use in tile drawing.

    Parameters
    ----------
    nside : int
        The nside of the HEALPix map
    shape : tuple
        Shape of the image
    wcs : astropy.wcs.wcs.WCS
        A WCS object containing the image header

    Returns
    -------
    pixels : `numpy.ndarray`
        Returns a list of pixel values

    """

    y_center, x_center = shape[0] // 2, shape[1] // 2
    lon_center, lat_center = wcs.all_pix2world(x_center, y_center, 1)
    vec = hp.ang2vec(lon_center, lat_center, lonlat=True)
    separations = angular_separation(x_center, y_center, lon_center, lat_center)
    max_separation = np.nanmax(separations)
    return hp.query_disc(nside, vec, max_separation)
