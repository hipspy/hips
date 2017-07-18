# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HiPS tile drawing -- simple method."""
from typing import Tuple, List
import numpy as np
from astropy.wcs.utils import proj_plane_pixel_scales
from skimage.transform import ProjectiveTransform, warp
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..utils import WCSGeometry, healpix_pixels_in_sky_image, get_hips_order_for_resolution

__all__ = [
    'make_sky_image',
    'SimpleTilePainter',

]

__doctest_skip__ = [
    'SimpleTilePainter'
]


class SimpleTilePainter:
    """Draw sky image using the simple and quick method.

    Paint HiPS tiles onto an all-sky image using a simple projective
    transformation method. The algorithm implemented is described
    here: :ref:`drawing_algo`.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile

    Examples
    --------
    >>> from hips.utils import WCSGeometry
    >>> from hips.draw import SimpleTilePainter
    >>> from hips.tiles import HipsSurveyProperties
    >>> from astropy.coordinates import SkyCoord
    >>> url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    >>> hips_survey = HipsSurveyProperties.fetch(url)
    >>> geometry = WCSGeometry.create_simple(
    ...     skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
    ...     width=2000, height=1000, fov="3 deg",
    ...     coordsys='icrs', projection='AIT'
    ... )
    >>> painter = SimpleTilePainter(geometry, hips_survey, 'fits')
    >>> painter.draw_hips_order
    7
    >>> painter.run()
    >>> painter.image.shape
    (1000, 2000)
    """

    def __init__(self, geometry: WCSGeometry, hips_survey: HipsSurveyProperties, tile_format: str) -> None:
        self.geometry = geometry
        self.hips_survey = hips_survey
        self.tile_format = tile_format
        self._tiles = None

    @property
    def image(self) -> np.ndarray:
        """Computed sky image (`~numpy.ndarray`).

        * The ``dtype`` is always chosen to match the tile ``dtype``.
          This is ``uint8`` for JPG or PNG tiles,
          and can be e.g. ``int16`` or ``float32`` for FITS tiles.
        * The output shape is documented here: `~SimpleTilePainter.shape`.
        """
        return self.float_image.astype(self.tiles[0].data.dtype)

    @property
    def draw_hips_order(self) -> int:
        """Compute HiPS tile order matching a given image pixel size."""
        # Sky image angular resolution (pixel size in degrees)
        resolution = np.min(proj_plane_pixel_scales(self.geometry.wcs))
        desired_order = get_hips_order_for_resolution(self.hips_survey.tile_width, resolution)
        # Return the desired order, or the highest resolution available.
        # Note that HiPS never has resolution less than 3,
        # and that limit is handled in _get_hips_order_for_resolution
        return np.min([desired_order, self.hips_survey.hips_order])

    @property
    def tile_indices(self):
        """Get list of index values for HiPS tiles."""
        return healpix_pixels_in_sky_image(
            wcs_geometry=self.geometry,
            order=self.draw_hips_order,
            healpix_frame=self.hips_survey.astropy_frame,
        )

    @property
    def dst(self) -> np.ndarray:
        """Destination array for projective transform."""
        width = self.hips_survey.tile_width
        return np.array(
            [[width - 1, 0],
             [width - 1, width - 1],
             [0, width - 1],
             [0, 0]],
        )

    def projection(self, tile: HipsTile) -> ProjectiveTransform:
        """Estimate projective transformation on a HiPS tile."""
        corners = tile.meta.skycoord_corners.to_pixel(self.geometry.wcs)
        src = np.array(corners).T.reshape((4, 2))
        dst = self.dst
        pt = ProjectiveTransform()
        pt.estimate(src, dst)
        return pt

    def _fetch_tiles(self) -> HipsTile:
        """Generator function to fetch HiPS tiles from a remote URL."""
        for healpix_pixel_index in self.tile_indices:
            tile_meta = HipsTileMeta(
                order=self.draw_hips_order,
                ipix=healpix_pixel_index,
                frame=self.hips_survey.astropy_frame,
                file_format=self.tile_format,
            )
            url = self.hips_survey.tile_url(tile_meta)
            tile = HipsTile.fetch(tile_meta, url)
            yield tile

    @property
    def tiles(self) -> List[HipsTile]:
        """List of `~hips.HipsTile` (cached on multiple access)."""
        if self._tiles is None:
            self._tiles = list(self._fetch_tiles())

        return self._tiles

    @property
    def shape(self) -> Tuple[int]:
        """Shape of the output image.

        The output image shape is 2-dim for grayscale, and 3-dim for color images:

        * ``shape = (height, width)`` for FITS images with one grayscale channel
        * ``shape = (height, width, 3)`` for JPG images with three RGB channels
        * ``shape = (height, width, 4)`` for PNG images with four RGBA channels
        """
        height = self.geometry.shape.height
        width = self.geometry.shape.width
        tile_format = self.tile_format

        if tile_format == 'fits':
            return height, width
        elif tile_format == 'jpg':
            return height, width, 3
        elif tile_format == 'png':
            return height, width, 4
        else:
            return ValueError(f'Invalid tile format: {tile_format}')

    def warp_image(self, tile: HipsTile) -> np.ndarray:
        """Warp a HiPS tile and a sky image."""
        return warp(
            tile.data,
            self.projection(tile),
            output_shape=self.geometry.shape,
            preserve_range=True,
        )

    def draw_tiles(self) -> np.ndarray:
        """Draw HiPS tiles onto an empty image."""
        tiles = self.tiles

        image = np.zeros(self.shape, dtype=np.float32)
        for tile in tiles:
            tile_image = self.warp_image(tile)
            # TODO: put better algorithm here instead of summing pixels
            # this can lead to pixels that are painted twice and become to bright
            image += tile_image

        return image

    def run(self) -> None:
        """Run all steps of the naive algorithm."""
        self.float_image = self.draw_tiles()


def make_sky_image(geometry: WCSGeometry, hips_survey: HipsSurveyProperties, tile_format: str) -> np.ndarray:
    """Make sky image: fetch tiles and draw.

    The example for this can be found on the :ref:`gs` page.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        Geometry of the output image
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile to use
        (some surveys are available in several formats, so this extra argument is needed)

    Returns
    -------
    image : `~numpy.ndarray`
        Output image pixels
    """
    painter = SimpleTilePainter(geometry, hips_survey, tile_format)
    painter.run()

    return painter.image
