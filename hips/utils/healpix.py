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


def boundaries(nside: int, pix: int, nest: bool=False) -> tuple:
    """Returns an array containing the angle (theta and phi) in radians.

    This function calls `healpy.boundaries` and `healpy.vec2ang`.

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
        >>> theta, phi = boundaries(nside, pix, nest=True)
        >>> SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')
        <SkyCoord (ICRS): (ra, dec) in deg
        [( 264.375, -24.62431835), ( 258.75 , -30.        ),
         ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """

    boundary_coords = hp.boundaries(nside, pix, nest=nest)
    theta, phi = hp.vec2ang(np.transpose(boundary_coords))
    return theta, phi
