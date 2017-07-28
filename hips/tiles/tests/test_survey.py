# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from numpy.testing import assert_allclose
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import remote_data
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta
from ..survey import HipsSurveyProperties, HipsSurveyPropertiesList


class TestHipsSurveyProperties:
    @classmethod
    def setup_class(cls):
        filename = get_pkg_data_filename('data/properties.txt')
        cls.survey = HipsSurveyProperties.read(filename)

    @remote_data
    def test_from_name(self):
        survey = HipsSurveyProperties.from_name('CDS/P/2MASS/color')
        assert survey.title == '2MASS color J (1.23 microns), H (1.66 microns), K (2.16 microns)'

    @remote_data
    def test_make(self):
        survey = HipsSurveyProperties.make('CDS/P/EGRET/Dif/300-500')
        assert survey.title == 'EGRET Dif 300-500'
        assert self.survey is HipsSurveyProperties.make(self.survey)

    def test_title(self):
        assert self.survey.title == 'DSS colored'

    def test_hips_version(self):
        assert self.survey.hips_version == '1.31'

    def test_hips_frame(self):
        assert self.survey.hips_frame == 'equatorial'

    def test_astropy_frame(self):
        assert self.survey.astropy_frame == 'icrs'

    def test_hips_order(self):
        assert self.survey.hips_order == 9

    def test_tile_format(self):
        assert self.survey.tile_format == 'jpeg'

    def test_base_url(self):
        expected = 'http://alasky.u-strasbg.fr/DSS/DSSColor'
        assert self.survey.base_url == expected

    def test_tile_default_url(self):
        tile_meta = HipsTileMeta(order=9, ipix=54321, file_format='fits')
        url = self.survey.tile_url(tile_meta)
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

        survey = surveys.from_name('CDS/P/2MASS/H')
        assert survey.title == '2MASS H (1.66 microns)'
        assert survey.hips_order == 9

    @remote_data
    def test_key_error(self):
        with pytest.raises(KeyError):
            surveys = HipsSurveyPropertiesList.fetch()
            surveys.from_name('Kronka Lonka')
