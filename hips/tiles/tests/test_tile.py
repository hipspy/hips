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

    def test_path(self):
        assert str(self.meta.path) == 'hips/tiles/tests/data'

    def test_filename(self):
        assert self.meta.filename == 'Npix450.fits'

    def test_full_path(self):
        assert str(self.meta.full_path) == 'hips/tiles/tests/data/Npix450.fits'

    def test_nside(self):
        assert self.meta.nside == 8

    def test_skycoord_corners(self):
        assert_allclose(self.meta.skycoord_corners.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(self.meta.skycoord_corners.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert self.meta.skycoord_corners.frame.name == 'icrs'

    @staticmethod
    def test_skycoord_corners_galactic():
        meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='galactic')
        assert_allclose(meta.skycoord_corners.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(meta.skycoord_corners.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert meta.skycoord_corners.frame.name == 'galactic'


HIPS_TILE_TEST_CASES = [
    dict(
        meta=dict(order=3, ipix=463, file_format='fits'),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.fits',
        full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.fits',
        file_name='Npix463.fits',

        shape=(512, 512),
        pix_idx=[[510], [5]],
        pix_val=[3047],
    ),
    dict(
        meta=dict(order=3, ipix=463, file_format='jpg'),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.jpg',
        full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg',
        file_name='Npix463.jpg',

        shape=(512, 512, 3),
        pix_idx=[[510], [5]],
        pix_val=[[10, 10, 10]],
    ),
    dict(
        meta=dict(order=6, ipix=6112, file_format='png'),
        url='http://alasky.unistra.fr/2MASS6X/2MASS6X_H/Norder6/Dir0/Npix6112.png',
        full_path='datasets/samples/2MASS6XH/Norder6/Dir0/Npix6112.png',
        file_name='Npix6112.png',

        shape=(512, 512, 4),
        pix_idx=[[253], [5]],
        pix_val=[[19, 19, 19, 255]],
    ),
]


class TestHipsTile:
    @requires_hips_extra()
    @pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES)
    def test_read_write(self, tmpdir, pars):
        # Check that reading tiles in various formats works,
        # and that read / write round-trips, i.e. works properly
        meta = HipsTileMeta(**pars['meta'])
        full_path = get_hips_extra_file(pars['full_path'])
        tile = HipsTile.read(meta, full_path)

        assert tile.data.shape == pars['shape']
        assert_equal(tile.data[pars['pix_idx']], pars['pix_val'])

        filename = str(tmpdir / pars['file_name'])
        tile.write(filename)
        tile2 = HipsTile.read(meta, full_path=filename)

        # TODO: Fix JPG write issue
        # assert tile == tile2

    @requires_hips_extra()
    def test_value_error(self):
        # Check that an invalid `file_format` string like "jpeg" (should be "jpg") gives a ValueError
        meta = HipsTileMeta(order=3, ipix=463, file_format='jpeg')
        full_path = get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg')
        with pytest.raises(ValueError):
            HipsTile.read(meta, full_path)

    @remote_data
    @requires_hips_extra()
    @pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES)
    def test_fetch(self, pars):
        # Check that tile HTTP fetch gives the same result as tile read from disk
        meta = HipsTileMeta(**pars['meta'])
        tile_fetched = HipsTile.fetch(meta, url=pars['url'])

        full_path = get_hips_extra_file(pars['full_path'])
        tile_local = HipsTile.read(meta, full_path=full_path)

        assert tile_fetched == tile_local
