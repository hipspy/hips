# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path
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
    >>> meta = HipsTileMeta(order=6, ipix=30889, file_format='fits')
    >>> url = 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.fits'
    >>> tile = HipsTile.fetch(meta, url)
    >>> tile.data
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

    def __eq__(self, other: 'HipsTile') -> bool:
        return (
            self.meta == other.meta and
            (self.data == other.data).all()
            # Note: we're not checking FITS header here,
            # because it can change a bit on write / read.
        )

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
            hdu_list = fits.open(raw_image)
            data = hdu_list[0].data
            header = hdu_list[0].header
            return cls(meta, data, header)
        else:
            data = np.array(Image.open(raw_image))
            return cls(meta, data)

    @classmethod
    def read(cls, meta: HipsTileMeta, filename: str = None) -> 'HipsTile':
        """Read HiPS tile data from a directory and load into memory (`HipsTile`).

        Parameters
        ----------
        meta : `HipsTileMeta`
            Metadata of HiPS tile
        filename : `str`
            File path to store a HiPS tile
        """
        path = Path(filename) if filename else meta.full_path

        if meta.file_format == 'fits':
            hdu_list = fits.open(str(path))
            data = hdu_list[0].data
            header = hdu_list[0].header
            return cls(meta, data, header)
        else:
            image = Image.open(str(path))
            data = np.array(image)
            return cls(meta, data)

    def write(self, filename: str = None) -> None:
        """Write HiPS tile by a given filename.

        Parameters
        ----------
        filename : `str`
            Name of the file
        """
        path = Path(filename) if filename else self.meta.full_path

        if self.meta.file_format == 'fits':
            hdu = fits.PrimaryHDU(self.data, header=self.header)
            hdu.writeto(str(path))
        else:
            image = Image.fromarray(self.data)
            image.save(str(path))
