# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS tile drawing -- simple method."""
import os
from pathlib import Path

import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from skimage import transform as tf
from typing import List

from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..utils import WCSGeometry, compute_healpix_pixel_indices, boundaries

__all__ = [
    'draw_sky_image',
    'make_sky_image',
]


def draw_sky_image(geometry: WCSGeometry, tiles: List[HipsTile]) -> np.ndarray:
    """Draw sky image using the simple and quick method.

    Parameters
    ----------
    geometry : 'WCSGeometry'
        An object of WCSGeometry
    tiles : List[HipsTile]
        A list of HipsTile

    Returns
    -------
    np.ndarray
        Returns a numpy array containing all HiPS tiles projected onto it
    """
    # TODO: copy over (and clean up a little) the drawing code you already have in notebooks.
    # Suggestion: don't debug the code now, just put it here.
    # First implement simple tile caching so that you can draw without needing to make web queries.

    # Probably this function should just loop over tiles and call a `_draw_sky_image_one_tile`
    # helper function, and sum up the results.
    all_sky = np.zeros(geometry.shape)
    for tile in tiles:
        nside = hp.order2nside(tile.meta.order)
        theta, phi = boundaries(nside, tile.meta.ipix)
        radec = SkyCoord(ra=phi, dec=np.pi / 2 - theta, unit='radian', frame='icrs')
        corners = []
        for i in range(len(radec.ra.deg)):
            corners.append([radec.ra.deg[i], radec.dec.deg[i]])
        all_sky += _draw_sky_image_one_tile(corners, WCS(tile.header), tile, all_sky.shape)
    return all_sky


def _draw_sky_image_one_tile(corners: list, wcs: WCS, tile: HipsTile, shape: tuple) -> np.ndarray:
    """A private function for drawing a tile over a sky image.

    Parameters
    ----------
    corners : `~astropy.coordinates.SkyCoord`
        Four corners of a HiPS tile
    wcs : `~astropy.wcs.WCS`
        WCS projection of a HiPS tile
    tile : 'HipsTile'
        An object of HipsTile
    shape ; tuple
        Shape of the all-sky image

    Returns
    -------
    np.ndarray
        Returns a numpy array containing the projected HiPS tile
    """
    src = wcs.wcs_world2pix(corners, 0)
    dst = np.array([[511, 0], [511, 511], [0, 511], [0, 0]])
    pt = tf.ProjectiveTransform()
    pt.estimate(src, dst)
    return tf.warp(tile.data, pt, output_shape=shape)


def _fetch_tiles(healpix_pixel_indices: np.ndarray, order: int, hips_survey: HipsSurveyProperties) -> 'HipsTile':
    """Fetch HiPS tiles from a remote URL.

    Parameters
    ----------
    healpix_pixel_indices : np.ndarray
        A list of HEALPix pixel indices
    order : int
        Order of the HEALPix map
    hips_survey : HipsSurveyProperties
        An object of HipsSurveyProperties

    Returns
    -------
    'HipsTile'
        Returns an object of  HipsTile
    """
    for healpix_pixel_index in healpix_pixel_indices:
        tile_meta = HipsTileMeta(order=order, ipix=healpix_pixel_index, file_format='fits')
        tile = HipsTile.fetch(tile_meta, hips_survey.base_url)
        yield tile


def make_sky_image(geometry: WCSGeometry, hips_survey: HipsSurveyProperties) -> np.ndarray:
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

    healpix_pixel_indices = compute_healpix_pixel_indices(geometry, hips_survey.hips_order)
    path = Path(os.environ['HIPS_EXTRA'])
    tiles_path = path / 'datasets' / 'samples' / 'DSS2Red' / 'Norder3' / 'Dir0'

    tiles = []
    for pixel_index in healpix_pixel_indices:
        meta = HipsTileMeta(hips_survey.hips_order, pixel_index, 'fits')
        filepath = str(tiles_path / meta.filename)
        tiles.append(HipsTile.read(meta, filepath))

    # Fetch the tiles
    # TODO: this isn't a good API. Will become better when we have a cache.
    # tiles = _fetch_tiles(healpix_pixel_indices, order, hips_survey)

    # Draw the image
    image_data = draw_sky_image(geometry, tiles)

    return image_data
