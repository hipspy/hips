# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .. healpix import boundaries
import numpy as np


def test_boundaries():
    nside = 8
    pix = 450
    theta, phi = boundaries(nside, pix, nest=True)

    thetaphi_precomp = ([[2.00057176,  2.0943951,  2.19362291,  2.0943951],
                         [4.61421421,  4.51603944,  4.61421421,  4.71238898]])

    np.testing.assert_allclose([theta, phi], thetaphi_precomp)
