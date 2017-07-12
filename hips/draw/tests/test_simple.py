# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
from numpy.testing import assert_allclose
from astropy.tests.helper import remote_data
from ..simple import make_sky_image, draw_sky_image, compute_matching_hips_order, _get_hips_order_for_resolution
from ...tiles import HipsSurveyProperties, HipsTileMeta, HipsTile
from ...utils import WCSGeometry
from ...utils.testing import get_hips_extra_file, make_test_wcs_geometry, requires_hips_extra


def get_test_tiles(file_format, survey, order, ipix_list):
    filename = get_hips_extra_file('datasets/samples/' + survey + '/properties')
    hips_survey = HipsSurveyProperties.read(filename)

    tiles = []
    for ipix in ipix_list:
        tiles.append(HipsTile.read(
            meta=HipsTileMeta(order=order, ipix=ipix, file_format=file_format, frame=hips_survey.astropy_frame),
            full_path=get_hips_extra_file('datasets/samples/' + survey + hips_survey.tile_path(order=order, ipix=ipix, tile_format=file_format)),
        ))

    return tiles


draw_sky_image_pars = [
    dict(file_format='fits', shape=(1000, 2000), survey='DSS2Red', data_1=2866.0101409848185,
         data_2=2563.6916727348043, data_sum=4575235421.512643, order=3, ipix_list=[450, 451]),
    dict(file_format='jpg', shape=(1000, 2000, 3), survey='DSS2Red', data_1=[13.040878, 13.040878, 13.040878],
         data_2=[17.235874, 17.235874, 17.235874], data_sum=243177268.56158745, order=3, ipix_list=[450, 451]),
    dict(file_format='png', shape=(1000, 2000, 4), survey='AKARI-FIS', data_1=[254., 254., 254., 255.],
         data_2=[254., 254., 254., 255.], data_sum=946809963.7487414, order=3, ipix_list=[450, 451])
]


@remote_data
@requires_hips_extra()
@pytest.mark.parametrize('pars', draw_sky_image_pars)
def test_draw_sky_image(pars):
    geometry = make_test_wcs_geometry(case=2)
    tiles = get_test_tiles(file_format=pars['file_format'], survey=pars['survey'], order=pars['order'], ipix_list=pars['ipix_list'])
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/' + pars['survey'] + '/properties'
    hips_survey = HipsSurveyProperties.fetch(url)

    data = draw_sky_image(geometry=geometry, tiles=tiles, hips_survey=hips_survey, tile_format=pars['file_format'])

    assert data.shape == pars['shape']
    assert data.dtype == np.float64
    assert_allclose(np.sum(data), pars['data_sum'])
    assert_allclose(data[400, 500], pars['data_1'])
    assert_allclose(data[400, 501], pars['data_2'])


@remote_data
def test_make_sky_image():
    # The same example is used in the high level docs getting started page
    url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    hips_survey = HipsSurveyProperties.fetch(url)
    geometry = make_test_wcs_geometry(case=2)
    data = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format='fits')
    assert data.shape == geometry.shape
    assert data.dtype == np.float64

    assert_allclose(np.sum(data), 8757489268.044867)
    assert_allclose(data[200, 994], 2213.30874796)
    assert_allclose(data[200, 995], 2296.93885940)

hips_order_pars = [
    dict(order=7, fov="3 deg"),
    dict(order=5, fov="10 deg"),
    dict(order=4, fov="15 deg"),
]


@requires_hips_extra()
@pytest.mark.parametrize('pars', hips_order_pars)
def test_compute_matching_hips_order(pars):
    full_path = get_hips_extra_file('datasets/samples/2MASS6XH/properties')
    hips_survey = HipsSurveyProperties.read(filename=full_path)
    geometry = WCSGeometry.create_simple(
        skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
        width=2000, height=1000, fov=pars['fov'],
        coordsys='icrs', projection='AIT'
    )
    assert compute_matching_hips_order(geometry, hips_survey) == pars['order']

get_hips_order_for_resolution_pars = [
    dict(tile_width=512, resolution=0.01232, resolution_res=0.06395791924665553, order=4),
    dict(tile_width=256, resolution=0.0016022, resolution_res=0.003997369952915971, order=8),
    dict(tile_width=128, resolution=0.00009032, resolution_res=0.00012491781102862408, order=13),
]


@pytest.mark.parametrize('pars', get_hips_order_for_resolution_pars)
def test_get_hips_order_for_resolution(pars):
    hips_order = _get_hips_order_for_resolution(pars['tile_width'], pars['resolution'])
    assert hips_order == pars['order']
    hips_resolution = hp.nside2resol(hp.order2nside(hips_order))
    assert_allclose(hips_resolution, pars['resolution_res'])
# TODO: add tests for SimpleTilePainter with asserts on the intermediate computed things.
