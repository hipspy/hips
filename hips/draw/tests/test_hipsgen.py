# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_equal
from ...tiles import HipsTile, HipsTileMeta
from ..hipsgen import healpix_to_hips
from .test_healpix import make_hpx_data


@pytest.mark.parametrize("file_format", ["fits", "png"])
def test_healpix_to_hips(tmpdir, file_format):
    hpx_data = make_hpx_data(file_format)

    healpix_to_hips(
        hpx_data=hpx_data, tile_width=2, base_path=tmpdir, file_format=file_format
    )

    properties = (tmpdir / "properties").read_text(encoding=None)
    assert file_format in properties
    assert "icrs" in properties

    # Check one tile
    filename = str(tmpdir / f"Norder1/Dir0/Npix2.{file_format}")
    meta = HipsTileMeta(order=1, ipix=2, file_format=file_format, width=2)
    tile = HipsTile.read(meta, filename)

    if file_format == "fits":
        assert tile.data.dtype == np.uint8
        assert tile.data.shape == (2, 2)
        assert_equal(tile.data, [[9, 11], [8, 10]])
    elif file_format == "png":
        assert tile.data.dtype == np.uint8
        assert tile.data.shape == (2, 2, 4)
        assert_equal(tile.data[..., 0], [[9, 11], [8, 10]])
