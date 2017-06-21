# Licensed under a 3-clause BSD style license - see LICENSE.rst
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord

from ..wcs import WCSGeometry


def make_test_wcs_geometry(case=0):
    """An example Galactic CAR WCS that """
    if case == 0:
        return WCSGeometry.create(
            skydir=SkyCoord(3, 4, unit='deg', frame='galactic'),
            shape=(2, 3), coordsys='GAL',
            projection='CAR', cdelt=1.0, crpix=(1, 1),
        )
    elif case == 1:
        return WCSGeometry.create(
            skydir=SkyCoord(10, 20, unit='deg', frame='galactic'),
            shape=(10, 20), coordsys='GAL',
            projection='CAR', cdelt=1.0, crpix=(1, 1),
        )
    else:
        raise ValueError()


class TestWCSGeometry:
    def setup(self):
        self.wcs_geometry = make_test_wcs_geometry(case=0)

    def test_center(self):
        c = self.wcs_geometry.center_skycoord
        assert c.frame.name == 'galactic'
        assert_allclose(c.l.deg, 2, atol=1e-2)
        assert_allclose(c.b.deg, 4.5, atol=1e-2)
