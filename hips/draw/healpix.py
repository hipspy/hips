# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import healpy as hp
from pathlib import Path
from astropy.io import fits

from ..tiles import HipsTile, HipsTileMeta, HipsSurveyProperties
from ..utils.healpix import hips_tile_healpix_ipix_array

__all__ = [
    'healpix_to_hips_tile',
    'healpix_to_hips',
    'hips_to_healpix_array',
    'hips_to_healpix'
]


def healpix_to_hips_tile(hpx_data, tile_width, tile_idx, file_format) -> HipsTile:
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


def healpix_to_hips(hpx_data, tile_width, base_path, file_format='fits'):
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

def hips_to_healpix_array(order: int):
    """Create array giving mapping between:

    HEALPix index ==> XY index
    XY index ==> HEALPix index

    Parameters
    ----------
    order : int
        Order of HEALPix array.
    """
    def fill_array(npix, nsize, pos):
        size = nsize ** 2
        npix_idx = [[0 for i in range(size // 4)] for j in range(4)]
        nb = [0 for i in range(4)]

        for i in range(size):
            if (i % nsize) < (nsize // 2):
                dg = 0
            else:
                dg = 1

            if i < (size / 2):
                bh = 1
            else:
                bh = 0

            quad = (dg << 1) | bh

            if pos is None:
                j = i
            else:
                j = pos[i]

            npix[j] = npix[j] << 2 | quad
            npix_idx[quad][nb[quad]] = j
            nb[quad] += 1

        if size > 4:
            for i in range(4):
                fill_array(npix, nsize // 2, npix_idx[i])

    if order == 0:
        xy_to_healpix = healpix_to_xy = [0]
        return

    nsize = 2 ** order
    xy_to_healpix = [0 for i in range(nsize ** 2)]
    healpix_to_xy = [0 for i in range(nsize ** 2)]

    fill_array(xy_to_healpix, nsize, None)

    for i in range(len(xy_to_healpix)):
        healpix_to_xy[xy_to_healpix[i]] = i

    return healpix_to_xy, xy_to_healpix

def hips_to_healpix(hips_url: str, npix: int, hpx_output_path: str):
    """Given a HiPS survey, generate a HEALPix map.

    Parameters
    ----------
    hips_url : str
        URL of HiPS survey.
    npix : int
        HEALPix pixel number.
    hpx_output_path : str
        HEALPix output path.
    """
    # Query the HiPS survey properties.
    hips_properties = HipsSurveyProperties.fetch(hips_url + "/properties")

    hips_tile_width = hips_properties.tile_width
    order = int(np.log2(hips_tile_width))

    healpix_to_xy, xy_to_healpix = hips_to_healpix_array(order)

    healpix_map = np.empty(hp.nside2npix(2 ** 12), dtype=np.double) # 2 ** 12?
    healpix_map[:] = hp.pixelfunc.UNSEEN

    for ipix in range(npix):
        try:
            tile = fits.open(f'{hips_url}/Norder3/Dir0/Npix{ipix}.fits')
        except:
            continue

        # BSCALE and BZERO.
        bzero = 0
        bscale = 1
        has_blank_value = False

        if 'BZERO' in tile[0].header:
            bzero = tile[0].header['BZERO']
        if 'BSCALE' in tile[0].header:
            bscale = tile[0].header['BSCALE']
        if 'BLANK' in tile[0].header:
            has_blank_value = True
            blank_value_scaled = bscale * tile[0].header['BLANK'] + bzero

        for k in range(hips_tile_width ** 2):
            x = k % hips_tile_width
            y = k // hips_tile_width
            healpix_index = xy_to_healpix[k]
            pixel_value = tile[0].data[y][x]

            if has_blank_value and np.fabs(pixel_value - blank_value_scaled) < 1e-6:
                pixel_value = hp.pixelfunc.UNSEEN

            healpix_map[ipix * hips_tile_width * hips_tile_width + healpix_index] = pixel_value

    hp.write_map(str(hpx_output_path), healpix_map, coord='C', nest=True)
