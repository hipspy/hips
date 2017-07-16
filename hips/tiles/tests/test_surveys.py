# Licensed under a 3-clause BSD style license - see LICENSE.rst
from numpy.testing import assert_allclose
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta
from ..surveys import HipsSurveyProperties, HipsSurveyPropertiesList


class TestHipsSurveyProperties:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        cls.hips_survey = HipsSurveyProperties.read(filename)

    def test_title(self):
        assert self.hips_survey.title == 'DSS colored'

    def test_hips_version(self):
        assert self.hips_survey.hips_version == '1.31'

    def test_hips_frame(self):
        assert self.hips_survey.hips_frame == 'equatorial'

    def test_astropy_frame(self):
        assert self.hips_survey.astropy_frame == 'icrs'

    def test_hips_order(self):
        assert self.hips_survey.hips_order == 9

    def test_tile_format(self):
        assert self.hips_survey.tile_format == 'jpeg'

    def test_base_url(self):
        expected = 'http://alasky.u-strasbg.fr/DSS/DSSColor'
        assert self.hips_survey.base_url == expected

    def test_tile_default_url(self):
        tile_meta = HipsTileMeta(order=9, ipix=54321, file_format='fits')
        url = self.hips_survey.tile_url(tile_meta)
        assert url == 'http://alasky.u-strasbg.fr/DSS/DSSColor/Norder9/Dir50000/Npix54321.fits'

    @staticmethod
    @requires_hips_extra()
    def test_tile_width():
        filename = get_hips_extra_file('datasets/samples/Planck-HFI143/properties')
        survey = HipsSurveyProperties.read(filename)
        assert survey.tile_width == 256

    @staticmethod
    @remote_data
    def test_fetch():
        url = 'http://alasky.u-strasbg.fr/DSS/DSS2-NIR/properties'
        survey = HipsSurveyProperties.fetch(url)
        assert survey.base_url == 'http://alasky.u-strasbg.fr/DSS/DSS2-NIR'


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

    def test_table(self):
        table = self.surveys.table
        assert len(table) == 4

        row = table[0]
        assert row['creator_did'] == 'ivo://CDS/C/MUSE-M42'
        assert row['obs_collection'] == 'MUSE-M42'
        assert row['hips_tile_format'] == 'png fits'
        assert row['moc_order'] == 12
        assert_allclose(row['moc_sky_fraction'], 2.98e-07, rtol=0.01)

    @remote_data
    def test_fetch(self):
        surveys = HipsSurveyPropertiesList.fetch()
        assert len(surveys.data) > 3

        # TODO: look up survey by name here
        # Otherwise this will break when the list changes
        survey = surveys.data[0]
        assert survey.title == '2MASS H (1.66 microns)'
        assert survey.hips_order == 9
