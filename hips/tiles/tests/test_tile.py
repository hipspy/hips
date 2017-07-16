# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose, assert_equal
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta, HipsTile


class TestHipsTileMeta:
    @classmethod
    def setup_class(cls):
        cls.meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs')

    def test_nside(self):
        assert self.meta.nside == 8

    def test_skycoord_corners(self):
        coord = self.meta.skycoord_corners
        assert_allclose(coord.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(coord.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert self.meta.skycoord_corners.frame.name == 'icrs'

    @staticmethod
    def test_skycoord_corners_galactic():
        meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='galactic')
        coord = meta.skycoord_corners
        assert_allclose(coord.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(coord.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert coord.frame.name == 'galactic'

    def test_tile_url(self):
        url = self.meta.tile_default_url
        assert url == 'Norder3/Dir0/Npix450.fits'


HIPS_TILE_TEST_CASES = [
    dict(
        meta=dict(order=3, ipix=463, file_format='fits'),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.fits',
        filename='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.fits',

        dtype='int16',
        shape=(512, 512),
        pix_idx=[[510], [5]],
        pix_val=[3047],
    ),
    dict(
        meta=dict(order=3, ipix=463, file_format='jpg'),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.jpg',
        filename='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg',

        dtype='uint8',
        shape=(512, 512, 3),
        pix_idx=[[510], [5]],
        pix_val=[[10, 10, 10]],
    ),
    dict(
        meta=dict(order=6, ipix=6112, file_format='png'),
        url='http://alasky.unistra.fr/2MASS6X/2MASS6X_H/Norder6/Dir0/Npix6112.png',
        filename='datasets/samples/2MASS6XH/Norder6/Dir0/Npix6112.png',

        dtype='uint8',
        shape=(512, 512, 4),
        pix_idx=[[253], [5]],
        pix_val=[[19, 19, 19, 255]],
    ),
]


class TestHipsTile:
    @requires_hips_extra()
    @pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES)
    def test_read(self, pars):
        # Check that reading tiles in various formats works,
        # i.e. that pixel data in numpy array format
        # has correct shape, dtype and values
        meta = HipsTileMeta(**pars['meta'])
        filename = get_hips_extra_file(pars['filename'])
        tile = HipsTile.read(meta, filename)
        data = tile.data

        assert data.shape == pars['shape']
        assert data.dtype.name == pars['dtype']
        assert_equal(tile.data[pars['pix_idx']], pars['pix_val'])

    # @requires_hips_extra()
    # @pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES)
    # def test_write(self, tmpdir, pars):
    #
    #         filename = str(tmpdir / pars['file_name'])
    #     tile.write(filename)
    #     tile2 = HipsTile.read(meta, full_path=filename)
    #
    #     # TODO: Fix JPG write issue
    #     # assert tile == tile2


    @remote_data
    @requires_hips_extra()
    @pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES)
    def test_fetch(self, pars):
        # Check that tile HTTP fetch gives the same result as tile read from disk
        meta = HipsTileMeta(**pars['meta'])
        tile_fetch = HipsTile.fetch(meta, url=pars['url'])

        filename = get_hips_extra_file(pars['filename'])
        tile_read = HipsTile.read(meta, filename)

        assert tile_fetch == tile_read
