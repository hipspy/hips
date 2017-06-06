# Licensed under a 3-clause BSD style license - see LICENSE.rst
from .. healpix import boundaries
from astropy.coordinates import SkyCoord
import numpy as np


def test_boundaries():
    nside = 8
    pix = 450
    theta, phi = boundaries(nside, pix, nest=True)

    radec = SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')
    radec_precomp = [[264.375,  258.75,  264.375,  270.],
                     [-24.624318,  -30.,  -35.685335,  -30.]]
    np.testing.assert_allclose([radec.ra, radec.dec], radec_precomp)
