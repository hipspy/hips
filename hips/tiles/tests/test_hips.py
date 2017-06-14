# Licensed under a 3-clause BSD style license - see LICENSE.rst
from ..hips import Hips


class TestHiPS:
    @classmethod
    def setup_class(cls):
        cls.hips = Hips
        cls.hips.base_url = 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_base_url(self):
        assert self.hips.base_url == 'http://alasky.unistra.fr/DSS/DSSColor'

    def test_tile_url(self):
        assert self.hips.get_tile_url(self.hips, 6, 24185, 'jpg') == 'http://alasky.unistra.fr/DSS/DSSColor/Norder6/Dir20000/Npix24185.jpg'
