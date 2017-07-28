# Licensed under a 3-clause BSD style license - see LICENSE.rst
from typing import List
import numpy as np
from ..utils.healpix import healpix_order_to_npix
from .tile import HipsTile

__all__ = [
    'HipsTileAllskyArray',
]

__doctest_skip__ = [
    'HipsTileAllskyArray',
]


class HipsTileAllskyArray(HipsTile):
    """All-sky tile array container.

    To quote from section 4.3.2 "Allsky preview file" of the HiPS IVOA working draft:
    "The tiles at low orders (0 to 3) may be packaged
    together into a unique file called Allsky."

    This class implements that all-sky tile array format.

    TODO: We're sub-classing `~hips.HipsTile` here at the moment.
    This is weird!
    Probably the current ``HipsTile`` should be renamed ``ImageIO``
    or be split up into functions that do image I/O in the three supported formats?

    TODO: We re-use the `~hips.HipsTileMeta` class to store ``order``
    as well as other info like ``file_format`` and ``frame``.
    Note that ``ipix`` doesn't make sense for an ``AllSkyTileArray``.
    Maybe there's  a better way to handle this without code duplication?

    Examples
    --------

    Load an example existing HiPS all-sky image
    (unfortunately one has to pass a dummy ipix value here):

    >>> from hips import HipsTileAllskyArray, HipsTileMeta
    >>> meta = HipsTileMeta(order=3, ipix=-1, file_format='jpg', frame='icrs')
    >>> url = 'http://alasky.unistra.fr/Fermi/Color/Norder3/Allsky.jpg'
    >>> allsky = HipsTileAllskyArray.fetch(meta, url)

    Now you can extract tiles (e.g. for drawing):

    >>> tile = allsky.tile(ipix=42)
    >>> tile.meta
    HipsTileMeta(order=3, ipix=42, file_format='jpg', frame='icrs', width=64)

    TODO: add an example how to go the other way: combine tiles into an allsky image.
    """

    def __repr__(self):
        return (
            'HipsTileAllskyArray('
            f'format={self.meta.file_format!r}, order={self.meta.order}, '
            f'width={self.width}, height={self.height}, '
            f'n_tiles={self.n_tiles}, '
            f'tile_width={self.tile_width}'
            ')'
        )

    @property
    def width(self) -> int:
        """Image pixel width (int)."""
        return self.data.shape[1]

    @property
    def height(self) -> int:
        """Image pixel height (int)"""
        return self.data.shape[0]

    @property
    def n_tiles(self) -> int:
        """Number of tiles in the image (int)."""
        return healpix_order_to_npix(self.meta.order)

    @property
    def n_tiles_in_row(self) -> int:
        """Number of tiles per tile row (int)."""
        return int(np.sqrt(self.n_tiles))

    @property
    def tile_width(self) -> int:
        """Pixel width of a single tile (int)."""
        return self.width // self.n_tiles_in_row

    @classmethod
    def from_tiles(cls, tiles: List[HipsTile]) -> 'HipsTileAllskyArray':
        """Create all-sky image from list of tiles."""
        meta = tiles[0].meta.copy()
        data = cls.tiles_to_allsky_array(tiles)
        # TODO: check return type here.
        # Pycharm warns that a `HipsTile` is returned here, not a `HipsTileAllskyArray`
        # Is this true or a bug in their static code analysis?
        return cls.from_numpy(meta, data)

    @staticmethod
    def tiles_to_allsky_array(tiles: List[HipsTile]) -> np.ndarray:
        """Combine tiles into an all-sky image."""
        # Compute all-sky image parameters that we need below
        n_tiles = len(tiles)
        n_tiles_in_row = int(np.sqrt(n_tiles))
        n_tiles_in_col = (n_tiles // n_tiles_in_row) + 1
        tile_width = tiles[0].meta.width

        # Make an empty all-sky image
        shape = (
            tile_width * n_tiles_in_col,  # height
            tile_width * n_tiles_in_row,  # width
        )
        if len(tiles[0].data.shape) == 3:
            shape = (*shape, tiles[0].data.shape[2])

        # TODO: is this a good way to fill the blank pixels?
        # I checked `datasets/samples/DSS2Red/Norder3/Allsky.fits` and
        # there in the FITS header and data array I see
        # BLANK = -32768.0
        # I don't do this here for now because I don't know how to
        # handle this properly for FITS / JPEG / PNG
        # Maybe we should switch to `NaN` or `-32768` for float data?
        blank_value = 0
        data = blank_value * np.ones(shape, tiles[0].data.dtype)

        # Copy over the tile data into the all-sky image
        for tile in tiles:
            tile_slice = HipsTileAllskyArray._tile_slice(
                ipix=tile.meta.ipix,
                tile_width=tile.meta.width,
                n_tiles_in_row=n_tiles_in_row,
            )
            # TODO: explain this flip. (see comment below in the tile method)
            data[::-1, ...][tile_slice] = tile.data[::-1, ...]

        return data

    @property
    def tiles(self) -> List[HipsTile]:
        """Split into a list of `~hips.HipsTile`.

        This is called when using the all-sky image for drawing.
        """
        return [self.tile(ipix) for ipix in range(self.n_tiles)]

    def tile(self, ipix: int) -> HipsTile:
        """Extract one of the tiles (`~hips.HipsTile`)

        A copy of the data by default.
        For drawing we could avoid the copy by passing ``copy=False`` here.
        """
        meta = self.meta.copy()
        meta.ipix = ipix
        meta.width = self.tile_width

        tile_slice = self._tile_slice(ipix, self.tile_width, self.n_tiles_in_row)
        # Note: apparently, tiles in all-sky files are ordered top to bottom,
        # left to right, always assuming the JPEG / PNG orientation, even for
        # FITS all-sky images!?
        # That's why we flip the all-sky image to JPEG / PNG orientation here
        # before extracting the tile data, and then we flip the tile data back
        # because internally we're always using the FITS tile orientation
        data = self.data[::-1, ...][tile_slice][::-1, ...]

        # data = self.data[tile_slice]

        return HipsTile.from_numpy(meta, data)

    @staticmethod
    def _tile_slice(ipix, tile_width, n_tiles_in_row):
        """Compute the 2-dim slice in the allsky ``data`` for a given tile."""
        w = tile_width
        row_idx, col_idx = divmod(ipix, n_tiles_in_row)
        return [
            slice(row_idx * w, (row_idx + 1) * w),
            slice(col_idx * w, (col_idx + 1) * w),
        ]
