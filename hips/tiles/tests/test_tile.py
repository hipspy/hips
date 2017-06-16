# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from ..description import HipsDescription
from ..tile import HipsTile
from pathlib import Path
import numpy as np

class TestHipsTile:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        hips_description = HipsDescription.read(filename)

        cls.tile = HipsTile(hips_description, 6, 24185, 'jpg')
        cls.tile.base_url = 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_base_url(self):
        assert self.tile.base_url == 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_tile_url(self):
        assert self.tile.tile_url == 'http://alasky.unistra.fr/DSS/DSSColor/Norder6/Dir20000/Npix24185.jpg'

    def test_fetch(self):
        self.tile.fetch()

        """
        This data was obtain from 'http://alasky.unistra.fr/DSS/DSSColor/Norder6/Dir20000/Npix24185.jpg'
        at the index [10, 20]
        """
        data_precomp = [0, 0, 0]
        assert self.data[10, 20] == data_precomp

    def test_read(self):
        self.tile.read()

        """
        This data was obtain from 'http://alasky.unistra.fr/DSS/DSSColor/Norder6/Dir20000/Npix24185.jpg'
        at the index [10, 20]
        """
        data_precomp = [0, 0, 0]
        assert list(self.tile.data[10, 20]) == data_precomp

    def test_store(self):
        filename = 'test_file'
        self.tile.store(filename)

        path = self.tile.path.joinpath(''.join([filename, '.', self.tile.format]))
        assert True == path.is_file()
