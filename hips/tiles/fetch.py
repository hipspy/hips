# Licensed under a 3-clause BSD style license - see LICENSE.rst
import socket
import asyncio
import urllib.request
import concurrent.futures
from typing import List
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta

__all__ = [
    'fetch_tiles',
]

__doctest_skip__ = [
    'fetch_tiles',
]


def fetch_tiles(tile_metas: List[HipsTileMeta], hips_survey: HipsSurveyProperties,
                progress_bar: bool = True, n_parallel: int = 5,
                timeout: float = 10) -> List[HipsTile]:
    """Fetch a list of HiPS tiles.

    This function fetches a list of HiPS tiles based
    on their URLs, which are generated using ``hips_survey``
    and ``tile_metas``.

    The tiles are then fetched asynchronously using ``urllib`` or ``aiohttp``.

    Parameters
    ----------
    tile_metas : list
        Python list of `~hips.HipsTileMeta`
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    progress_bar : bool
        Show a progress bar for tile fetching and drawing
    n_parallel : int
        Number of tile fetch web requests to make in parallel
    timeout : float
        Seconds to timeout for fetching a HiPS tile

    Examples
    --------
    Define a list of tiles we want::

        from hips import HipsSurveyProperties, HipsTileMeta
        from hips import fetch_tiles
        url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
        hips_survey = HipsSurveyProperties.fetch(url)
        tile_indices = [69623, 69627, 69628, 69629, 69630, 69631]
        tile_metas = []
        for healpix_pixel_index in tile_indices:
            tile_meta = HipsTileMeta(
               order=7,
               ipix=healpix_pixel_index,
               frame=hips_survey.astropy_frame,
               file_format='fits',
            )
            tile_metas.append(tile_meta)

    Fetch all tiles (in parallel)::

        tiles = fetch_tiles(tile_metas, hips_survey)

    Returns
    -------
    tiles : list
        A Python list of `~hips.HipsTile`
    """
    tile_urls = [hips_survey.tile_url(meta) for meta in tile_metas]
    response_all = do_fetch_tiles(tile_urls, hips_survey, progress_bar, n_parallel, timeout)

    tiles = []
    for idx, response in enumerate(response_all):
        try:
            response['raw_data']
            tiles.append(HipsTile(tile_metas[idx], response['raw_data']))
        except KeyError:
            tiles.append(HipsTile(tile_metas[idx], b'', is_missing=True))

    return tiles


def do_fetch_single_tile(url: str, timeout: float) -> dict:
    """Fetch a HiPS tile asynchronously."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as conn:
            return {'raw_data': conn.read(), 'url': url}
    except urllib.error.HTTPError as error:
        # If the tile is missing, enable the `is_missing` flag in HipsTile.
        if error.code == 404:
            print(f'Tile not found at:\n{url}')
            return {'is_missing': True}
    except urllib.error.URLError as error:
        if isinstance(error.reason, socket.timeout):
            print(f'The server timed out while fetching the tile at:\n{url}')
            return {'is_missing': True}


def do_fetch_tiles(tile_urls: List[str], hips_survey: HipsSurveyProperties,
                   progress_bar: bool, n_parallel, timeout: float) -> List[dict]:
    """Generator function to fetch HiPS tiles from a remote URL."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel) as executor:
        return list(executor.map(do_fetch_single_tile, tile_urls, [timeout] * len(tile_urls)))
