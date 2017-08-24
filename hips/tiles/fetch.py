# Licensed under a 3-clause BSD style license - see LICENSE.rst
import asyncio
import urllib.request
import concurrent.futures
from typing import Generator, List
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta

__all__ = [
    'fetch_tiles',
]

__doctest_skip__ = [
    'fetch_tiles',
]


def fetch_tiles(tile_metas: List[HipsTileMeta], hips_survey: HipsSurveyProperties,
                progress_bar: bool = False, n_parallel: int = 10,
                timeout: float = 10, fetch_package: str = 'urllib') -> List[HipsTile]:
    """Fetch a list of HiPS tiles.

    This function fetches a list of HiPS tiles based
    on their URLs, which are generated using ``hips_survey``
    and ``tile_metas``.

    The tiles are then fetched asynchronously using ``urllib`` or ``aiohttp``.

    Parameters
    ----------
    tile_metas : List[HipsTileMeta]
        Python list of HipsTileMeta
    hips_survey : `~hips.HipsSurveyProperties`
        HiPS survey properties
    progress_bar : bool
        Show a progress bar for tile fetching and drawing
    n_parallel : int
        Number of threads to use for fetching HiPS tiles
    timeout : float
        Seconds to timeout for fetching a HiPS tile
    fetch_package : {'urllib', 'aiohttp'}
        Package to use for fetching HiPS tiles

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
    tiles : List[HipsTile]
        A Python list of HiPS tiles
    """
    if fetch_package == 'aiohttp':
        fetch_fct = tiles_aiohttp
    elif fetch_package == 'urllib':
        fetch_fct = tiles_urllib
    else:
        raise ValueError(f'Invalid package name: {fetch_package}')

    tiles = fetch_fct(tile_metas, hips_survey, progress_bar, n_parallel, timeout)

    # Sort tiles to match the tile_meta list
    # TODO: this doesn't seem like a great solution.
    # Use OrderedDict instead?
    out = []
    for tile_meta in tile_metas:
        for tile in tiles:
            if tile.meta == tile_meta:
                out.append(tile)
                continue
    return out


def fetch_tile_urllib(url: str, meta: HipsTileMeta, timeout: float) -> Generator:
    """Fetch a HiPS tile asynchronously."""
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        raw_data = conn.read()
        return HipsTile(meta, raw_data)


def tiles_urllib(tile_metas: List[HipsTileMeta], hips_survey: HipsSurveyProperties,
                 progress_bar: bool = False, n_parallel: int = 10, timeout: float = 10) -> List[HipsTile]:
    """Generator function to fetch HiPS tiles from a remote URL."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel) as executor:
        futures = []
        for meta in tile_metas:
            url = hips_survey.tile_url(meta)
            future = executor.submit(fetch_tile_urllib, url, meta, timeout)
            futures.append(future)

        futures = concurrent.futures.as_completed(futures)
        if progress_bar:
            from tqdm import tqdm
            futures = tqdm(futures, total=len(tile_metas), desc='Fetching tiles')

        tiles = []
        for future in futures:
            tiles.append(future.result())

    return tiles


async def fetch_tile_aiohttp(url: str, meta: HipsTileMeta, session) -> Generator:
    """Fetch a HiPS tile asynchronously using aiohttp."""
    async with session.get(url) as response:
        raw_data = await response.read()
        return HipsTile(meta, raw_data)


async def fetch_all_tiles_aiohttp(tile_metas: List[HipsTileMeta],
                                  hips_survey: HipsSurveyProperties, progress_bar: bool) -> List[HipsTile]:
    """Generator function to fetch HiPS tiles from a remote URL using aiohttp."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        futures = []
        for meta in tile_metas:
            url = hips_survey.tile_url(meta)
            future = asyncio.ensure_future(fetch_tile_aiohttp(url, meta, session))
            futures.append(future)

        futures = asyncio.as_completed(futures)
        if progress_bar:
            from tqdm import tqdm
            futures = tqdm(futures, total=len(tile_metas), desc='Fetching tiles')

        tiles = []
        for future in futures:
            tiles.append(await future)

    return tiles


def tiles_aiohttp(tile_metas: List[HipsTileMeta], hips_survey: HipsSurveyProperties,
                  progress_bar: bool, n_parallel: int = 10, timeout: float = 10) -> List[HipsTile]:
    # TODO: implement n_parallel and timeout
    return asyncio.get_event_loop().run_until_complete(
        fetch_all_tiles_aiohttp(tile_metas, hips_survey, progress_bar)
    )
