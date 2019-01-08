# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from PIL import Image
from astropy.io import fits
from numpy.testing import assert_allclose, assert_equal
from astropy_healpix import healpy as hp
from ..healpix import healpix_to_hips, healpix_to_hips_tile


def test_healpix_to_hips_tile():
    nside, tile_width = 4, 2
    npix = hp.nside2npix(nside)
    hpx_data = np.arange(npix, dtype="uint8")
    tile = healpix_to_hips_tile(
        hpx_data=hpx_data,
        tile_width=tile_width,
        tile_idx=0,
        file_format="fits",
        frame="galactic",
    )

    assert_equal(tile.data, [[1, 3], [0, 2]])
    assert tile.meta.order == 1
    assert tile.meta.ipix == 0
    assert tile.meta.file_format == "fits"
    assert tile.meta.frame == "galactic"
    assert tile.meta.width == 2


@pytest.mark.parametrize("file_format", ["fits", "png"])
def test_healpix_to_hips(tmpdir, file_format):
    nside, tile_width = 4, 2
    npix = hp.nside2npix(nside)
    hpx_data = np.arange(npix, dtype="uint8")

    healpix_to_hips(
        hpx_data=hpx_data,
        tile_width=tile_width,
        base_path=tmpdir,
        file_format=file_format,
        frame="galactic",
    )

    # The test data is filled with np.arange(), here we reproduce the sum of the
    # indices in the nested scheme manually for comparison
    desired = hpx_data.reshape((-1, tile_width, tile_width))

    for idx, val in enumerate(desired):
        filename = str(tmpdir / f"Norder1/Dir0/Npix{idx}.{file_format}")
        if file_format is "fits":
            data = fits.getdata(filename)
            data = np.rot90(data, k=-1)
        else:
            data = np.array(Image.open(filename))
            data = data.T
        assert_allclose(val, data)

    properties = (tmpdir / "properties").read_text(encoding=None)
    assert file_format in properties
    assert "galactic" in properties
