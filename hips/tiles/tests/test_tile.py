# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.tests.helper import remote_data

from ..tile import HipsTile
from ..tile_meta import HipsTileMeta


class TestHipsTile:
    def setup(self):
        self.hips_tile_meta_fits = HipsTileMeta(order=6, ipix=30889, file_format='fits')
        self.hips_tile_meta_jpg = HipsTileMeta(order=6, ipix=30889, file_format='jpg')

    @remote_data
    def test_fetch_read_write(self, tmpdir):
        fits_tile = HipsTile.fetch(self.hips_tile_meta_fits,
                                   'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.fits')
        jpg_tile = HipsTile.fetch(self.hips_tile_meta_jpg,
                                  'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.jpg')

        data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        assert fits_tile.data.shape == (512, 512)
        assert jpg_tile.data.shape == (512, 512, 3)
        assert list(fits_tile.data[510][:12]) == data_precomp

        jpg_tile.write('Npix30889.jpg', str(tmpdir / 'Npix30889.jpg'))
        fits_tile.write('Npix30889.fits', str(tmpdir / 'Npix30889.fits'))

        jpg_tile = HipsTile.read(self.hips_tile_meta_jpg, str(tmpdir / 'Npix30889.jpg'))
        fits_tile = HipsTile.read(self.hips_tile_meta_fits, str(tmpdir / 'Npix30889.fits'))

        data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        assert fits_tile.data.shape == (512, 512)
        assert jpg_tile.data.shape == (512, 512, 3)
        assert list(fits_tile.data[510][:12]) == data_precomp
