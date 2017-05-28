# Licensed under a 3-clause BSD style license - see LICENSE.rst
from ..simple import hello


def test_hello():
    meaning_of_life = hello('Adeel')
    assert meaning_of_life == 43
