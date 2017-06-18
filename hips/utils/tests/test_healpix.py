# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import healpy as hp
from ..wcs import WCSGeometry
from ..healpix import boundaries
from astropy.coordinates import SkyCoord
from numpy.testing import assert_allclose
from ..healpix import compute_healpix_pixel_indices


def test_boundaries():
    order = 3
    nside = hp.order2nside(order)
    pix = 450
    theta, phi = boundaries(nside, pix)

    radec = SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')

    """
    These HEALPix corner values were verified through Aladin Lite with the "Show
    healpix grid" option turned on. More information can be found on this GitHub
    issue: https://github.com/healpy/healpy/issues/393#issuecomment-305994042
    """
    radec_precomp = [[264.375,  258.75,  264.375,  270.],
                     [-24.624318,  -30.,  -35.685335,  -30.]]
    assert_allclose([radec.ra, radec.dec], radec_precomp)

def test_compute_healpix_pixel_indices():
    order = 3
    nside = hp.order2nside(order)

    skycoord = SkyCoord(10, 20, unit="deg")
    wcs_geometry = WCSGeometry.create(skycoord, (10, 20), 'CEL', 'AIT', 1.0, 1)

    """
    These pixel values were obtained for the all-sky image located at:
    https://github.com/gammapy/gammapy-extra/blob/master/datasets/catalogs/fermi/gll_psch_v08.fit.gz?raw=true
    """
    pixels_precomp = [0, 767]

    pixels = compute_healpix_pixel_indices(wcs_geometry, nside)
    assert_allclose([pixels[0], pixels[-1]], pixels_precomp)
