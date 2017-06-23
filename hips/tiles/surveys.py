# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from typing import List
from astropy.table import Table
from .description import HipsSurveyProperties

__all__ = [
    'HipsSurveyPropertiesList',
]

__doctest_skip__ = ['HipsSurveyPropertiesList']


class HipsSurveyPropertiesList:
    """HiPS survey properties list.

    Parameters
    ----------
    data : List[HipsSurveyProperties]
        HiPS survey properties

    Examples
    --------
    Fetch the list of available HiPS surveys from CDS:

    >>> from hips import HipsSurveyPropertiesList
    >>> surveys = HipsSurveyPropertiesList.fetch()

    Look at the results:

    >>> len(surveys.data)
    335
    >>> survey = surveys.data[0]
    >>> survey.title
    '2MASS H (1.66 microns)'
    >>> survey.hips_order
    9
    """
    DEFAULT_URL = ('http://alasky.unistra.fr/MocServer/query?'
                   'hips_service_url=*&dataproduct_type=!catalog&dataproduct_type=!cube&get=record')
    """Default URL to fetch HiPS survey list from CDS."""

    def __init__(self, data: List[HipsSurveyProperties]) -> None:
        self.data = data

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
    def fetch(cls, url: str = None) -> 'HipsSurveyPropertiesList':
        """Fetch HiPS list text from remote location (`HipsSurveyPropertiesList`).

        Parameters
        ----------
        url : str
            HiPS list URL
        """
        url = url or cls.DEFAULT_URL
        response = urllib.request.urlopen(url).read()
        text = response.decode('utf-8', errors='ignore')
        return cls.parse(text)

    @classmethod
    def parse(cls, text: str) -> 'HipsSurveyPropertiesList':
        """Parse HiPS list text (`HipsSurveyPropertiesList`).

        Parameters
        ----------
        text : str
            HiPS list text
        """
        data = []
        for properties_text in text.split('\n\n'):
            properties = HipsSurveyProperties.parse(properties_text)
            data.append(properties)

        return cls(data)

    @property
    def table(self) -> Table:
        """Astropy Table containing HiPS surveys (`HipsSurveyPropertiesList`)."""
        rows = [properties.data for properties in self.data]
        # This way (one column) to fill the table is not useful!
        # Instead, there should be one row per survey and one column per property
        # TODO: implement this properly!
        table = Table()
        table['surveys'] = rows
        return table
