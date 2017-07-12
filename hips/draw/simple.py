# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS tile drawing -- simple method."""
from typing import Generator, Any
import numpy as np
from astropy.wcs.utils import proj_plane_pixel_scales
from skimage.transform import ProjectiveTransform, warp
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..utils import WCSGeometry, compute_healpix_pixel_indices

__all__ = [
    'draw_sky_image',
    'make_sky_image',
    'SimpleTilePainter',
    'compute_matching_hips_order'
]

__doctest_skip__ = [
    'compute_matching_hips_order',
]


# TODO: Fix type annotation issue
def draw_sky_image(geometry: WCSGeometry, tiles: Generator[HipsTile, Any, Any],
                   hips_survey: HipsSurveyProperties, tile_format: str) -> np.ndarray:
    """Draw sky image using the simple and quick method.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    tiles : List[HipsTile]
        A list of HipsTile
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : `str`
        Format of HiPS tile

    Returns
    -------
    np.ndarray
        Returns a numpy array containing all HiPS tiles projected onto it
    """
    if tile_format == 'jpg':
        shape = (geometry.shape.height, geometry.shape.width, 3)
    elif tile_format == 'png':
        shape = (geometry.shape.height, geometry.shape.width, 4)
    else:
        shape = (geometry.shape.height, geometry.shape.width)
    image = np.zeros(shape)
    for tile in tiles:
        painter = SimpleTilePainter(geometry, hips_survey, tile)
        image += painter.warp_image()
    return image


class SimpleTilePainter:
    """Paint a single tile using a simple projective transformation method.
    The algorithm implemented is described here: :ref:`drawing_algo`.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile : `HipsTile`
       An object of HipsTile
    """

    def __init__(self, geometry: WCSGeometry, hips_survey: HipsSurveyProperties, tile: HipsTile) -> None:
        self.geometry = geometry
        self.hips_survey = hips_survey
        self.tile = tile

    @property
    def dst(self) -> np.ndarray:
        """Destination array for projective transform"""
        width = self.hips_survey.tile_width
        return np.array(
            [[width - 1, 0],
             [width - 1, width - 1],
             [0, width - 1],
             [0, 0]],
        )

    @property
    def projection(self) -> ProjectiveTransform:
        """Estimate projective transformation on a HiPS tile"""
        corners = self.tile.meta.skycoord_corners.to_pixel(self.geometry.wcs)
        src = np.array(corners).T.reshape((4, 2))
        dst = self.dst
        pt = ProjectiveTransform()
        pt.estimate(src, dst)
        return pt

    def warp_image(self) -> np.ndarray:
        """Warp a HiPS tile and a sky image"""
        return warp(
            self.tile.data,
            self.projection,
            output_shape=self.geometry.shape,
            preserve_range=True,
        )


def fetch_tiles(healpix_pixel_indices: np.ndarray, order: int,
                hips_survey: HipsSurveyProperties, tile_format: str) -> 'HipsTile':
    """Fetch HiPS tiles from a remote URL.

    Parameters
    ----------
    healpix_pixel_indices : np.ndarray
        A list of HEALPix pixel indices
    order : int
        Order of the HEALPix map
    hips_survey : HipsSurveyProperties
        An object of HipsSurveyProperties
    tile_format : `str`
        Format of HiPS tile

    Returns
    -------
    'HipsTile'
        Returns an object of HipsTile
    """
    for healpix_pixel_index in healpix_pixel_indices:
        tile_meta = HipsTileMeta(
            order=order,
            ipix=healpix_pixel_index,
            frame=hips_survey.astropy_frame,
            file_format=tile_format,
        )
        tile = HipsTile.fetch(tile_meta, hips_survey.tile_access_url(order=order, ipix=healpix_pixel_index) + tile_meta.filename)
        yield tile


def compute_matching_hips_order(geometry: WCSGeometry, hips_survey: HipsSurveyProperties) -> int:
    """Compute HiPS tile order matching a given image pixel size.

    Parameters
    ----------
    geometry : WCSGeometry
        Geometry of the output image
    hips_survey : HipsSurveyProperties
        An object of HipsSurveyProperties

    Returns
    -------
    'int'
        Returns HiPS order

    Examples
    --------
    >>> from hips.draw import compute_matching_hips_order
    >>> from astropy.coordinates import SkyCoord
    >>> url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    >>> hips_survey = HipsSurveyProperties.fetch(url)
    >>> geometry = WCSGeometry.create_simple(
    ...     skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
    ...     width=2000, height=1000, fov="3 deg",
    ...     coordsys='icrs', projection='AIT'
    ... )
    >>> compute_matching_hips_order(geometry, hips_survey)
    7
    """

    # Sky image angular resolution (pixel size in degree)
    resolution = np.min(proj_plane_pixel_scales(geometry.wcs))
    desired_order = _get_hips_order_for_resolution(hips_survey.tile_width, resolution)
    # Return the desired order, or the highest resolution available.
    # Note that HiPS never has resolution less than 3,
    # and that limit is handled in _get_hips_order_for_resolution
    return np.min([desired_order, hips_survey.hips_order])


def _get_hips_order_for_resolution(tile_width, resolution):
    """Finding the best HiPS order by looping through all possible options."""
    tile_order = np.log2(tile_width)
    full_sphere_area = 4 * np.pi * np.square(180 / np.pi)
    # 29 is the maximum order supported by healpy and 3 is the minimum order
    for candidate_tile_order in range(3, 29 + 1):
        tile_resolution = np.sqrt(full_sphere_area / 12 / 4 ** (candidate_tile_order + tile_order))
        # Finding the smaller tile order with a resolution equal or better than geometric resolution
        if tile_resolution <= resolution:
            break

    return candidate_tile_order


def make_sky_image(geometry: WCSGeometry, hips_survey: HipsSurveyProperties, tile_format: str) -> np.ndarray:
    """Make sky image: fetch tiles and draw.
    The example for this can be found on the :ref:`gs` page.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        Geometry of the output image
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : `str`
        Format of HiPS tile

    Returns
    -------
    data : `~numpy.ndarray`
        Output image pixels
    """
    order = compute_matching_hips_order(geometry, hips_survey)
    healpix_pixel_indices = compute_healpix_pixel_indices(
        wcs_geometry=geometry,
        order=order,
        healpix_frame=hips_survey.astropy_frame,
    )
    # TODO: this isn't a good API. Will become better when we have a cache.
    tiles = fetch_tiles(healpix_pixel_indices, order, hips_survey, tile_format)

    image_data = draw_sky_image(geometry, tiles, hips_survey, tile_format)

    return image_data
