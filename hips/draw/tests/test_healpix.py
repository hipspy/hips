# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from numpy.testing import assert_equal
from astropy_healpix import healpy as hp
from ..healpix import healpix_to_hips_tile


def make_hpx_data(file_format):
    npix = hp.nside2npix(4)
    data = np.arange(npix, dtype="uint8")

    if file_format == "fits":
        return data
    elif file_format == "jpg":
        return np.moveaxis([data, data + 1, data + 2], 0, -1)
    elif file_format == "png":
        return np.moveaxis([data, data + 1, data + 2, data + 3], 0, -1)
    else:
        raise ValueError()


def test_healpix_to_hips_tile_fits():
    hpx_data = make_hpx_data("fits")

    tile = healpix_to_hips_tile(
        hpx_data=hpx_data, tile_width=2, tile_idx=0, file_format="fits"
    )

    assert tile.meta.order == 1
    assert tile.meta.ipix == 0
    assert tile.meta.file_format == "fits"
    assert tile.meta.frame == "icrs"
    assert tile.meta.width == 2

    assert tile.data.dtype == np.uint8
    assert tile.data.shape == (2, 2)
    assert_equal(tile.data, [[1, 3], [0, 2]])


def test_healpix_to_hips_tile_jpg():
    hpx_data = make_hpx_data("jpg")

    tile = healpix_to_hips_tile(
        hpx_data=hpx_data, tile_width=2, tile_idx=0, file_format="jpg"
    )

    assert tile.meta.order == 1
    assert tile.meta.ipix == 0
    assert tile.meta.file_format == "jpg"
    assert tile.meta.width == 2

    assert tile.data.dtype == np.uint8
    assert tile.data.shape == (2, 2, 3)

    # Note: we don't assert on the tile data for JPEG,
    # because JPEG encoding noise is large and results
    # can vary depending on JPEG lib and machine used.


def test_healpix_to_hips_tile_png():
    hpx_data = make_hpx_data("png")

    tile = healpix_to_hips_tile(
        hpx_data=hpx_data, tile_width=2, tile_idx=0, file_format="png"
    )

    assert tile.meta.order == 1
    assert tile.meta.ipix == 0
    assert tile.meta.file_format == "png"
    assert tile.meta.frame == "icrs"
    assert tile.meta.width == 2

    assert tile.data.dtype == np.uint8
    assert tile.data.shape == (2, 2, 4)
    assert_equal(tile.data[..., 0], [[1, 3], [0, 2]])
