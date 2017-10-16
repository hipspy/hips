# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""HEALPix and HiPS utility functions."""
from functools import lru_cache
import numpy as np
from astropy_healpix import HEALPix
from astropy_healpix.core import level_to_nside
from astropy.coordinates import SkyCoord, Angle, ICRS, Galactic, BaseCoordinateFrame
from .wcs import WCSGeometry

__all__ = [
    'healpix_order_to_npix',
    'hips_order_for_pixel_resolution',
    'healpix_pixel_corners',

    'healpix_pixels_in_sky_image',
    'hips_tile_healpix_ipix_array',
]

__doctest_skip__ = [
    'healpix_pixel_corners',
    'healpix_pixels_in_sky_image',
]


def healpix_order_to_npix(order: int) -> int:
    """HEALPix order to npix."""
    return HEALPix(nside=2 ** order, order='nested').npix


def healpix_pixel_corners(order: int, ipix: int, frame: str) -> SkyCoord:
    """Returns an array containing the angle (theta and phi) in radians.

    This function calls `healpy.boundaries` to compute the four corners of a HiPS tile.

    It's not documented, but apparently the order of the corners is always as follows:

    1. North (N)
    2. West (W)
    3. South (S)
    4. East (E)

    Parameters
    ----------
    order : int
        HEALPix ``order`` parameter
    ipix : int
        HEALPix pixel index
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame

    Returns
    -------
    corners : `~astropy.coordinates.SkyCoord`
        Sky coordinates (array of length 4).
    """
    frame = make_frame(frame)
    hp = HEALPix(nside=2 ** order, order='nested', frame=frame)
    return hp.boundaries_skycoord(ipix, step=1)[0]


def healpix_pixels_in_sky_image(geometry: WCSGeometry, order: int, healpix_frame: str) -> np.ndarray:
    """Compute HEALPix pixels within a given sky image.

    The algorithm used is as follows:

    * compute the sky position of every pixel in the image using the given ``geometry``
    * compute the HEALPix pixel index for every pixel using `healpy.pixelfunc.ang2pix`
    * compute the unique set of HEALPix pixel values that occur via `numpy.unique`

    Parameters
    ----------
    geometry : `WCSGeometry`
        Sky image WCS geometry
    order : int
        HEALPix order
    healpix_frame : {'icrs', 'galactic', 'ecliptic'}
        HEALPix coordinate frame

    Returns
    -------
    pixels : `numpy.ndarray`
        HEALPix pixel numbers

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> from hips import WCSGeometry
    >>> from hips.utils.healpix import healpix_pixels_in_sky_image
    >>> skycoord = SkyCoord(10, 20, unit="deg")
    >>> geometry = WCSGeometry.create(
    ...     skydir=skycoord, shape=(10, 20),
    ...     coordsys='CEL', projection='AIT',
    ...     cdelt=1.0, crpix=(1., 1.),
    ... )
    >>> healpix_pixels_in_sky_image(geometry, order=3, healpix_frame='galactic')
    array([321, 611, 614, 615, 617, 618, 619, 620, 621, 622])
    """
    hp = HEALPix(nside=2 ** order, order='nested', frame=healpix_frame)
    skycoord = geometry.pixel_skycoords  # .transform_to(healpix_frame)
    ipix = hp.skycoord_to_healpix(skycoord)
    return np.unique(ipix)


def hips_order_for_pixel_resolution(tile_width: int, resolution: float) -> int:
    """Find the HiPS tile order that will result in a given pixel resolution.

    Parameters
    ----------
    tile_width : int
        HiPS tile width
    resolution : float
        Sky image angular resolution (pixel size in degrees)

    Returns
    -------
    candidate_tile_order : int
        Best HiPS tile order
    """
    resolution = Angle(resolution, unit='deg')
    nside = pixel_resolution_to_nside(resolution * tile_width, round='up')
    return nside_to_level(nside)


@lru_cache(maxsize=None)
def hips_tile_healpix_ipix_array(shift_order: int) -> np.ndarray:
    """

    TODO: write a good description what this is.
    Note that there is already a mention of this in the high-level docs:
    https://github.com/hipspy/hips/blame/71e593ab7e60767be70d9b2b13398016c35db09a/docs/drawing_algo.rst#L103

    Parameters
    ----------
    shift_order : int
        The HiPS tile "shift order", which is related to the tile
        pixel width as follows: ``tile_width = 2 ** shift_order``.
        Supported range of values: 1 to 16

    Returns
    -------
    shift_ipix_array : `~numpy.ndarray`
        2-dimensional array of HEALPix nested order ``ipix`` values
        for the tile pixels. These numbers are relative to the
        HiPS tile HEALPix index, which needs to be added.

    Examples
    --------
    TODO: give examples here, or elsewhere from where this helper is called?
    """
    # Sanity check, prevent users from shooting themselves in the foot here
    # and waste a lot of CPU and memory.
    if not isinstance(shift_order, int):
        raise TypeError('The `shift_order` option must by of type `int`.')
    # Usually tiles have ``shift_order == 9``, i.e. ``tile_width == 512`
    # There's no examples for very high shift order,
    # so the ``shift_oder == 16`` limit (``tile_width == 65536``) here should be OK.
    if shift_order < 1 or shift_order > 16:
        raise ValueError('The `shift_order` must be in the range 1 to 16.')

    if shift_order == 1:
        return np.array([[0, 1], [2, 3]])
    else:
        # Create 4 tiled copies of the parent
        ipix_parent = hips_tile_healpix_ipix_array(shift_order - 1)
        data1 = np.tile(ipix_parent, reps=(2, 2))

        # Add the right offset values to each of the 4 parts
        repeats = 2 ** (shift_order - 1)
        data2 = (repeats ** 2) * np.array([[0, 1], [2, 3]])
        data2 = np.repeat(data2, repeats, axis=0)
        data2 = np.repeat(data2, repeats, axis=1)

        return data1 + data2


# TODO: remove this function and call the one in `astropy_healpix`
# as soon as astropy-healpix v0.3 is released
def pixel_resolution_to_nside(resolution, round='nearest'):
    resolution = Angle(resolution).radian
    pixel_area = resolution * resolution
    npix = 4 * np.pi / pixel_area
    nside = np.sqrt(npix / 12)

    # Now we have to round to the closest ``nside``
    # Since ``nside`` must be a power of two,
    # we first compute the corresponding ``level = log2(nside)`
    # round the level and then go back to nside
    level = np.log2(nside)

    if round == 'up':
        level = np.array(level, dtype=int) + 1
    elif round == 'nearest':
        level = np.array(level + 0.5, dtype=int)
    elif round == 'down':
        level = np.array(level, dtype=int)
    else:
        raise ValueError('Invalid value for round: {!r}'.format(round))

    return level_to_nside(np.clip(level, 0, None))


# TODO: move to astropy-healpix
# Call from above as: HEALPix(nside, order='nested').level
def nside_to_level(nside):
    level = np.log2(nside)
    return np.round(level).astype(int)


# TODO: move to astropy-healpix
# or maybe call this? `astropy.coordinates.frame_transform_graph.lookup_name(frame)`
# See https://github.com/astropy/astropy-healpix/issues/56#issuecomment-336803290
def make_frame(frame):
    if isinstance(frame, BaseCoordinateFrame):
        return frame
    elif isinstance(frame, str):
        if frame == 'icrs':
            return ICRS()
        elif frame == 'galactic':
            return Galactic()
        else:
            raise ValueError(f'Invalid value for frame: {frame!r}')
    else:
        raise TypeError(f'Invalid type for frame: {type(frame)}')
