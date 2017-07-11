# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
import healpy as hp
from ..healpix import boundaries, compute_healpix_pixel_indices, get_hips_order_for_resolution
from ..testing import make_test_wcs_geometry


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


compute_healpix_pixel_indices_pars = [
    dict(frame='galactic', ipix=[269, 270, 271, 280, 282, 283, 292, 293, 295, 304, 305, 306]),
    dict(frame='icrs', ipix=[448, 449, 450, 451, 454, 456, 457, 460, 661, 663, 669]),
]


@pytest.mark.parametrize('pars', compute_healpix_pixel_indices_pars)
def test_wcs_healpix_pixel_indices(pars):
    geometry = make_test_wcs_geometry(case=2)
    healpix_pixel_indices = compute_healpix_pixel_indices(geometry, order=3, healpix_frame=pars['frame'])
    assert list(healpix_pixel_indices) == pars['ipix']

hips_order_for_resolution_pars = [
    dict(tile_width=512, resolution=0.01232, resolution_res=0.06395791924665553, order=4),
    dict(tile_width=256, resolution=0.0016022, resolution_res=0.003997369952915971, order=8),
    dict(tile_width=128, resolution=0.00009032, resolution_res=0.00012491781102862408, order=13),
]


@pytest.mark.parametrize('pars', hips_order_for_resolution_pars)
def test_get_hips_order_for_resolution(pars):
    hips_order = get_hips_order_for_resolution(pars['tile_width'], pars['resolution'])
    assert hips_order == pars['order']
    hips_resolution = hp.nside2resol(hp.order2nside(hips_order))
    assert_allclose(hips_resolution, pars['resolution_res'])
