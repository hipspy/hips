# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
from astropy.coordinates import SkyCoord
from astropy.tests.helper import remote_data
from ...tiles import HipsSurveyProperties
from ..simple import make_sky_image, SimpleTilePainter
from ...utils.wcs import WCSGeometry
from ...utils.testing import make_test_wcs_geometry, requires_hips_extra

make_sky_image_pars = [
    dict(
        file_format='fits',
        shape=(1000, 2000),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        data_1=2213,
        data_2=2296,
        data_sum=8756493140,
        dtype='>i2'
    ),
    dict(
        file_format='jpg',
        shape=(1000, 2000, 3),
        url='https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/FermiColor/properties',
        data_1=[145, 98, 49],
        data_2=[146, 99, 56],
        data_sum=808113247,
        dtype='uint8'
    ),
    dict(
        file_format='png',
        shape=(1000, 2000, 4),
        url='https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/AKARI-FIS/properties',
        data_1=[249, 237, 190, 255.],
        data_2=[249, 238, 195, 255.],
        data_sum=1632505453,
        dtype='uint8'
    ),
]


@remote_data
@pytest.mark.parametrize('pars', make_sky_image_pars)
def test_make_sky_image(pars):
    hips_survey = HipsSurveyProperties.fetch(url=pars['url'])
    geometry = make_test_wcs_geometry(case=2)
    image = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format=pars['file_format'])
    assert image.shape == pars['shape']
    assert image.dtype == pars['dtype']
    assert_allclose(np.sum(image), pars['data_sum'])
    assert_allclose(image[200, 994], pars['data_1'])
    assert_allclose(image[200, 995], pars['data_2'])


@remote_data
class TestSimpleTilePainter:
    @classmethod
    def setup_class(cls):
        url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
        cls.hips_survey = HipsSurveyProperties.fetch(url)
        cls.geometry = WCSGeometry.create_simple(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov="3 deg",
            coordsys='icrs', projection='AIT'
        )
        cls.simple_tile_painter = SimpleTilePainter(cls.geometry, cls.hips_survey, 'fits')

    def test_draw_hips_order(self):
        assert self.simple_tile_painter.draw_hips_order == 7

    def test_shape(self):
        assert self.simple_tile_painter.shape == (1000, 2000)

    def test_tile_indices(self):
        assert list(self.simple_tile_painter.tile_indices)[:4] == [69623, 69627, 69628, 69629]

    draw_hips_order_pars = [
        dict(order=7, fov="3 deg"),
        dict(order=5, fov="10 deg"),
        dict(order=4, fov="15 deg"),
    ]

    @requires_hips_extra()
    @pytest.mark.parametrize('pars', draw_hips_order_pars)
    def test_compute_matching_hips_order(self, pars):
        geometry = WCSGeometry.create_simple(
            skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
            width=2000, height=1000, fov=pars['fov'],
            coordsys='icrs', projection='AIT'
        )
        simple_tile_painter = SimpleTilePainter(geometry, self.hips_survey, 'fits')
        assert simple_tile_painter.draw_hips_order == pars['order']

    def test_run(self):
        self.simple_tile_painter.run()
        assert_allclose(self.simple_tile_painter.image[200, 994], 2120)
