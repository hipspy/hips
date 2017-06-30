# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from io import BytesIO
from pathlib import Path

import healpy as hp
import numpy as np
from PIL import Image
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.io.fits.header import Header

from ..utils import boundaries

__all__ = [
    'HipsTile',
    'HipsTileMeta'
]

__doctest_skip__ = ['HipsTile']


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
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame
    tile_width : `int`
        Tile width (in pixels)

    Examples
    --------
    >>> from hips.tiles import HipsTileMeta
    >>> tile_meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs', tile_width=512)
    >>> tile_meta.skycoord_corners
    <SkyCoord (ICRS): (ra, dec) in deg
    [( 264.375, -24.62431835), ( 258.75 , -30.        ),
    ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """

    def __init__(self, order: int, ipix: int, file_format: str, frame: str = 'galactic', tile_width: int = 512) -> None:
        self.order = order
        self.ipix = ipix
        self.file_format = file_format
        self.frame = frame
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
        """Default path for tile storage (`~pathlib.Path`)."""
        return Path('hips', 'tiles', 'tests', 'data')

    @property
    def filename(self) -> str:
        """Filename for HiPS tile (`str`)."""
        return ''.join(['Npix', str(self.ipix), '.', self.file_format])

    @property
    def full_path(self) -> Path:
        """Full path (folder and filename) (`~pathlib.Path`)"""
        return self.path / self.filename

    @property
    def nside(self) -> int:
        """nside of the HEALPix map"""
        return hp.order2nside(self.order)

    @property
    def dst(self) -> np.ndarray:
        """Destination array for projective transform"""
        return np.array(
            [[self.tile_width - 1, 0],
             [self.tile_width - 1, self.tile_width - 1],
             [0, self.tile_width - 1],
             [0, 0]])

    @property
    def skycoord_corners(self) -> SkyCoord:
        """Corner values for a HiPS tile"""
        theta, phi = boundaries(self.nside, self.ipix)
        return SkyCoord(phi, np.pi / 2 - theta, unit='radian', frame=self.frame)


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
    >>> from hips.tiles import HipsTile, HipsTileMeta
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
            with fits.open(str(path)) as hdu_list:
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
