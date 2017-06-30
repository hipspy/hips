# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS tile drawing -- simple method."""

import numpy as np
from skimage import transform as tf
from typing import List, Generator, Any

from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..utils import WCSGeometry, compute_healpix_pixel_indices, frames

__all__ = [
    'draw_sky_image',
    'make_sky_image',
    'SimpleTilePainter'
]


def draw_sky_image(geometry: WCSGeometry, tiles: Generator[HipsTile, Any, Any]) -> np.ndarray:
    """Draw sky image using the simple and quick method.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    tiles : List[HipsTile]
        A list of HipsTile

    Returns
    -------
    np.ndarray
        Returns a numpy array containing all HiPS tiles projected onto it
    """
    # TODO: Fix type annotation issue
    sky_sky = np.zeros(geometry.shape)
    for tile in tiles:
        painter = SimpleTilePainter(geometry, tile)
        sky_sky += painter.warp_image()
    return sky_sky


class SimpleTilePainter:
    """Paint a single tile using a simple projective transformation method.

    The algorithm implemented is described here: :ref:`drawing_algo`.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    tile : `HipsTile`
       An object of HipsTile
    """

    def __init__(self, geometry: WCSGeometry, tile: HipsTile) -> None:
        self.geometry = geometry
        self.tile = tile
        self.pt = None

    @property
    def projection(self) -> tf.ProjectiveTransform:
        """Estimate projective transformation on a HiPS tile"""
        corners = self.tile.meta.skycoord_corners.to_pixel(self.geometry.wcs)
        src = np.array(corners).T.reshape((4, 2))
        dst = self.tile.meta.dst
        self.pt = tf.ProjectiveTransform()
        self.pt.estimate(src, dst)
        return self.pt

    def warp_image(self) -> np.ndarray:
        """Warp a HiPS tile and a sky image"""
        return tf.warp(self.tile.data, self.projection, output_shape=self.geometry.shape, preserve_range=True)


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
    base_url = hips_survey.access_url + '/Norder' + str(hips_survey.hips_order) + '/Dir0/'
    for healpix_pixel_index in healpix_pixel_indices:
        tile_meta = HipsTileMeta(order=order, ipix=healpix_pixel_index,
                                 frame=frames()[hips_survey.hips_frame], file_format='fits')
        tile = HipsTile.fetch(tile_meta, base_url + tile_meta.filename)
        yield tile


def make_sky_image(geometry: WCSGeometry, hips_survey: HipsSurveyProperties) -> np.ndarray:
    """Make sky image: fetch tiles and draw.

    The example for this can be found on the :ref:`gs` page.

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
    """
    healpix_pixel_indices = compute_healpix_pixel_indices(geometry, hips_survey.hips_order)
    # TODO: this isn't a good API. Will become better when we have a cache.
    tiles = _fetch_tiles(healpix_pixel_indices, hips_survey.hips_order, hips_survey)

    image_data = draw_sky_image(geometry, tiles)

    return image_data
