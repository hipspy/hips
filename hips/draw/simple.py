# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS tile drawing -- simple method."""
import numpy as np
import healpy as hp
from typing import List
from skimage import transform as tf
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..utils import WCSGeometry, compute_healpix_pixel_indices, boundaries

__all__ = [
    'draw_sky_image',
    'make_sky_image',
]


def draw_sky_image(geometry: WCSGeometry, tiles: List[HipsTile]) -> np.ndarray:
    """Draw sky image using the simple and quick method.

    TODO: fill in code here
    """
    # TODO: copy over (and clean up a little) the drawing code you already have in notebooks.
    # Suggestion: don't debug the code now, just put it here.
    # First implement simple tile caching so that you can draw without needing to make web queries.

    # Probably this function should just loop over tiles and call a `_draw_sky_image_one_tile`
    # helper function, and sum up the results.
    for tile in HipsTile:
        nside = hp.order2nside(tile.meta.order)
        corners = boundaries(nside, tile.meta.ipix)
        # tile.meta.

    return np.zeros(geometry.shape)

def _draw_sky_image_one_tile(corners: tuple, tile: HipsTile) -> np.ndarray:


def _fetch_tiles(healpix_pixel_indices, order, hips_survey):
    for healpix_pixel_index in healpix_pixel_indices:
        tile_meta = HipsTileMeta(order=order, ipix=healpix_pixel_index, file_format='jpg')
        tile = HipsTile.fetch(tile_meta, hips_survey.base_url)
        yield tile


def make_sky_image(geometry: WCSGeometry, hips_survey: HipsSurveyProperties):
    """Make sky image: fetch tiles and draw.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        Geometry of the output image
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties

    Returns
    -------
    data : `~numpy.ndarray`
        Output image pixels

    Examples
    --------
    Define which image you want:

    >>> geometry = tbd

    Define which HiPS survey you want:

    >>> hips_survey = tbd

    Compute the image:

    >>> from hips import make_sky_image
    >>> data = make_sky_image(geometry, hips_survey)

    If you want, you can save the image to file:
    >>> from astropy.io import fits
    >>> hdu = fits.PrimaryHDU(data=data, header=geometry.header)
    >>> hdu.writeto('my_image.fits')
    """
    # Compute list of tiles needed
    order = hips_survey.hips_order
    healpix_pixel_indices = compute_healpix_pixel_indices(geometry, order)

    # Fetch the tiles
    # TODO: this isn't a good API. Will become better when we have a cache.
    tiles = _fetch_tiles(healpix_pixel_indices, order, hips_survey)

    # Draw the image
    image_data = draw_sky_image(geometry, tiles)

    return image_data
