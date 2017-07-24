# Licensed under a 3-clause BSD style license - see LICENSE.rst
from typing import List
import numpy as np
from ..utils.healpix import healpix_order_to_npix
from ..tiles import HipsTile

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
        data = np.empty(shape, tiles[0].data.dtype)

        # Copy over the tile data into the all-sky image
        for tile in tiles:
            tile_slice = HipsTileAllskyArray._tile_slice(
                ipix=tile.meta.ipix,
                tile_width=tile.meta.width,
                n_tiles_in_row=n_tiles_in_row,
            )
            data[tile_slice] = tile.data

        return data

    @property
    def tiles(self) -> List[HipsTile]:
        """Split into a list of `~hips.HipsTile`.

        This is called when using the all-sky image for drawing.
        """
        return [self.tile(ipix) for ipix in range(self.n_tiles)]

    def tile(self, ipix: int, copy: bool = True) -> HipsTile:
        """Extract one of the tiles (`~hips.HipsTile`)

        A copy of the data by default.
        For drawing we could avoid the copy by passing ``copy=False`` here.
        """
        meta = self.meta.copy()
        meta.ipix = ipix
        meta.width = self.tile_width

        tile_slice = self._tile_slice(ipix, self.tile_width, self.n_tiles_in_row)
        data = self.data[tile_slice]

        if copy:
            data = data.copy()

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
