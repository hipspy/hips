# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ..description import HipsDescription
from ..tile import HipsTile
from pathlib import Path
import numpy as np

class TestHipsTile:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        hips_description = HipsDescription.read(filename)

        cls.fits_tile = HipsTile(hips_description=hips_description, order=6,
                            ipix=30889, format='fits', tile_width=512)
        cls.jpg_tile = HipsTile(hips_description=hips_description, order=6,
                            ipix=30889, format='jpg', tile_width=512)
        cls.fits_tile.base_url = 'http://alasky.unistra.fr/2MASS/H'
        cls.jpg_tile.base_url = 'http://alasky.unistra.fr/2MASS/H'

    def test_base_url(self):
        assert self.fits_tile.base_url == 'http://alasky.unistra.fr/2MASS/H'
        assert self.jpg_tile.base_url == 'http://alasky.unistra.fr/2MASS/H'

    def test_tile_url(self):
        assert self.fits_tile.tile_url == 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.fits'
        assert self.jpg_tile.tile_url == 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.jpg'

    @remote_data
    def test_fetch(self):
        self.fits_tile.fetch()
        self.jpg_tile.fetch()

        shape_fits_precomp = (512, 512)
        shape_jpg_precomp = (512, 512, 3)
        data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        assert self.fits_tile.data.shape == shape_fits_precomp
        assert self.jpg_tile.data.shape == shape_jpg_precomp
        assert list(self.fits_tile.data[510][:12]) == data_precomp

    def test_read(self):
        self.fits_tile.read()
        self.jpg_tile.read()

        shape_fits_precomp = (512, 512)
        shape_jpg_precomp = (512, 512, 3)
        data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        assert (self.fits_tile.data.shape) == shape_fits_precomp
        assert (self.jpg_tile.data.shape) == shape_jpg_precomp
        assert list(self.fits_tile.data[510][:12]) == data_precomp

    def test_write(self):
        filename = 'test_file'
        self.fits_tile.write(filename)
        self.jpg_tile.write(filename)

        path_fits = self.fits_tile.path.joinpath(''.join([filename, '.', self.fits_tile.format]))
        path_jpg = self.jpg_tile.path.joinpath(''.join([filename, '.', self.jpg_tile.format]))
        assert True == path_fits.is_file()
        assert True == path_jpg.is_file()
