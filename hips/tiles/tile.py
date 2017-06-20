# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .description import HipsDescription
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

    This class provides methods for fetching, reading,
    and writing a HiPS tile. It also contains a few
    getters and setters around frequently used
    HiPS tile attributes.

    Parameters
    ----------
    hips_description : `HipsDescription`
        Class HipsDescription contains HiPS properties
    order : `int`
        Order of the HiPS tile
    ipix : `int`
        HEALPix pixel number
    format : `format`
        Format of HiPS tile
    data : `numpy.ndarray`
        Pixel values of HiPS tile
    tile_width : `int`
        Width of HiPS tile
    base_url : `str`
        Base URL of HiPS tile

    Examples
    --------
    ::

        >>> import urllib.request
        >>> from hips.tiles import HipsDescription
        >>> from astropy.tests.helper import remote_data
        >>> text = urllib.request.urlopen('https://raw.githubusercontent.com/hipspy/hips/master/hips/tiles/tests/data/properties.txt').read() # doctest: +REMOTE_DATA
        >>> hips_description = HipsDescription.parse(str(text))
        >>> hips_tile = HipsTile(hips_description=hips_description, order=6, ipix=30889, format='fits', tile_width=512)
        >>> hips_tile.read()
        >>> hips_tile.data
        array([[0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               [0, 0, 0, ..., 0, 0, 0],
               ...,
               [0, 0, 0, ..., 1, 0, 0],
               [0, 0, 0, ..., 1, 0, 1],
               [0, 0, 0, ..., 1, 0, 1]], dtype=int16)
        """

    def __init__(self, hips_description: HipsDescription, order: int, ipix: int, format: str,
                 data: np.ndarray=None, tile_width: int=512, base_url: str=None) -> None:
        self.hips_description = hips_description
        self.order = order
        self.ipix = ipix
        self.tile_width = tile_width
        self.format = format
        self.data = data
        self.base_url = base_url

    @staticmethod
    def _directory(ipix: int) -> int:
        """Directory of the HiPS tile (`int`)."""
        return np.around(ipix, decimals=-(len(str(ipix)) - 1))

    @property
    def path(self) -> Path:
        """Default path for tile storage (`Path`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @property
    def tile_url(self) -> str:
        """HiPS tile url (`str`)."""
        return ''.join([self.base_url, '/Norder', str(self.order), '/Dir',
               str(self._directory(self.ipix)), '/Npix', str(self.ipix), '.', self.format])

    def fetch(self) -> None:
        """Fetch HiPS tile and load into memory (`None`)."""
        raw_image = BytesIO(urllib.request.urlopen(self.tile_url).read())
        if self.format == 'fits':
            hdulist = fits.open(raw_image)
            self.data = np.array(hdulist[0].data)
            self.header = hdulist[0].header
        else:
            self.data = np.array(Image.open(raw_image))

    def read(self) -> None:
        """Read HiPS tile data from a directory and load into memory (`None`)."""
        path = self.path / (''.join(['Npix', str(self.ipix), '.', self.format]))
        if self.format == 'fits':
            hdulist = fits.open(path)
            self.data = np.array(hdulist[0].data)
            self.header = hdulist[0].header
        else:
            self.data = np.array(Image.open(str(path)))

    def write(self, filename: str) -> None:
        """Write HiPS tile by a given filename (`None`).

        Parameters
        ----------
        filename : `str`
            Name of the file
        """
        path = self.path / (''.join([filename, '.', self.format]))
        if self.format == 'fits':
            hdu = fits.PrimaryHDU(self.data, header=self.header)
            hdulist = fits.HDUList([hdu])
            hdulist.writeto(path)
            hdulist.close()
        else:
            Image.fromarray(self.data).save(str(path))
