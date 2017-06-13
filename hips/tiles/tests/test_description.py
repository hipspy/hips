# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from ..description import HipsDescription


class TestHiPSDescription:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        cls.hipsdescription = HipsDescription.read(filename)

    def test_base_url(self):
        assert self.hipsdescription.base_url == 'http://alasky.u-strasbg.fr/DSS/DSSColor'

    def test_title(self):
        assert self.hipsdescription.title == 'DSS colored'

    def test_hips_version(self):
        assert self.hipsdescription.hips_version == '1.31'

    def test_hips_frame(self):
        assert self.hipsdescription.hips_frame == 'equatorial'

    def test_hips_order(self):
        assert self.hipsdescription.hips_order == 9

    def test_tile_format(self):
        assert self.hipsdescription.tile_format == 'jpeg'
