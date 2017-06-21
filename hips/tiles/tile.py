# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from io import BytesIO

import numpy as np
from PIL import Image
from astropy.io import fits
from astropy.io.fits.header import Header

from .tile_meta import HipsTileMeta
from ..utils.tile import tile_path

__all__ = [
    'HipsTile',
]

__doctest_skip__ = ['HipsTile']


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading, and writing a HiPS tile.

    Parameters
    ----------
    hips_tile_meta : `HipsTileMeta`
        Metadata of HiPS tile
    format : `str`
        Format of HiPS tile
    data : `np.ndarray`
        Data containing HiPS tile
    header : `astropy.io.fits.Header`
        Header of HiPS tile

    Examples
    --------
        >>> import urllib.request
        >>> from hips.tiles import HipsTile
        >>> from hips.tiles import HipsTileMeta
        >>> from astropy.tests.helper import remote_data
        >>> hips_tile_metadata = HipsTileMeta(order=6, ipix=30889, format='fits')
        >>> hips_tile = HipsTile.read(hips_tile_metadata, 'Npix30889.fits')
        >>> hips_tile.data
        array([[0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               ...,
               [0, 0, 0, ..., 1, 0, 0],
               [0, 0, 0, ..., 1, 0, 1],
               [0, 0, 0, ..., 1, 0, 1]], dtype=int16)
        """

    def __init__(self, hips_tile_meta: HipsTileMeta, data: np.ndarray = None, header: Header = None) -> None:
        self.hips_tile_meta = hips_tile_meta
        self.format = format
        self.data = data
        self.header = header

    @classmethod
    def fetch(cls, hips_tile_meta: HipsTileMeta, url: str) -> 'HipsTile':
        """Fetch HiPS tile and load into memory (`HipsTile`).

        Parameters
        ----------
        hips_tile_meta : `HipsTileMeta`
            Metadata of HiPS tile
        url : `str`
            URL containing HiPS tile
        """
        raw_image = BytesIO(urllib.request.urlopen(url).read())
        if hips_tile_meta.format == 'fits':
            hdulist = fits.open(raw_image)
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(hips_tile_meta, data, header)
        else:
            data = np.array(Image.open(raw_image))
            return cls(hips_tile_meta, data)

    @classmethod
    def read(cls, hips_tile_meta: HipsTileMeta, filename: str) -> 'HipsTile':
        """Read HiPS tile data from a directory and load into memory (`HipsTile`).

        Parameters
        ----------
        hips_tile_meta : `HipsTileMeta`
            Metadata of HiPS tile
        filename : `str`
            File name of HiPS tile
        """
        path = tile_path().absolute() / filename
        if hips_tile_meta.format == 'fits':
            hdulist = fits.open(path)
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(hips_tile_meta, data, header)
        else:
            data = np.array(Image.open(str(path)))
            return cls(hips_tile_meta, data)

    def write(self, filename: str) -> None:
        """Write HiPS tile by a given filename (`None`).

        Parameters
        ----------
        filename : `str`
            Name of the file
        """
        path = tile_path().absolute() / filename
        if self.hips_tile_meta.format == 'fits':
            hdu = fits.PrimaryHDU(self.data, header=self.header)
            hdulist = fits.HDUList([hdu])
            hdulist.writeto(str(path))
            hdulist.close()
        else:
            Image.fromarray(self.data).save(str(path))
