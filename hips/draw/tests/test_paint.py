# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
from astropy.tests.helper import remote_data
from ...utils.testing import requires_hips_extra
from ...utils.wcs import WCSGeometry
from ...tiles import HipsSurveyProperties
from ..paint import is_tile_distorted, measure_tile_lengths, HipsPainter, plot_mpl_single_tile


@remote_data
class TestHipsPainter:
    @classmethod
    def setup_class(cls):
        url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
        cls.hips_survey = HipsSurveyProperties.fetch(url)
        cls.geometry = WCSGeometry.create(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov="3 deg",
            coordsys='icrs', projection='AIT',
        )
        cls.painter = HipsPainter(cls.geometry, cls.hips_survey, 'fits')

    def test_draw_hips_order(self):
        assert self.painter.draw_hips_order == 7

    def test_tile_indices(self):
        assert list(self.painter.tile_indices)[:4] == [69623, 69627, 69628, 69629]

    draw_hips_order_pars = [
        dict(order=7, fov="3 deg"),
        dict(order=5, fov="10 deg"),
        dict(order=4, fov="15 deg"),
    ]

    @requires_hips_extra()
    @pytest.mark.parametrize('pars', draw_hips_order_pars)
    def test_compute_matching_hips_order(self, pars):
        geometry = WCSGeometry.create(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov=pars['fov'],
            coordsys='icrs', projection='AIT',
        )

        simple_tile_painter = HipsPainter(geometry, self.hips_survey, 'fits')
        assert simple_tile_painter.draw_hips_order == pars['order']

    def test_run(self):
        self.painter.run()
        assert self.painter.image.shape == (1000, 2000)
        assert_allclose(self.painter.image[200, 994], 2120)

    def test_draw_hips_tile_grid(self):
        self.painter.plot_mpl_hips_tile_grid()

    def test_draw_debug_image(self):
        tile = self.painter.tiles[3]
        image = self.painter._make_empty_sky_image()
        plot_mpl_single_tile(self.geometry, tile, image)


@pytest.fixture(scope='session')
def corners():
    x = [764.627476, 999., 764.646551, 530.26981]
    y = [300.055412, 101.107245, -97.849955, 101.105373]
    return x, y


def test_is_tile_distorted(corners):
    assert is_tile_distorted(corners) is True


def test_measure_tile_lengths(corners):
    edges, diagonals = measure_tile_lengths(corners)

    expected = [307.426175, 307.417479, 307.434024, 307.41606]
    assert_allclose(edges, expected)

    assert_allclose(diagonals, [397.905367, 468.73019])
