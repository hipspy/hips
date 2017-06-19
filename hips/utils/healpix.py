# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library
"""

__all__ = [
    'boundaries', 'compute_healpix_pixel_indices'
]

import healpy as hp
import numpy as np
from .wcs import WCSGeometry
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

def compute_healpix_pixel_indices(wcs_geometry: WCSGeometry, nside: int) -> np.ndarray:
    """Returns an array containing HEALPix pixels corresponding to disk regions.

    This function calls `healpy.pixelfunc.ang2vec`, `healpy.query_disc`, and
    `astropy.coordinates.angle_utilities.angular_separation` to compute
    the HEALPix pixel indices, which will be used in tile drawing.

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
    ::

        >>> import healpy as hp
        >>> from hips.utils import WCSGeometry
        >>> from astropy.coordinates import SkyCoord
        >>> from hips.utils import compute_healpix_pixel_indices
        >>> order = 3
        >>> nside = hp.order2nside(order)
        >>> skycoord = SkyCoord(10, 20, unit="deg")
        >>> wcs_geometry = WCSGeometry.create(skydir=skycoord, shape=(10, 20), coordsys='CEL', projection='AIT', cdelt=1.0, crpix=(1., 1.))
        >>> compute_healpix_pixel_indices(wcs_geometry, nside)
        [ 84 111 112 113 142 143 144 145 146 174 175 176 177 178 206 207 208 209
        210 238 239 240 241 270 271 272 273 274 302 303 304 305 334 335 336 337
        367 368 399]
    """
    y_center, x_center = wcs_geometry.shape[0] // 2, wcs_geometry.shape[1] // 2
    lon_center, lat_center = wcs_geometry.wcs.all_pix2world(x_center, y_center, 1)
    vec = hp.ang2vec(lon_center, lat_center, lonlat=True)
    separations = angular_separation(x_center, y_center, lon_center, lat_center)
    max_separation = np.nanmax(separations)
    return hp.query_disc(nside, vec, max_separation)
