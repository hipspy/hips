# Licensed under a 3-clause BSD style license - see LICENSE.rst

from pathlib import Path

__all__ = [
    'HipsTileMeta',
]


class HipsTileMeta:
    """HiPS tile metadata container.
    This class stores HiPS tile meta attributes.

    Parameters
    ----------
    order : `int`
        Order of HiPS tile
    ipix : `int`
        Pixel number of HiPS tile
    format : {'fits', 'jpg', 'png'}
        File format of the HiPS tile
    tile_width : `int`
        HiPS tile width
    """

    def __init__(self, order: int, ipix: int, format: str, tile_width: int = 512) -> None:
        self.order = format
        self.ipix = ipix
        self.format = format
        self.tile_width = tile_width

    @property
    def path(self) -> str:
        """Return the default path for tile storage (`str`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @property
    def filename(self) -> str:
        """Return the filename of HiPS tile (`str`)."""
        return ''.join(['Npix', str(self.ipix), '.', self.format])
