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
    all_sky = np.zeros(geometry.shape)
    for tile in tiles:
        draw_tile = DrawSkyImageOneTile(geometry, tile, all_sky.shape)
        draw_tile.compute_corners()
        draw_tile.apply_projection()
        all_sky += draw_tile.warp_image()
    return all_sky


class DrawSkyImageOneTile:
    """A private function for drawing a tile over a sky image.

    Parameters
    ----------
    geometry : 'WCSGeometry'
        An object of WCSGeometry
    tile : HipsTile
       An object of HipsTile
    shape ; tuple
        Shape of the all-sky image
    """

    def __init__(self, geometry: WCSGeometry, tile: HipsTile, shape: tuple) -> None:
        self.geometry = geometry
        self.tile = tile
        self.shape = shape
        self.wcs = WCS(tile.header)
        self.corners = None
        self.pt = None

    def compute_corners(self) -> None:
        nside = hp.order2nside(self.tile.meta.order)
        theta, phi = boundaries(nside, self.tile.meta.ipix)
        radec = SkyCoord(ra=phi, dec=np.pi / 2 - theta, unit='radian', frame='icrs')
        self.corners = []
        for i in range(len(radec.ra.deg)):
            self.corners.append([radec.ra.deg[i], radec.dec.deg[i]])

    def apply_projection(self) -> None:
        src = self.geometry.wcs.wcs_world2pix(self.corners, 0)
        dst = np.array([[511, 0], [511, 511], [0, 511], [0, 0]])
        self.pt = tf.ProjectiveTransform()
        self.pt.estimate(src, dst)

    def warp_image(self) -> np.ndarray:
        return tf.warp(self.tile.data, self.pt, output_shape=self.shape)


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
    >>> from astropy.io import fits
    >>> from hips.utils import WCSGeometry
    >>> from hips.draw import make_sky_image
    >>> from hips.tiles import HipsSurveyProperties
    >>> geometry = WCSGeometry.create(
    ...     skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    ...     shape=(1000, 2000), coordsys='GAL',
    ...     projection='AIT', cdelt=0.01, crpix=(1000, 500),
    ... )
    >>> url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    >>> hips_survey = HipsSurveyProperties.fetch(url)
    >>> data = make_sky_image(geometry, hips_survey)
    >>> hdu = fits.PrimaryHDU(data=data, header=geometry.header)
    >>> hdu.writeto('my_image.fits')
    """
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

    image_data = draw_sky_image(geometry, tiles)

    return image_data
