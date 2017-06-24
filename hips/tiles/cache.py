# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Functions and classes to fetch and cache tiles."""
from pathlib import Path
from typing import List
from .tile import HipsTile
from .tile_meta import HipsTileMeta

__all__ = [
    'HipsTileCache',
]

__doctest_skip__ = ['HipsTileCache']


class HipsTileCache:
    """HiPS tile on-disk cache.

    Uses the standard way to organise HiPS files
    (the same one that's used on the server).

    Parameters
    ----------
    base_path : str
        Base path on local machine for the cache.

    Examples
    --------
    To download a bunch of tiles to your local disk:

    >>> from hips import HipsTileCache
    >>> tiles = 'todo'
    >>> hips_cache = HipsTileCache('/tmp/hips_test')
    >>> hips_cache.fetch(tiles)
    >>> tile = hips_cache.get(tiles[0].meta)
    """

    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def fetch(self, tiles: List[HipsTileMeta]) -> None:
        """TODO"""
        for tile in tiles:
            tile.fetch(...)
            filename = self.make_filename(tile.meta)
            tile.write(filename)

    def get(self, meta: HipsTileMeta) -> HipsTile:
        """TODO"""
        filename = self.make_filename(meta)
        return HipsTile.read(meta, filename)

    def has_tile(self, meta: HipsTileMeta):
        raise NotImplementedError

    def make_filename(self, meta: HipsTileMeta) -> Path:
        return self.base_path / meta.filename
