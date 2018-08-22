# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from pathlib import Path
from typing import Union, List
from astropy.io import fits
from astropy_healpix import healpy as hp
import healpy as hp

from ..tiles import HipsTile, HipsTileMeta, HipsSurveyProperties
from ..utils.healpix import hips_tile_healpix_ipix_array

__all__ = [
    'healpix_to_hips_tile',
    'healpix_to_hips',
    'hips_to_healpix'
]


def healpix_to_hips_tile(hpx_data: np.ndarray, tile_width: int,
                         tile_idx: int, file_format: str) -> HipsTile:
    """Create single hips tile from healpix data given a tile index.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
    tile_width : int
        Width of the hips tile.
    tile_idx : int
        Index of the hips tile.
    file_format : {'fits', 'jpg', 'png'}
        File format to store the hips tile in.

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
        width=tile_width,
        file_format=file_format,
        frame='galactic'
    )

    return HipsTile.from_numpy(meta=meta, data=data)


def healpix_to_hips(hpx_data: np.ndarray, tile_width: int,
                    base_path: Union[str, Path], file_format='fits') -> None:
    """Convert HEALPix image to HiPS.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
    tile_width : int
        Width of the hips tiles.
    base_bath : str or `~pathlib.Path`
        Base path.
    file_format : {'fits', 'jpg', 'png'}
        File format to store the hips in.
    """
    n_tiles = hpx_data.size // tile_width ** 2

    for tile_idx in range(n_tiles):
        tile = healpix_to_hips_tile(hpx_data=hpx_data, tile_width=tile_width,
                                    tile_idx=tile_idx, file_format=file_format)

        filename = Path(base_path) / tile.meta.tile_default_path
        filename.parent.mkdir(exist_ok=True, parents=True)
        tile.write(filename=filename)


    data = {
        'hips_tile_format': file_format,
        'hips_tile_width': tile_width,
        'hips_frame': tile.meta.frame,
    }

    properties = HipsSurveyProperties(data=data)
    properties.write(base_path / 'properties')

def hips_to_healpix(hips_url: str, hips_tiles: List[HipsTile], healpix_pixels: np.ndarray) -> np.ndarray:
    """Given a HiPS survey, generate a HEALPix map.

    Parameters
    ----------
    hips_tiles : List[HipsTile]
        List of HiPS tiles.
    hips_url : str
        URL of HiPS survey.
    healpix_pixels : `~numpy.ndarray`
        HEALPix pixel numbers.

    Returns
    -------
    healpix_map : `~numpy.ndarray`
        HEALPix map.
    """
    # Query the HiPS survey properties.
    hips_properties = HipsSurveyProperties.fetch(hips_url + "/properties")

    hips_tile_width = hips_properties.tile_width
    order = int(np.log2(hips_tile_width))

    # xy_to_healpix = hips_tile_healpix_ipix_array(shift_order=order).flatten()

    healpix_map = np.empty(hp.nside2npix(2 ** 12), dtype=np.double) # 2 ** 12?
    healpix_map[:] = hp.pixelfunc.UNSEEN

    for index, tile in enumerate(hips_tiles):
        has_blank_value = False

        if 'BLANK' in tile.data:
            has_blank_value = True
            blank_value_scaled = bscale * tile[0].header['BLANK'] + bzero

        # healpix_index = xy_to_healpix[index]
        pixel_value = tile.data

        if has_blank_value and np.fabs(pixel_value - blank_value_scaled) < 1e-6:
            pixel_value = hp.pixelfunc.UNSEEN

        healpix_map_range = index * (hips_tile_width ** 2)
        healpix_map[healpix_map_range: healpix_map_range + tile.meta.width] = pixel_value[0]

    return healpix_map
