# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from numpy.testing import assert_allclose
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ..simple import make_sky_image, draw_sky_image
from ...tiles import HipsSurveyProperties, HipsTileMeta, HipsTile
from ...utils.testing import get_hips_extra_file, make_test_wcs_geometry, requires_hips_extra


def get_test_tiles():
    filename = get_pkg_data_filename('../../tiles/tests/data/properties.txt')
    hips_survey = HipsSurveyProperties.read(filename)

    tile1 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=450, file_format='fits', frame=hips_survey.astropy_frame),
        full_path=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix450.fits'),
    )

    tile2 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=451, file_format='fits', frame=hips_survey.astropy_frame),
        full_path=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix451.fits'),
    )

    return [tile1, tile2]


@remote_data
@requires_hips_extra()
def test_draw_sky_image():
    geometry = make_test_wcs_geometry(case=2)
    tiles = get_test_tiles()
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    hips_survey = HipsSurveyProperties.fetch(url)

    data = draw_sky_image(geometry, tiles, hips_survey)

    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert_allclose(np.sum(data), 4575235421.5126467)
    assert_allclose(data[400, 500], 2866.0101409848185)
    assert_allclose(data[400, 501], 2563.6916727348043)


@remote_data
def test_make_sky_image():
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    hips_survey = HipsSurveyProperties.fetch(url)
    geometry = make_test_wcs_geometry(case=2)
    data = make_sky_image(geometry, hips_survey)
    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert_allclose(data[200, 994], 3717.10091363)
    assert_allclose(data[200, 995], 3402.55292158)


# TODO: add tests for SimpleTilePainter with asserts on the intermediate computed things.
