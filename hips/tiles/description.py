# Licensed under a 3-clause BSD style license - see LICENSE.rst
import urllib.request
from collections import OrderedDict

__all__ = [
    'HipsSurveyProperties',
]

__doctest_skip__ = ['HipsSurveyProperties']


class HipsSurveyProperties:
    """HiPS properties container.

    Parameters
    ----------
    data : `~collections.OrderedDict`
        HiPS survey properties

    Examples
    --------
    >>> url = 'https://raw.githubusercontent.com/hipspy/hips/master/hips/tiles/tests/data/properties.txt'
    >>> hips_survey_property = HipsSurveyProperties.fetch(url)
    >>> hips_survey_property.base_url
    'http://alasky.u-strasbg.fr/DSS/DSSColor'
    """

    def __init__(self, data: OrderedDict) -> None:
        self.data = data

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

        response = urllib.request.urlopen(url).read()
        text = response.decode('utf-8')
        return cls.parse(text)

    @classmethod
    def parse(cls, text: str) -> 'HipsSurveyProperties':
        """Parse HiPS survey description text (`HipsSurveyProperties`).

        Parameters
        ----------
        text : str
            Text containing HiPS survey properties
        """
        data = OrderedDict()
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

        return cls(data)

    @property
    def base_url(self) -> str:
        """HiPS service base URL (`str`)."""
        return self.data['hips_service_url']

    @property
    def title(self) -> str:
        """HiPS title (`str`)."""
        return self.data['obs_title']

    @property
    def hips_version(self) -> str:
        """HiPS version (`str`)."""
        return self.data['hips_version']

    @property
    def hips_frame(self) -> str:
        """HiPS coordinate frame (`str`)."""
        return self.data['hips_frame']

    @property
    def hips_order(self) -> int:
        """HiPS order (`int`)."""
        return int(self.data['hips_order'])

    @property
    def tile_format(self) -> str:
        """HiPS tile format (`str`)."""
        return self.data['hips_tile_format']
