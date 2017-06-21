# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.io.fits.header import Header
from astropy.io import fits
from pathlib import Path
from io import BytesIO
from PIL import Image
import urllib.request
import numpy as np

__all__ = [
    'HipsTile',
]


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading, and writing a HiPS tile.

    Parameters
    ----------
    format : `str`
        Format of HiPS tile
    data : `int`
        Data containing HiPS tile
    header : `format`
        Header of HiPS tile

    Examples
    --------
    ::

        >>> import urllib.request
        >>> from astropy.tests.helper import remote_data
        >>> text = urllib.request.urlopen('https://raw.githubusercontent.com/hipspy/hips/master/hips/tiles/tests/data/properties.txt').read() # doctest: +REMOTE_DATA
        >>> hips_tile = HipsTile.read('fits', 'Npix30889.fits')
        >>> hips_tile.data
        array([[0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               ...,
               [0, 0, 0, ..., 1, 0, 0],
               [0, 0, 0, ..., 1, 0, 1],
               [0, 0, 0, ..., 1, 0, 1]], dtype=int16)
        """

    def __init__(self, format: str, data: np.ndarray=None, header: Header=None) -> None:
        self.format = format
        self.data = data
        self.header = header

    @property
    def path(self) -> Path:
        """Default path for tile storage (`Path`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @classmethod
    def fetch(cls, format: str, url: str) -> HipsTile:
        """Fetch HiPS tile and load into memory (`HipsTile`).

        Parameters
        ----------
        format : `str`
            Format of HiPS tile
        url : `str`
            URL containing HiPS tile
        """
        raw_image = BytesIO(urllib.request.urlopen(url).read())
        if format == 'fits':
            hdulist = fits.open(raw_image)
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(format, data, header)
        else:
            data = np.array(Image.open(raw_image))
            return cls(format, data)

    @classmethod
    def read(cls, format: str, filename: str) -> 'HipsTile':
        """Read HiPS tile data from a directory and load into memory (`HipsTile`).

        Parameters
        ----------
        format : `str`
            Format of HiPS tile
        filename : `str`
            File name of HiPS tile
        """
        path = Path('hips', 'tiles', 'tests', 'data') / filename
        if format == 'fits':
            hdulist = fits.open(path)
            data = np.array(hdulist[0].data)
            header = hdulist[0].header
            return cls(format, data, header)
        else:
            data = np.array(Image.open(str(path)))
            return cls(format, data)

    def write(self, filename: str) -> None:
        """Write HiPS tile by a given filename (`None`).

        Parameters
        ----------
        filename : `str`
            Name of the file
        """
        path = self.path / filename
        if self.format == 'fits':
            hdu = fits.PrimaryHDU(self.data, header=self.header)
            hdulist = fits.HDUList([hdu])
            hdulist.writeto(path)
            hdulist.close()
        else:
            Image.fromarray(self.data).save(str(path))
