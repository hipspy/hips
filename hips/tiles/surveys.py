# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from typing import List
from astropy.table import Table
from collections import OrderedDict
from .description import HipsSurveyProperties

__all__ = [
    'HipsSurveyPropertiesList',
]


class HipsSurveyPropertiesList:
    """HiPS survey container.

    Parameters
    ----------
    surveys : List[HipsSurveyProperties]
        HiPS surveys
    """

    def __init__(self, surveys: List[HipsSurveyProperties]) -> None:
        self.surveys = surveys

    @classmethod
    def read(cls, filename: str) -> 'HipsSurveyPropertiesList':
        """Read HiPS list from file (`HipsSurveyPropertiesList`).

        Parameters
        ----------
        filename : str
            HiPS list filename
        """
        with open(filename, encoding='utf-8', errors='ignore') as fh:
            text = fh.read()
        return cls.parse(text)

    @classmethod
    def fetch(cls, url: str='http://alasky.unistra.fr/MocServer/query?hips_service_url=*&dataproduct_type=!catalog&dataproduct_type=!cube&get=record') -> 'HipsSurveyPropertiesList':
        """Fetch HiPS list text from remote location (`HipsSurveyPropertiesList`).

        Parameters
        ----------
        url : str
            HiPS list URL
        """
        response = urllib.request.urlopen(url).read()
        text = str(response)
        return cls.parse(text)

    @classmethod
    def parse(cls, text: str) -> 'HipsSurveyPropertiesList':
        """Parse HiPS list text (`HipsSurveyPropertiesList`).

        Parameters
        ----------
        text : str
            HiPS list text
        """
        surveys = list()
        for raw_survey in text.split('\n\n'):
            surveys.append(HipsSurveyProperties.parse(raw_survey))
        return cls(surveys)

    @property
    def table(self) -> Table:
        """Astropy Table containing HiPS surveys (`HipsSurveyPropertiesList`)."""
        table = Table()
        table['surveys'] = [survey.properties for survey in self.surveys]
        return table
