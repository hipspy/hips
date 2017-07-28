# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tile input / output (I/O) methods (both local and remote)."""
from typing import List
from pathlib import Path

__all__ = [
    'tile_default_url',
    'tile_default_path',
]


def _tile_default_location(order: int, ipix: int, file_format: str) -> List[str]:
    # Directory index: HiPS tiles are grouped in chunks of 10k tiles
    dir_idx = (ipix // 10_000) * 10_000

    return [
        f'Norder{order}',
        f'Dir{dir_idx}',
        f'Npix{ipix}.{file_format}',
    ]


def tile_default_url(order: int, ipix: int, file_format: str) -> str:
    loc = _tile_default_location(order, ipix, file_format)
    return '/'.join(loc)


def tile_default_path(order: int, ipix: int, file_format: str) -> Path:
    loc = _tile_default_location(order, ipix, file_format)
    return Path(*loc)
