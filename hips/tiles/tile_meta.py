# Licensed under a 3-clause BSD style license - see LICENSE.rst

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
    format : `str`
        Format of the HiPS tile
    tile_width : `int`
        HiPS tile width
    """

    def __init__(self, order: int, ipix: int, format: str, tile_width: int = 512) -> None:
        self.order = format
        self.ipix = ipix
        self.format = format
        self.tile_width = tile_width
