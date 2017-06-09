# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library
"""

__all__ = [
    'boundaries',
]

import healpy as hp
import numpy as np


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
