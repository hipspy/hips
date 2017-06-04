# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library
"""

__all__ = [
    'boundaries',
]

import healpy


def boundaries(nside, pix, step=1, nest=False):
    """Returns an array containing the longitude and latitude.

    Parameters
    ----------
        nside : int

            The nside of the HEALPix map

        pix : int

            Pixel identifier

        step : int, optional

            Number of elements for each side of the pixel

        nest : bool, optional

            If True, assume NESTED pixel ordering, otherwise, RING pixel ordering

    Returns
    -------
    longitude, latitude : float, array
        Longitude and latitude positions
    """

    boundary_coords = healpy.boundaries(nside, pix, nest=nest)
    lon, lat = healpy.vec2ang(boundary_coords, lonlat=True)
    return [lon, lat]
