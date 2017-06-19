# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ..surveys import HipsSurveyPropertiesList

class TestHipsSurveyPropertiesList:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/surveys.txt')
        cls.hips_survey_list = HipsSurveyPropertiesList.read(filename)

    @remote_data
    def test_fetch(self):
        self.hips_survey_list.fetch()

    def test_surveys(self):
        assert len(self.hips_survey_list.surveys) == 4
        assert self.hips_survey_list.surveys[0].properties['creator_did'] == 'ivo://CDS/C/MUSE-M42'
        assert self.hips_survey_list.surveys[0].properties['obs_collection'] == 'MUSE-M42'
        assert self.hips_survey_list.surveys[0].properties['hips_tile_format'] == 'png fits'
        assert self.hips_survey_list.table['surveys'][0]['hips_tile_format'] == 'png fits'
