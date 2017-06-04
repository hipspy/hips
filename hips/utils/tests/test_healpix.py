# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .. healpix import boundaries
import numpy as np


def test_boundaries():
    nside = 8
    pix = 450
    lon = boundaries(nside, pix, nest=True)
    lonlat_precomp = [[242.19350089, 270., 226.97382512, 229.39870535],
                      [-22.6263803, -43.1943471, -19.37793463, -33.05573115]]

    np.testing.assert_array_almost_equal(lon, lonlat_precomp, decimal=8)
