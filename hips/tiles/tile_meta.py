# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path

__all__ = [
    'HipsTileMeta',
]


class HipsTileMeta:
    """HiPS tile metadata.

    Parameters
    ----------
    order : `int`
        HEALPix order
    ipix : `int`
        HEALPix pixel number
    file_format : {'fits', 'jpg', 'png'}
        File format
    tile_width : `int`
        Tile width (in pixels)
    """

    def __init__(self, order: int, ipix: int, file_format: str, tile_width: int = 512) -> None:
        self.order = order
        self.ipix = ipix
        self.file_format = file_format
        self.tile_width = tile_width

    def __eq__(self, other: 'HipsTileMeta') -> bool:
        return (
            self.order == other.order and
            self.ipix == other.ipix and
            self.file_format == other.file_format and
            self.tile_width == other.tile_width
        )

    @property
    def path(self) -> Path:
        """Return the default path for tile storage (`~pathlib.Path`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @property
    def filename(self) -> str:
        """Return the filename of HiPS tile (`str`)."""
        return ''.join(['Npix', str(self.ipix), '.', self.file_format])

    @property
    def full_path(self) -> Path:
        """Full path (folder and filename) (`~pathlib.Path`)"""
        return self.path / self.filename
