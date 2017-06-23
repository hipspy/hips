# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from io import BytesIO

import numpy as np
from PIL import Image
from astropy.io import fits
from astropy.io.fits.header import Header

from .tile_meta import HipsTileMeta

__all__ = [
    'HipsTile',
]

__doctest_skip__ = ['HipsTile']


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading, and writing a HiPS tile.

    Parameters
    ----------
    meta : `HipsTileMeta`
        Metadata of HiPS tile
    data : `~numpy.ndarray`
        Data containing HiPS tile
    header : `~astropy.io.fits.Header`
        Header of HiPS tile

    Examples
    --------
        >>> from hips.tiles import HipsTile
        >>> from hips.tiles import HipsTileMeta
        >>> meta = HipsTileMeta(order=6, ipix=30889, format='fits')
        >>> hips_tile = HipsTile.read(meta)
        >>> hips_tile.data
        array([[0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               ...,
               [0, 0, 0, ..., 1, 0, 0],
               [0, 0, 0, ..., 1, 0, 1],
               [0, 0, 0, ..., 1, 0, 1]], dtype=int16)
        """

    def __init__(self, meta: HipsTileMeta, data: np.ndarray = None, header: Header = None) -> None:
        self.meta = meta
        self.data = data
        self.header = header

    @classmethod
    def fetch(cls, meta: HipsTileMeta, url: str) -> 'HipsTile':
        """Fetch HiPS tile and load into memory (`HipsTile`).

        Parameters
        ----------
        meta : `HipsTileMeta`
            Metadata of HiPS tile
        url : `str`
            URL containing HiPS tile
        """
        raw_image = BytesIO(urllib.request.urlopen(url).read())
        if meta.file_format == 'fits':
            hdulist = fits.open(raw_image)
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(meta, data, header)
        else:
            data = np.array(Image.open(raw_image))
            return cls(meta, data)

    @classmethod
    def read(cls, meta: HipsTileMeta, file_path: str = None) -> 'HipsTile':
        """Read HiPS tile data from a directory and load into memory (`HipsTile`).

        Parameters
        ----------
        meta : `HipsTileMeta`
            Metadata of HiPS tile
        file_path : `str`
            File path to store a HiPS tile
        """
        if file_path is None:
            path = meta.path / meta.filename  # pragma: no cover
        else:
            path = file_path

        if meta.file_format == 'fits':
            hdulist = fits.open(str(path))
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(meta, data, header)
        else:
            data = np.array(Image.open(str(path)))
            return cls(meta, data)

    def write(self, filename: str, file_path: str = None) -> None:
        """Write HiPS tile by a given filename.

        Parameters
        ----------
        filename : `str`
            Name of the file
        file_path : `str`
            File path to store a HiPS tile
        """
        if file_path is None:
            path = self.meta.path / self.meta.filename  # pragma: no cover
        else:
            path = file_path

        if self.meta.file_format == 'fits':
            hdu = fits.PrimaryHDU(self.data, header=self.header).writeto(str(path))
        else:
            Image.fromarray(self.data).save(str(path))
