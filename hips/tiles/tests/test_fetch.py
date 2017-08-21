# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose
from ..fetch import fetch_tiles
from ..survey import HipsSurveyProperties
from ..tile import HipsTileMeta

TILE_FETCH_TEST_CASES = [
    dict(
        tile_indices=[69623, 69627, 69628, 69629, 69630, 69631],
        tile_format='fits',
        order=7,
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        progress_bar=True,
        data=[2101, 1680, 1532, 1625, 2131],
        fetch_package='urllib'
    ),
    dict(
        tile_indices=[69623, 69627, 69628, 69629, 69630, 69631],
        tile_format='fits',
        order=7,
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        progress_bar=True,
        data=[2101, 1680, 1532, 1625, 2131],
        fetch_package='aiohttp'
    ),
]


@pytest.mark.parametrize('pars', TILE_FETCH_TEST_CASES)
@remote_data
def test_fetch_tiles(pars):
    hips_survey = HipsSurveyProperties.fetch(pars['url'])

    tile_metas = []
    for healpix_pixel_index in pars['tile_indices']:
        tile_meta = HipsTileMeta(
            order=pars['order'],
            ipix=healpix_pixel_index,
            frame=hips_survey.astropy_frame,
            file_format=pars['tile_format'],
        )
        tile_metas.append(tile_meta)

    tiles = fetch_tiles(tile_metas, hips_survey, progress_bar=pars['progress_bar'], fetch_package=pars['fetch_package'])
    assert_allclose(tiles[0].data[0][5:10], [2101, 1680, 1532, 1625, 2131])
