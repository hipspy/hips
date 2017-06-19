# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from ..description import HipsSurveyProperties


class TestHipsSurveyProperties:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        cls.hips_survey_property = HipsSurveyProperties.read(filename)

    def test_base_url(self):
        assert self.hips_survey_property.base_url == 'http://alasky.u-strasbg.fr/DSS/DSSColor'

    def test_title(self):
        assert self.hips_survey_property.title == 'DSS colored'

    def test_hips_version(self):
        assert self.hips_survey_property.hips_version == '1.31'

    def test_hips_frame(self):
        assert self.hips_survey_property.hips_frame == 'equatorial'

    def test_hips_order(self):
        assert self.hips_survey_property.hips_order == 9

    def test_tile_format(self):
        assert self.hips_survey_property.tile_format == 'jpeg'
