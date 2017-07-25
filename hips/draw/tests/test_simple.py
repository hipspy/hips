# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
from astropy.tests.helper import remote_data
from ...utils.testing import make_test_wcs_geometry, requires_hips_extra
from ...utils.wcs import WCSGeometry
from ...tiles import HipsSurveyProperties
from ..simple import make_sky_image, SimpleTilePainter, plot_mpl_single_tile
from ..simple import is_tile_distorted, measure_tile_shape

make_sky_image_pars = [
    dict(
        file_format='fits',
        shape=(1000, 2000),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        data_1=2213,
        data_2=2296,
        data_sum=8756493140,
        dtype='>i2',
        repr='HipsDrawResult(width=1000, height=2000, channels=2, dtype=>i2, format=fits)'
    ),
    dict(
        file_format='jpg',
        shape=(1000, 2000, 3),
        url='https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/FermiColor/properties',
        data_1=[133, 117, 121],
        data_2=[137, 116, 114],
        data_sum=828908873,
        dtype='uint8',
        repr='HipsDrawResult(width=1000, height=2000, channels=3, dtype=uint8, format=jpg)'
    ),
    dict(
        file_format='png',
        shape=(1000, 2000, 4),
        url='https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/AKARI-FIS/properties',
        data_1=[224, 216, 196, 255],
        data_2=[227, 217, 205, 255],
        data_sum=1635622838,
        dtype='uint8',
        repr='HipsDrawResult(width=1000, height=2000, channels=3, dtype=uint8, format=png)'
    ),
]


@remote_data
@pytest.mark.parametrize('pars', make_sky_image_pars)
def test_make_sky_image(tmpdir, pars):
    hips_survey = HipsSurveyProperties.fetch(url=pars['url'])
    geometry = make_test_wcs_geometry()
    result = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format=pars['file_format'])
    assert result.image.shape == pars['shape']
    assert result.image.dtype == pars['dtype']
    assert repr(result) == pars['repr']
    assert_allclose(np.sum(result.image), pars['data_sum'])
    assert_allclose(result.image[200, 994], pars['data_1'])
    assert_allclose(result.image[200, 995], pars['data_2'])
    result.write_image(str(tmpdir / 'test.' + pars['file_format']))
    result.plot()

@remote_data
class TestSimpleTilePainter:
    @classmethod
    def setup_class(cls):
        url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
        cls.hips_survey = HipsSurveyProperties.fetch(url)
        cls.geometry = WCSGeometry.create(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov="3 deg",
            coordsys='icrs', projection='AIT',
        )
        cls.painter = SimpleTilePainter(cls.geometry, cls.hips_survey, 'fits')

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

        simple_tile_painter = SimpleTilePainter(geometry, self.hips_survey, 'fits')
        assert simple_tile_painter.draw_hips_order == pars['order']

    def test_run(self):
        self.painter.run()
        assert self.painter.image.shape == (1000, 2000)
        assert_allclose(self.painter.image[200, 994], 2120)

    def test_draw_hips_tile_grid(self):
        self.painter.plot_mpl_hips_tile_grid()

    def test_draw_debug_image(self):
        tile = self.painter.tiles[3]
        image = self.painter.image
        plot_mpl_single_tile(self.geometry, tile, image)


@pytest.fixture(scope='session')
def corners():
    x = [764.627476, 999., 764.646551, 530.26981]
    y = [300.055412, 101.107245, -97.849955, 101.105373]
    return x, y


def test_is_tile_distorted(corners):
    assert is_tile_distorted(corners) is True


def test_measure_tile_shape(corners):
    edges, diagonals = measure_tile_shape(corners)

    expected = [307.426175, 307.417479, 307.434024, 307.41606]
    assert_allclose(edges, expected)

    assert_allclose(diagonals, [397.905367, 468.73019])
