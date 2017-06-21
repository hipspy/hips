# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
import healpy as hp
from ..healpix import boundaries, compute_healpix_pixel_indices
from .test_wcs import make_test_wcs_geometry


def test_boundaries():
    nside = hp.order2nside(order=3)
    theta, phi = boundaries(nside, pix=450)

    radec = SkyCoord(ra=phi, dec=np.pi / 2 - theta, unit='radian')

    """
    These HEALPix corner values were verified through Aladin Lite with the "Show
    healpix grid" option turned on. More information can be found on this GitHub
    issue: https://github.com/healpy/healpy/issues/393#issuecomment-305994042
    """
    assert_allclose(radec.ra.deg, [264.375, 258.75, 264.375, 270.])
    assert_allclose(radec.dec.deg, [-24.624318, -30., -35.685335, -30.])


def test_compute_healpix_pixel_indices():
    wcs_geometry = make_test_wcs_geometry(case=1)
    nside = hp.order2nside(order=3)
    pixels = compute_healpix_pixel_indices(wcs_geometry, nside)
    assert_allclose(pixels, [176, 207, 208, 239, 240, 271, 272])
