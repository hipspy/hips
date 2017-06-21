# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALpy wrapper functions.

This module contains wrapper functions around HEALPix utilizing
the healpy library.
"""

from pathlib import Path

__all__ = [
    'tile_path',
]


def tile_path() -> Path:
    """Return default path of HiPS tile storage."""
    path = Path('hips', 'tiles', 'tests', 'data')
    return path