# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from ..tile import HipsTile
from ..description import HipsDescription


class TestHipsTile:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        hips_description = HipsDescription.read(filename)

        cls.tile = HipsTile(hips_description, 6, 24185, 'jpg')
        cls.tile.data = [0, 0, 0, 0]
        cls.tile.base_url = 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_base_url(self):
        assert self.tile.base_url == 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_data(self):
        assert self.tile.data == [0, 0, 0, 0]

    def test_tile_url(self):
        assert self.tile.get_tile_url(6, 24185, 'jpg') == 'http://alasky.unistra.fr/DSS/DSSColor/Norder6/Dir20000/Npix24185.jpg'
