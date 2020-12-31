# Licensed under a 3-clause BSD style license - see LICENSE.rst
from typing import List
import logging
import numpy as np
from ..tiles import HipsTile, HipsTileMeta
from ..utils.healpix import hips_tile_healpix_ipix_array

__all__ = ["healpix_to_hips_tile", "healpix_to_hips_tiles"]

log = logging.getLogger(__name__)


def healpix_to_hips_tile(
    hpx_data: np.ndarray,
    hips_order: int,
    tile_width: int,
    tile_idx: int,
    file_format: str,
    frame: str = "icrs",
) -> HipsTile:
    """Create single HiPS tile from HEALPix data.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
    hips_order : int
        HEALPix order for the HiPS tiles
    tile_width : int
        Width of the hips tile.
    tile_idx : int
        Index of the hips tile.
    file_format : {'fits', 'jpg', 'png'}
        HiPS tile file format
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame

    Returns
    -------
    hips_tile : `HipsTile`
        Hips tile object.
    """
    shift_order = int(np.log2(tile_width))
    hpx_ipix = hips_tile_healpix_ipix_array(shift_order=shift_order)

    offset_ipix = tile_idx * tile_width ** 2
    ipix = hpx_ipix + offset_ipix

    hpx_data = np.asarray(hpx_data)
    if file_format == "fits":
        if hpx_data.ndim != 1:
            raise ValueError(
                f"Invalid hpx_data.ndim = {hpx_data.ndim}."
                " Must be ndim = 1 for file_format='fits'."
            )
        data = hpx_data[ipix]
    elif file_format == "jpg":
        if hpx_data.ndim != 2 or hpx_data.shape[1] != 3:
            raise ValueError(
                f"Invalid hpx_data.shape = {hpx_data.shape}."
                " Must be shape = (npix, 3) to represent RGB color images."
            )
        data = hpx_data[ipix, :]
    elif file_format == "png":
        if hpx_data.ndim != 2 or hpx_data.shape[1] != 4:
            raise ValueError(
                f"Invalid hpx_data.shape = {hpx_data.shape}."
                " Must be shape = (npix, 4) to represent RGBA color images."
            )
        data = hpx_data[ipix, :]
    else:
        raise ValueError(f"Invalid file_format: {file_format!r}")

    # np.rot90 returns a rotated view so we make a copy here
    # because the view information is lost on fits io
    data = np.rot90(data).copy()

    meta = HipsTileMeta(
        order=hips_order,
        ipix=tile_idx,
        file_format=file_format,
        frame=frame,
        width=tile_width,
    )

    return HipsTile.from_numpy(meta=meta, data=data)


def healpix_to_hips_tiles(
    hpx_data: np.ndarray,
    hips_order: int,
    tile_width: int,
    file_format: str,
    frame: str = "icrs",
) -> List[HipsTile]:
    """Convert HEALPix image to HiPS tiles,

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        HEALPix data stored in the "nested" scheme.
    hips_order : int
        HEALPix order for the HiPS tiles
    tile_width : int
        Width of the hips tiles.
    file_format : {'fits', 'jpg', 'png'}
        HiPS tile file format
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame

    Returns
    -------
    tiles : Generator of HipsTile
        HiPS tiles
    """
    n_tiles = 12 * (2 ** hips_order)

    for tile_idx in range(n_tiles):
        yield healpix_to_hips_tile(
            hpx_data=hpx_data,
            hips_order=hips_order,
            tile_width=tile_width,
            tile_idx=tile_idx,
            file_format=file_format,
            frame=frame,
        )
