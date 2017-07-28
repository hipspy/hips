# Licensed under a 3-clause BSD style license - see LICENSE.rst
from collections import OrderedDict
from io import StringIO
from csv import DictWriter
import urllib.request
from typing import List, Union
from astropy.table import Table
from .tile import HipsTileMeta

__all__ = [
    'HipsSurveyProperties',
    'HipsSurveyPropertiesList',
]

__doctest_skip__ = [
    'HipsSurveyProperties',
    'HipsSurveyPropertiesList',
]


class HipsSurveyProperties:
    """HiPS properties container.

    Parameters
    ----------
    data : `~collections.OrderedDict`
        HiPS survey properties

    Examples
    --------
    >>> from hips import HipsSurveyProperties
    >>> url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    >>> hips_survey_property = HipsSurveyProperties.fetch(url)
    >>> hips_survey_property.base_url
    'http://alasky.u-strasbg.fr/DSS/DSS2Merged'
    """
    hips_to_astropy_frame_mapping = OrderedDict([
        ('equatorial', 'icrs'),
        ('galactic', 'galactic'),
        ('ecliptic', 'ecliptic'),
    ])
    """HIPS to Astropy SkyCoord frame string mapping."""

    def __init__(self, data: OrderedDict) -> None:
        self.data = data

    @classmethod
    def from_name(cls, name: str) -> 'HipsSurveyProperties':
        """Create object from Survey ID (`HipsSurveyProperties`)."""
        # TODO: implement some kind of caching for HipsSurveyPropertiesList
        surveys = HipsSurveyPropertiesList.fetch()
        return surveys.from_name(name)

    @classmethod
    def make(cls, hips_survey: Union[str, 'HipsSurveyProperties']) -> 'HipsSurveyProperties':
        """Convenience constructor for from_string classmethod or existing object (`HipsSurveyProperties`)."""
        if isinstance(hips_survey, str):
            return HipsSurveyProperties.from_name(hips_survey)
        elif isinstance(hips_survey, HipsSurveyProperties):
            return hips_survey
        else:
            raise TypeError(f'hips_survey must be of type str or `HipsSurveyProperties`. You gave {type(hips_survey)}')

    @classmethod
    def read(cls, filename: str) -> 'HipsSurveyProperties':
        """Read from HiPS survey description file (`HipsSurveyProperties`).

        Parameters
        ----------
        filename : str
            HiPS properties filename
        """
        with open(filename) as fh:
            text = fh.read()

        return cls.parse(text)

    @classmethod
    def fetch(cls, url: str) -> 'HipsSurveyProperties':
        """Read from HiPS survey description file from remote URL (`HipsSurveyProperties`).

        Parameters
        ----------
        url : str
            URL containing HiPS properties
        """

        with urllib.request.urlopen(url) as response:
            text = response.read().decode('utf-8')
        return cls.parse(text, url)

    @classmethod
    def parse(cls, text: str, url: str = None) -> 'HipsSurveyProperties':
        """Parse HiPS survey description text (`HipsSurveyProperties`).

        Parameters
        ----------
        text : str
            Text containing HiPS survey properties
        url : str
            Properties URL of HiPS
        """
        data: OrderedDict = OrderedDict()
        for line in text.split('\n'):
            # Skip empty or comment lines
            if line == '' or line.startswith('#'):
                continue
            try:
                key, value = [_.strip() for _ in line.split('=')]
                data[key] = value
            except ValueError:
                # Skip bad lines (silently, might not be a good idea to do this)
                continue

        if url is not None:
            data['properties_url'] = url.rsplit('/', 1)[0]

        return cls(data)

    @property
    def title(self) -> str:
        """HiPS title (str)."""
        return self.data['obs_title']

    @property
    def hips_version(self) -> str:
        """HiPS version (str)."""
        return self.data['hips_version']

    @property
    def hips_frame(self) -> str:
        """HiPS coordinate frame (str)."""
        return self.data['hips_frame']

    @property
    def astropy_frame(self) -> str:
        """Astropy coordinate frame (str)."""
        return self.hips_to_astropy_frame_mapping[self.hips_frame]

    @property
    def hips_order(self) -> int:
        """HiPS order (int)."""
        return int(self.data['hips_order'])

    @property
    def tile_width(self) -> int:
        """HiPS tile width"""
        try:
            return int(self.data['hips_tile_width'])
        except KeyError:
            return 512

    @property
    def tile_format(self) -> str:
        """HiPS tile format (str)."""
        return self.data['hips_tile_format']

    @property
    def hips_service_url(self) -> str:
        """HiPS service base URL (str)."""
        return self.data['hips_service_url']

    @property
    def base_url(self) -> str:
        """HiPS access URL"""
        try:
            return self.data['hips_service_url']
        except KeyError:
            try:
                return self.data['moc_access_url'].rsplit('/', 1)[0]
            except KeyError:
                try:
                    return self.data['properties_url']
                except KeyError:
                    raise ValueError('URL does not exist!')

    def tile_url(self, tile_meta: HipsTileMeta) -> str:
        """Tile URL on the server (str)."""
        return self.base_url + '/' + tile_meta.tile_default_url


class HipsSurveyPropertiesList:
    """HiPS survey properties list.

    Parameters
    ----------
    data : list
        Python list of `~hips.HipsSurveyProperties`

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

    You can make a `astropy.table.Table` of available HiPS surveys:

    >>> table = surveys.table

    and then do all the operations that Astropy table supports, e.g.

    >>> table[['ID', 'hips_order', 'hips_service_url']][[1, 30, 42]]
    >>> table.show_in_browser(jsviewer=True)
    >>> table.show_in_notebook()
    >>> table.to_pandas()

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
        with urllib.request.urlopen(url) as response:
            text = response.read().decode('utf-8', errors='ignore')
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
        """Table with HiPS survey infos (`~astropy.table.Table`)."""
        # There are two aspects that make creating a `Table` from the data difficult:
        # 1. Not all fields are present for the different surveys
        # 2. All data is stored as strings, numbers haven't been converted yet
        #
        # It might not be the best solution, but the following code does the conversion
        # by going via an intermediate CVS string, which Table can parse directly
        rows = [properties.data for properties in self.data]
        fieldnames = sorted({key for row in rows for key in row})
        buffer = StringIO()
        writer = DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return Table.read(buffer.getvalue(), format='ascii.csv', guess=False)

    def from_name(self, name: str) -> 'HipsSurveyProperties':
        """Return a matching HiPS survey (`HipsSurveyProperties`)."""
        for survey in self.data:
            if survey.data['ID'].strip() == name.strip():
                return survey

        raise KeyError(f'Survey not found: {name}')
