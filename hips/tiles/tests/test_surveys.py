# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ..surveys import HipsSurveyProperties, HipsSurveyPropertiesList
from ...utils.testing import get_hips_extra_file, requires_hips_extra

class TestHipsSurveyProperties:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        cls.hips_survey_property = HipsSurveyProperties.read(filename)

    def test_title(self):
        assert self.hips_survey_property.title == 'DSS colored'

    def test_hips_version(self):
        assert self.hips_survey_property.hips_version == '1.31'

    def test_hips_frame(self):
        assert self.hips_survey_property.hips_frame == 'equatorial'

    def test_astropy_frame(self):
        assert self.hips_survey_property.astropy_frame == 'icrs'

    def test_hips_order(self):
        assert self.hips_survey_property.hips_order == 9

    def test_tile_format(self):
        assert self.hips_survey_property.tile_format == 'jpeg'

    def test_base_url(self):
        assert self.hips_survey_property.base_url == 'http://alasky.u-strasbg.fr/DSS/DSSColor'

    def test_tile_access_url(self):
        assert self.hips_survey_property.tile_access_url(order=9, ipix=54321) == 'http://alasky.u-strasbg.fr/DSS/DSSColor/Norder9/Dir50000/'


    @requires_hips_extra()
    def test_tile_width(self):
        filename = get_hips_extra_file('datasets/samples/Planck-HFI143/properties')
        survey = HipsSurveyProperties.read(filename)
        assert survey.tile_width == 256


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
