# Licensed under a 3-clause BSD style license - see LICENSE.rst
import asyncio
import urllib.request
import concurrent.futures
from typing import Generator, List
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta

__all__ = [
    'fetch_tiles',
]

def fetch_tiles(tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties,
                progress_bar: bool = False, n_parallel: int = 10,  timeout: int = 10, fetch_package : str = 'urllib') -> List[HipsTile]:
    """Fetch a list of HiPS tiles.

    This function fetches a list of HiPS tiles based
    on their URLs, which are generated using `hips_survey`
    and `tile_metas`. The tiles are then fetched asynchronously
    using urllib or aiohttp.

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
    timeout : int
        Seconds to timeout for fetching a HiPS tile
    fetch_package : {'urllib', 'aiohttp'}
        Package to use for fetching HiPS tiles
    """
    if fetch_package == 'aiohttp':
        return tiles_aiohttp(tile_metas, hips_survey, progress_bar)
    elif fetch_package == 'urllib':
        return tiles_urllib(tile_metas, hips_survey, progress_bar, n_parallel, timeout)
    else:
        raise ValueError(f'Invalid package name: {fetch_package}')

def tile_urls(tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties) -> List[str]:
    """List of tile URLs"""
    return [hips_survey.tile_url(meta) for meta in tile_metas]

def fetch_tile_urllib(url: str, meta: HipsTileMeta, timeout: int) -> Generator:
    """Fetch a HiPS tile asynchronously."""
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        raw_data = conn.read()
        return HipsTile(meta, raw_data)

def tiles_urllib(tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties,
                 progress_bar: bool = False, n_parallel: int = 10,  timeout: int = 10) -> List[HipsTile]:
    """Generator function to fetch HiPS tiles from a remote URL."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_parallel) as executor:
        future_to_url = {executor.submit(
            fetch_tile_urllib,
            url,
            tile_metas[idx],
            timeout)
            : url for idx, url in enumerate(tile_urls(tile_metas, hips_survey))}

        if progress_bar:
            from tqdm import tqdm
            requests = tqdm(future_to_url, total=len(future_to_url), desc='Fetching tiles')
        else:
            requests = future_to_url

        tiles = []
        for request in requests:
            tiles.append(request.result())

    return tiles

async def fetch_tile_aiohttp(url: str, meta : HipsTileMeta, session) -> Generator:
    """Fetch a HiPS tile asynchronously using aiohttp."""
    async with session.get(url) as response:
        raw_data = await response.read()
        return HipsTile(meta, raw_data)

async def fetch_all_tiles_aiohttp(tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties, progress_bar: bool) -> List[HipsTile]:
    """Generator function to fetch HiPS tiles from a remote URL using aiohttp."""
    import aiohttp

    tasks = []
    async with aiohttp.ClientSession() as session:
        for idx, url in enumerate(tile_urls(tile_metas, hips_survey)):
            task = asyncio.ensure_future(fetch_tile_aiohttp(url.format(idx), tile_metas[idx], session))
            tasks.append(task)

        if progress_bar:
            from tqdm import tqdm
            tiles = []
            for f in tqdm(tasks, total=len(tasks), desc='Fetching tiles'):
                tiles.append(await f)
        else:
            tiles = await asyncio.gather(*tasks)

    return tiles

def tiles_aiohttp(tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties,
                  progress_bar: bool) -> List[HipsTile]:
    return asyncio.get_event_loop().run_until_complete(fetch_all_tiles_aiohttp(tile_metas, hips_survey, progress_bar))
