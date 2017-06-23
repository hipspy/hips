# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ..surveys import HipsSurveyPropertiesList


class TestHipsSurveyPropertiesList:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/surveys.txt')
        cls.surveys = HipsSurveyPropertiesList.read(filename)

    def test_surveys(self):
        assert len(self.surveys.data) == 4

        survey = self.surveys.data[0]
        assert survey.data['creator_did'] == 'ivo://CDS/C/MUSE-M42'
        assert survey.data['obs_collection'] == 'MUSE-M42'
        assert survey.data['hips_tile_format'] == 'png fits'

        table = self.surveys.table
        assert table['surveys'][0]['hips_tile_format'] == 'png fits'

    @remote_data
    def test_fetch(self):
        surveys = HipsSurveyPropertiesList.fetch()
        assert len(surveys.data) > 3

        # TODO: look up survey by name here
        # Otherwise this will break when the list changes
        survey = surveys.data[0]
        assert survey.title == '2MASS H (1.66 microns)'
        assert survey.hips_order == 9
