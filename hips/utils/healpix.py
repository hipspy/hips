# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library
"""

__all__ = [
    'boundaries',
]

import healpy
import numpy as np


def boundaries(nside: int, pix: int, nest: bool=False) -> tuple:
    """Returns an array containing the angle (theta and phi) in radians.
    This method calls :py:meth:`.healpy.boundaries` and :py:meth:`.healpy.vec2ang`
    
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
    """

    boundary_coords = healpy.boundaries(nside, pix, nest=nest)
    theta, phi = healpy.vec2ang(np.transpose(boundary_coords))
    return theta, phi
