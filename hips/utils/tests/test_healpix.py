# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from numpy.testing import assert_allclose, assert_equal
import healpy as hp
from ..testing import make_test_wcs_geometry
from ..healpix import (
    healpix_order_to_npix,
    healpix_pixel_corners,
    healpix_pixels_in_sky_image,
    hips_order_for_pixel_resolution,
    hips_tile_healpix_ipix_array,
)


def test_order_to_npix():
    assert healpix_order_to_npix(3) == 768


def test_healpix_pixel_corners():
    """
    These HEALPix corner values were verified through Aladin Lite with the "Show
    healpix grid" option turned on. More information can be found on this GitHub
    issue: https://github.com/healpy/healpy/issues/393#issuecomment-305994042
    """
    corners = healpix_pixel_corners(order=3, ipix=450, frame='icrs')

    assert_allclose(corners.ra.deg, [264.375, 258.75, 264.375, 270.])
    assert_allclose(corners.dec.deg, [-24.624318, -30., -35.685335, -30.])


@pytest.mark.parametrize('pars', [
    dict(frame='galactic', ipix=[269, 270, 271, 280, 282, 283, 292, 293, 295, 304, 305, 306]),
    dict(frame='icrs', ipix=[448, 449, 450, 451, 454, 456, 457, 460, 661, 663, 669]),
])
def test_wcs_healpix_pixel_indices(pars):
    geometry = make_test_wcs_geometry()
    healpix_pixel_indices = healpix_pixels_in_sky_image(geometry, order=3, healpix_frame=pars['frame'])
    assert list(healpix_pixel_indices) == pars['ipix']


@pytest.mark.parametrize('pars', [
    dict(tile_width=512, resolution=0.01232, resolution_res=0.06395791924665553, order=4),
    dict(tile_width=256, resolution=0.0016022, resolution_res=0.003997369952915971, order=8),
    dict(tile_width=128, resolution=0.00009032, resolution_res=0.00012491781102862408, order=13),
])
def test_get_hips_order_for_resolution(pars):
    hips_order = hips_order_for_pixel_resolution(pars['tile_width'], pars['resolution'])
    assert hips_order == pars['order']
    hips_resolution = hp.nside2resol(hp.order2nside(hips_order))
    assert_allclose(hips_resolution, pars['resolution_res'])


def test_hips_tile_healpix_ipix_array():
    ipix = hips_tile_healpix_ipix_array(shift_order=1)
    ipix_expected = [
        [0, 1],
        [2, 3],
    ]
    assert ipix.shape == (2, 2)
    assert_equal(ipix, ipix_expected)

    ipix = hips_tile_healpix_ipix_array(shift_order=2)
    ipix_expected = [
        [0, 1, 4, 5],
        [2, 3, 6, 7],
        [8, 9, 12, 13],
        [10, 11, 14, 15],
    ]
    assert ipix.shape == (4, 4)
    assert_equal(ipix, ipix_expected)

    ipix = hips_tile_healpix_ipix_array(shift_order=3)
    assert ipix.shape == (8, 8)
    assert ipix[0, 0] == 0
    assert ipix[-1, -1] == 63
