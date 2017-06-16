# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from .description import HipsDescription
from astropy.io import fits
from pathlib import Path
from io import BytesIO
from PIL import Image
import numpy as np
import urllib.request

__all__ = [
    'HipsTile',
]


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading,
    and stroing a HiPS tile. It also contains a few
    getters and setters around most commonly used
    HiPS tile attributes.

    Parameters
    ----------
    hips_description : `HipsDescription`
        Class HipsDescription contains HiPS properties
    order : `int`
        Order of the HiPS
    ipix : `int`
        HEALPix pixel number
    format : `format`
        Format of HiPS tile
    data : `list`
        Pixel values of HiPS tile

    Examples
    --------
    ::

        >>> from hips.tiles import HipsDescription
        >>> from astropy.utils.data import get_pkg_data_filename
        >>> filename = get_pkg_data_filename('tests/data/properties.txt')
        >>> hips_description = HipsDescription.read(filename)
        >>> hips_tile = HipsTile(hips_description, 6, 24185, 'fits')
        >>> tile.read()
        >>> tile.data
        [[3617 3304 4196 ..., 4545 4800 5701]
         [3638 3288 3934 ..., 4448 5029 4951]
         [3116 3653 3412 ..., 5282 4406 4967]
         ...,
         [3890 3463 3448 ..., 5980 6902 6543]
         [4845 4065 3821 ..., 6928 6557 7197]
         [4261 3581 3842 ..., 7095 6390 6191]]
    """

    def __init__(self, hips_description: HipsDescription, order: int, ipix: int, format: str, data: list=None) -> None:
        self.hips_description = hips_description
        self.order = order
        self.ipix = ipix
        self.format = format
        self.data = data

    @staticmethod
    def _directory(ipix: int) -> int:
        """Directory of the HiPS tile (`int`)."""
        return np.around(ipix, decimals=-(len(str(ipix)) - 1))

    @property
    def base_url(self) -> str:
        """HiPS tile base url (`str`)."""
        return self._base_url

    @property
    def path(self) -> Path:
        """Default path for tile storage (`Path`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @property
    def tile_url(self) -> str:
        """HiPS tile url (`str`)."""
        return ''.join([self._base_url, '/Norder', str(self.order), '/Dir', str(self._directory(self.ipix)), '/Npix', str(self.ipix), '.', self.format])

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        """Set the HiPS tile base url (`None`)."""
        self._base_url = base_url

    def fetch(self) -> None:
        """Fetch HiPS tile and load into memory (`None`)."""
        raw_image = BytesIO(urllib.request.urlopen(self.tile_url).read())
        if self.format is 'fits':
            hdulist = fits.open(raw_image)
            self.data = np.array(hdulist[0].data)
            self.header = hdulist[0].header
        else:
            self.data = np.array(Image.open(raw_image))

    def read(self) -> None:
        """Read HiPS tile data from a directory and load into memory (`None`)."""
        path = self.path.joinpath(''.join(['Npix', str(self.ipix), '.', self.format]))
        with path.open('rb') as rf:
            raw_img = BytesIO(rf.read())
            if self.format is 'fits':
                hdulist = fits.open(raw_img)
                self.data = np.array(hdulist[0].data)
                self.header = hdulist[0].header
            else:
                self.data = np.array(Image.open(raw_img))

    def store(self, filename: str) -> None:
        """Store HiPS tile by a given filename (`None`).

        Parameters
        ----------
        filename : `str`
            Name of the file
        """
        path = self.path.joinpath(''.join([filename, '.', self.format]))
        print(path)
        with path.open('w') as wf:
            if self.format is 'fits':
                hdu = fits.PrimaryHDU(self.data, header=self.header)
                hdulist = fits.HDUList([hdu])
                hdulist.writeto(wf)
                hdulist.close()
            else:
                Image.fromarray(self.data).save(wf)
