# Licensed under a 3-clause BSD style license - see LICENSE.rst
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
from ..wcs import WCSGeometry


class TestWCSGeometry:
    def setup(self):
        self.geometry = WCSGeometry.create(
            skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
            width=2000, height=1000, fov='3 deg',
            coordsys='galactic', projection='AIT',
        )

    def test_galactic_frame_center(self):
        c = self.geometry.center_skycoord

        assert c.frame.name == 'galactic'
        assert_allclose(c.l.deg, 359.99, atol=1e-2)
        assert_allclose(c.b.deg, 0.00075, atol=1e-2)
        assert_allclose(self.geometry.wcs.wcs.crpix, [1000., 500.])
        assert_allclose(self.geometry.wcs.wcs.cdelt, [-0.0015, 0.0015])

    def test_celestial_frame(self):
        geometry = WCSGeometry.create(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov='3 deg',
            coordsys='icrs', projection='AIT',
        )
        c = geometry.center_skycoord

        assert c.frame.name == 'icrs'
        assert_allclose(c.ra.deg, 359.99, atol=1e-2)
        assert_allclose(c.dec.deg, 0.00075, atol=1e-2)
        assert_allclose(self.geometry.wcs.wcs.crpix, [1000., 500.])
        assert_allclose(self.geometry.wcs.wcs.cdelt, [-0.0015, 0.0015])
