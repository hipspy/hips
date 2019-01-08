# Licensed under a 3-clause BSD style license - see LICENSE.rst
import logging
from pathlib import Path
import numpy as np
from astropy_healpix import healpy as hp
from ..tiles import HipsTile, HipsTileMeta, HipsSurveyProperties
from ..utils.healpix import hips_tile_healpix_ipix_array

__all__ = ["healpix_to_hips_tile", "healpix_to_hips"]

log = logging.getLogger(__name__)


def healpix_to_hips_tile(
    hpx_data: np.ndarray, tile_width: int, tile_idx: int, file_format: str, frame: str
) -> HipsTile:
    """Create single HiPS tile from HEALPix data.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
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
    data = hpx_data[ipix]

    # np.rot90 returns a rotated view so we make a copy here
    # because the view information is lost on fits io
    data = np.rot90(data).copy()

    hpx_nside = hp.npix2nside(hpx_data.size / tile_width ** 2)
    hpx_order = int(np.log2(hpx_nside))

    meta = HipsTileMeta(
        order=hpx_order,
        ipix=tile_idx,
        file_format=file_format,
        frame=frame,
        width=tile_width,
    )

    return HipsTile.from_numpy(meta=meta, data=data)


def healpix_to_hips(hpx_data, tile_width, base_path, file_format, frame):
    """Convert HEALPix image to HiPS.

    This function writes the HiPS to disk.
    If you don't want that, use `healpix_to_hips_tile` directly.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
    tile_width : int
        Width of the hips tiles.
    base_path : str or `~pathlib.Path`
        Base path.
    file_format : {'fits', 'jpg', 'png'}
        HiPS tile file format
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame
    """
    base_path = Path(base_path)
    base_path.mkdir(exist_ok=True, parents=True)

    path = base_path / "properties"
    log.info(f"Writing {path}")
    HipsSurveyProperties(
        {
            "hips_tile_format": file_format,
            "hips_tile_width": tile_width,
            "hips_frame": frame,
        }
    ).write(path)

    n_tiles = hpx_data.size // tile_width ** 2

    for tile_idx in range(n_tiles):
        tile = healpix_to_hips_tile(
            hpx_data=hpx_data,
            tile_width=tile_width,
            tile_idx=tile_idx,
            file_format=file_format,
            frame=frame,
        )

        path = base_path / tile.meta.tile_default_path
        log.info(f"Writing {path}")
        path.parent.mkdir(exist_ok=True, parents=True)
        tile.write(path)
