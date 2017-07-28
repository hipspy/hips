# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
from astropy.tests.helper import remote_data
from ...utils.testing import make_test_wcs_geometry
from ...tiles import HipsSurveyProperties
from ..ui import make_sky_image

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
