# Licensed under a 3-clause BSD style license - see LICENSE.rst
import warnings
import urllib.request
from io import BytesIO
from pathlib import Path
import healpy as hp
import numpy as np
from PIL import Image
from astropy.utils.exceptions import AstropyWarning
from astropy.io.fits.verify import VerifyWarning
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.io.fits.header import Header
from ..utils import boundaries
from .io import tile_default_url

__all__ = [
    'HipsTileMeta',
    'HipsTile',
]

__doctest_skip__ = ['HipsTile']


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
    >>> tile_meta.skycoord_corners
    <SkyCoord (ICRS): (ra, dec) in deg
    [( 264.375, -24.62431835), ( 258.75 , -30.        ),
    ( 264.375, -35.68533471), ( 270.   , -30.        )]>
    """

    def __init__(self, order: int, ipix: int, file_format: str, frame: str = 'icrs') -> None:
        self.order = order
        self.ipix = ipix
        self.file_format = file_format
        self.frame = frame

    def __eq__(self, other: 'HipsTileMeta') -> bool:
        return (
            self.order == other.order and
            self.ipix == other.ipix and
            self.file_format == other.file_format
        )

    @property
    def nside(self) -> int:
        """HEALPix nside (int)"""
        return hp.order2nside(self.order)

    @property
    def skycoord_corners(self) -> SkyCoord:
        """Corner sky coordinates (`~astropy.coordinates.SkyCoord`)"""
        theta, phi = boundaries(self.nside, self.ipix)
        return SkyCoord(phi, np.pi / 2 - theta, unit='radian', frame=self.frame)

    @property
    def tile_default_url(self) -> str:
        """Tile relative URL in the default scheme."""
        return tile_default_url(self.order, self.ipix, self.file_format)


class HipsTile:
    """HiPS tile container.

    This class provides methods for fetching, reading, and writing a HiPS tile.

    Parameters
    ----------
    meta : `~hips.HipsTileMeta`
        Metadata of HiPS tile
    data : `~numpy.ndarray`
        Data containing HiPS tile

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
        """Fetch HiPS tile and load into memory (`~hips.HipsTile`).

        Parameters
        ----------
        meta : `~hips.HipsTileMeta`
            Metadata of HiPS tile
        url : str
            URL containing HiPS tile
        """
        with urllib.request.urlopen(url) as response:
            raw_data = BytesIO(response.read())

        return cls._from_raw_data(meta, raw_data)

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
        path = Path(filename)

        with path.open(mode='rb') as fh:
            raw_data = BytesIO(fh.read())

        return cls._from_raw_data(meta, raw_data)

    @classmethod
    def _from_raw_data(cls, meta: HipsTileMeta, raw_data: BytesIO) -> 'HipsTile':
        if meta.file_format == 'fits':
            # At the moment CDS is serving FITS tiles in non-standard FITS files
            # https://github.com/hipspy/hips/issues/42
            # The following warnings handling is supposed to suppress these warnings
            # (but hopefully still surface other issues in a useful way).
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', AstropyWarning)
                warnings.simplefilter('ignore', VerifyWarning)
                with fits.open(raw_data) as hdu_list:
                    data = hdu_list[0].data
                    header = hdu_list[0].header
            return cls(meta, data, header)
        elif meta.file_format in {'jpg', 'png'}:
            with Image.open(raw_data) as image:
                data = np.array(image)
            return cls(meta, data)
        else:
            raise ValueError(f'Tile file format not supported: {meta.file_format}. '
                             'Supported formats: fits, jpg, png')

    def write(self, filename: str) -> None:
        """Write to file.

        Parameters
        ----------
        filename : str
            Filename
        """
        path = Path(filename)
        file_format = self.meta.file_format

        if file_format == 'fits':
            # See comment above when reading FITS on why we catch warnings here
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', VerifyWarning)
                hdu = fits.PrimaryHDU(self.data, header=self.header)
                hdu.writeto(str(path))
        elif file_format in {'jpg', 'png'}:
            image = Image.fromarray(self.data)
            image.save(str(path))
        else:
            raise ValueError(f'Tile file format not supported: {file_format}. '
                             'Supported formats: fits, jpg, png')  # pragma: no cover
