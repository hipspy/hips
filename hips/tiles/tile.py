# Licensed under a 3-clause BSD style license - see LICENSE.rst
import warnings
import urllib.request
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
from astropy.utils.exceptions import AstropyWarning
from astropy.io.fits.verify import VerifyWarning
from astropy.coordinates import SkyCoord
from astropy.io import fits
from ..utils import healpix_pixel_corners
from .io import tile_default_url, tile_default_path
from typing import List

__all__ = [
    'HipsTileMeta',
    'HipsTile',
]

__doctest_skip__ = [
    'HipsTile',
]


class HipsTileMeta:
    """HiPS tile metadata.

    Parameters
    ----------
    order : int
        HEALPix order
    ipix : int
        HEALPix pixel number
    file_format : {'fits', 'jpg', 'png'}
        File format
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame

    Examples
    --------
    >>> from hips.tiles import HipsTileMeta
    >>> tile_meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs')
    >>> tile_meta
    HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs')
    >>> tile_meta.skycoord_corners
    <SkyCoord (ICRS): (ra, dec) in deg
    [( 264.375, -24.62431835), ( 258.75 , -30.        ),
    ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    >>> tile_meta.tile_default_url
    'Norder3/Dir0/Npix450.fits'
    >>> tile_meta.tile_default_path
    PosixPath('Norder3/Dir0/Npix450.fits')
    """

    def __init__(self, order: int, ipix: int, file_format: str, frame: str = 'icrs') -> None:
        self.order = order
        self.ipix = ipix
        self.file_format = file_format
        self.frame = frame

    def __repr__(self):
        return (
            f'HipsTileMeta(order={self.order}, ipix={self.ipix}, '
            f'file_format={self.file_format!r}, frame={self.frame!r})'
        )

    def __eq__(self, other: 'HipsTileMeta') -> bool:
        return (
            self.order == other.order and
            self.ipix == other.ipix and
            self.file_format == other.file_format
        )

    @property
    def skycoord_corners(self) -> SkyCoord:
        """Tile corner sky coordinates (`~astropy.coordinates.SkyCoord`)."""
        return healpix_pixel_corners(self.order, self.ipix, self.frame)

    @property
    def tile_default_url(self) -> str:
        """Tile relative URL (str)."""
        return tile_default_url(self.order, self.ipix, self.file_format)

    @property
    def tile_default_path(self) -> str:
        """Tile relative filename path (`~pathlib.Path`)."""
        return tile_default_path(self.order, self.ipix, self.file_format)


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading, and writing a HiPS tile.

    Parameters
    ----------
    meta : `~hips.HipsTileMeta`
        Metadata of HiPS tile
    raw_data : `bytes`
        Raw data (copy of bytes from file)

    Examples
    --------

    Fetch a HiPS tile:

    >>> from hips.tiles import HipsTile, HipsTileMeta
    >>> meta = HipsTileMeta(order=6, ipix=30889, file_format='fits')
    >>> url = 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.fits'
    >>> tile = HipsTile.fetch(meta, url)

    The tile pixel data is available as a Numpy array:

    >>> type(tile.data)
    numpy.ndarray
    >>> tile.data.shape
    (512, 512)
    >>> tile.data.dtype.name
    int16
    """

    def __init__(self, meta: HipsTileMeta, raw_data: BytesIO) -> None:
        self.meta = meta
        self.raw_data = raw_data

    def __eq__(self, other: 'HipsTile') -> bool:
        return (
            self.meta == other.meta and
            self.raw_data == other.raw_data
        )

    @classmethod
    def from_numpy(cls, meta: HipsTileMeta, data: np.ndarray) -> 'HipsTile':
        """Create a tile from given pixel data.

        Parameters
        ----------
        meta : `~hips.HipsTileMeta`
            Metadata of HiPS tile
        data : `~numpy.ndarray`
            Tile pixel data

        Returns
        -------
        tile : `~hips.HipsTile`
            HiPS tile object in the format requested in ``meta``.
        """
        fmt = meta.file_format
        bio = BytesIO()

        if fmt == 'fits':
            hdu = fits.PrimaryHDU(data)
            hdu.writeto(bio)
        elif fmt == 'jpg':
            image = Image.fromarray(data)
            image.save(bio, format='jpeg')
        elif fmt == 'png':
            image = Image.fromarray(data)
            image.save(bio, format='png')
        else:
            raise ValueError(f'Tile file format not supported: {fmt}. '
                             'Supported formats: fits, jpg, png')

        bio.seek(0)
        raw_data = bio.read()

        return cls(meta, raw_data)

    @property
    def children(self) -> List['HipsTile']:
        """Create four children tiles from parent tile."""
        children_tiles = []
        w = self.data.shape[0] // 2
        child_data = [
            self.data[0: w, 0: w],
            self.data[0: w, w: w * 2],
            self.data[w: w * 2, 0: w],
            self.data[w: w * 2, w: w * 2]
        ]

        for index, data in enumerate(child_data):
            meta = HipsTileMeta(
                self.meta.order + 1,
                self.meta.ipix * 4 + index,
                self.meta.file_format,
                self.meta.frame
            )
            children_tiles.append(self.from_numpy(meta, data))

        return children_tiles

    @property
    def data(self) -> np.ndarray:
        """Tile pixel data (`~numpy.ndarray`)."""
        fmt = self.meta.file_format
        bio = BytesIO(self.raw_data)

        if fmt == 'fits':
            # At the moment CDS is serving FITS tiles in non-standard FITS files
            # https://github.com/hipspy/hips/issues/42
            # The following warnings handling is supposed to suppress these warnings
            # (but hopefully still surface other issues in a useful way).
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', AstropyWarning)
                warnings.simplefilter('ignore', VerifyWarning)
                with fits.open(bio) as hdu_list:
                    data = hdu_list[0].data
                    # header = hdu_list[0].header
        elif fmt in {'jpg', 'png'}:
            with Image.open(bio) as image:
                data = np.array(image)
        else:
            raise ValueError(f'Tile file format not supported: {fmt}. '
                             'Supported formats: fits, jpg, png')

        return data

    @classmethod
    def read(cls, meta: HipsTileMeta, filename: str = None) -> 'HipsTile':
        """Read HiPS tile data from a directory and load into memory (`~hips.HipsTile`).

        Parameters
        ----------
        meta : `~hips.HipsTileMeta`
            Metadata of HiPS tile
        filename : str
            Filename
        """
        raw_data = Path(filename).read_bytes()
        return cls(meta, raw_data)

    @classmethod
    def fetch(cls, meta: HipsTileMeta, url: str) -> 'HipsTile':
        """Fetch HiPS tile and load into memory (`~hips.HipsTile`).

        Parameters
        ----------
        meta : `~hips.HipsTileMeta`
            Metadata of HiPS tile
        url : str
            URL containing HiPS tile
        """
        with urllib.request.urlopen(url) as response:
            raw_data = response.read()

        return cls(meta, raw_data)

    def write(self, filename: str) -> None:
        """Write to file.

        Parameters
        ----------
        filename : str
            Filename
        """
        Path(filename).write_bytes(self.raw_data)
