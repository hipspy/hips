# Licensed under a 3-clause BSD style license - see LICENSE.rst
from numpy.testing import assert_allclose
from ..testing import make_test_wcs_geometry


class TestWCSGeometry:
    def setup(self):
        self.wcs_geometry = make_test_wcs_geometry(case=0)

    def test_center(self):
        c = self.wcs_geometry.center_skycoord
        assert c.frame.name == 'galactic'
        assert_allclose(c.l.deg, 2, atol=1e-2)
        assert_allclose(c.b.deg, 4.5, atol=1e-2)
