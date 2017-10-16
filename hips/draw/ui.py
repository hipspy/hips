# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""The high-level end user interface (UI)."""
import numpy as np
from PIL import Image
from astropy.io import fits
from typing import List, Union
from ..utils.wcs import WCSGeometry
from ..tiles import HipsSurveyProperties, HipsTile
from .paint import HipsPainter

__all__ = [
    'make_sky_image',
    'HipsDrawResult',
]


def make_sky_image(geometry: Union[dict, WCSGeometry], hips_survey: Union[str, 'HipsSurveyProperties'],
                   tile_format: str, precise: bool = False, progress_bar: bool = True, fetch_opts: dict = None) -> 'HipsDrawResult':
    """Make sky image: fetch tiles and draw.

    The example for this can be found on the :ref:`gs` page.

    Parameters
    ----------
    geometry : dict or `~hips.utils.WCSGeometry`
        Geometry of the output image
    hips_survey : str or `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile to use
        (some surveys are available in several formats, so this extra argument is needed)
    precise : bool
        Use the precise drawing algorithm
    progress_bar : bool
        Show a progress bar for tile fetching and drawing
    fetch_opts : dict
        Keyword arguments for fetching HiPS tiles. To see the
        list of passable arguments, refer to `~hips.fetch_tiles`

    Returns
    -------
    result : `~hips.HipsDrawResult`
        Result object
    """
    painter = HipsPainter(geometry, hips_survey, tile_format, precise, progress_bar, fetch_opts)
    painter.run()
    return HipsDrawResult.from_painter(painter)


class HipsDrawResult:
    """HiPS draw result object (sky image and more).

    Parameters
    ----------
    image : `~numpy.ndarray`
        Sky image (the main result)
    geometry : `~hips.utils.WCSGeometry`
        WCS geometry of the sky image
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile
    tiles : list
        Python list of `~hips.HipsTile` objects that were used
    stats : dict
        Information including time for fetching and drawing HiPS tiles
    """

    def __init__(self, image: np.ndarray, geometry: WCSGeometry, tile_format: str, tiles: List[HipsTile], stats: dict) -> None:
        self.image = image
        self.geometry = geometry
        self.tile_format = tile_format
        self.tiles = tiles
        self.stats = stats

    def __str__(self):
        return (
            'HiPS draw result:\n'
            f'Sky image: shape={self.image.shape}, dtype={self.image.dtype}\n'
            f'WCS geometry: {self.geometry}\n'
        )

    def __repr__(self):
        return (
            'HipsDrawResult('
            f'width={self.image.shape[0]}, '
            f'height={self.image.shape[1]}, '
            f'channels={self.image.ndim}, '
            f'dtype={self.image.dtype}, '
            f'format={self.tile_format}'
            ')'
        )

    @classmethod
    def from_painter(cls, painter: HipsPainter) -> 'HipsDrawResult':
        """Make a `~hips.HipsDrawResult` from a `~hips.HipsTilePainter`."""
        return cls(
            image=painter.image,
            geometry=painter.geometry,
            tile_format=painter.tile_format,
            tiles=painter.tiles,
            stats=painter._stats,
        )

    def write_image(self, filename: str) -> None:
        """Write image to file.

        Parameters
        ----------
        filename : str
            Filename
        """
        if self.tile_format == 'fits':
            hdu = fits.PrimaryHDU(data=self.image, header=self.geometry.fits_header)
            hdu.writeto(filename)
        else:
            image = Image.fromarray(self.image)
            image.save(filename)

    def plot(self) -> None:
        """Plot the all sky image and overlay HiPS tile outlines.

        Uses `astropy.visualization.wcsaxes`.
        """
        import matplotlib.pyplot as plt
        for tile in self.tiles:
            corners = tile.meta.skycoord_corners
            corners = corners.transform_to(self.geometry.celestial_frame)
            ax = plt.subplot(projection=self.geometry.wcs)
            opts = dict(color='red', lw=1, )
            ax.plot(corners.data.lon.deg, corners.data.lat.deg,
                    transform=ax.get_transform('world'), **opts)
        ax.imshow(self.image, origin='lower')

    def report(self) -> None:
        """Print a brief report for the fetched data."""

        print (
            f"Time for fetching tiles = {self.stats['fetch_time']} seconds\n"
            f"Time for drawing tiles = {self.stats['draw_time']} seconds\n"
            f"Total memory consumed = {self.stats['consumed_memory'] / 1e6} MB\n"
            f"Total tiles fetched = {self.stats['tile_count']}\n"
        )
