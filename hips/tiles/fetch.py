# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import urllib.request
import concurrent.futures
from typing import Generator, List
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta

__all__ = [
    'HipsTileFetcher',
]


class HipsTileFetcher:
    """Fetch a list of HiPS tiles.

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

    def __init__(self, tile_metas: List[HipsTileMeta], hips_survey : HipsSurveyProperties,
                 progress_bar: bool = False, n_parallel: int = 10,  timeout: int = 10, fetch_package : str = 'urllib') -> None:
        self.tile_metas = tile_metas
        self.hips_survey = hips_survey
        self.progress_bar = progress_bar
        self.n_parallel = n_parallel
        self.timeout = timeout
        self.fetch_package = fetch_package

    @property
    def tile_urls(self) -> List[str]:
        """List of tile URLs"""
        tile_urls = []
        for meta in self.tile_metas:
            tile_urls.append(self.hips_survey.tile_url(meta))

        return tile_urls

    @property
    def tiles(self):
        if self.fetch_package == 'aiohttp':
            return self.tiles_aiohttp
        elif self.fetch_package == 'urllib':
            return self.tiles_urllib
        else:
            raise ValueError(f'Invalid package name: {self.fetch_package}')

    def fetch_tile_urllib(self, url: str, meta : HipsTileMeta) -> Generator:
        """Fetch a HiPS tile asynchronously."""
        with urllib.request.urlopen(url, timeout=self.timeout) as conn:
            raw_data = conn.read()
            return HipsTile(meta, raw_data)

    @property
    def tiles_urllib(self) -> np.ndarray:
        """Generator function to fetch HiPS tiles from a remote URL."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n_parallel) as executor:
            future_to_url = {executor.submit(self.fetch_tile_urllib, url, self.tile_metas[idx]) : url for idx, url in enumerate(self.tile_urls)}

            if self.progress_bar:
                from tqdm import tqdm
                requests = tqdm(concurrent.futures.as_completed(future_to_url), total=len(future_to_url), desc='Fetching tiles')
            else:
                requests = future_to_url#concurrent.futures.as_completed(future_to_url)

            tiles = []
            for future in requests:
                tiles.append(future.result())

        return tiles

    async def fetch_tile_aiohttp(self, url: str, meta : HipsTileMeta, session) -> Generator:
        """Fetch a HiPS tile asynchronously using aiohttp."""
        async with session.get(url) as response:
            raw_data = await response.read()
            return HipsTile(meta, raw_data)

    @property
    async def fetch_all_tiles_aiohttp(self) -> np.ndarray:
        """Generator function to fetch HiPS tiles from a remote URL using aiohttp."""
        import aiohttp, asyncio

        tasks = []
        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(self.tile_urls):
                task = asyncio.ensure_future(self.fetch_tile_aiohttp(url.format(idx), self.tile_metas[idx], session))
                tasks.append(task)

            if self.progress_bar:
                from tqdm import tqdm
                tiles = []
                for f in tqdm(tasks, total=len(tasks), desc='Fetching tiles'):
                    tiles.append(await f)
            else:
                tiles = await asyncio.gather(*tasks)

        return tiles

    @property
    def tiles_aiohttp(self) -> np.ndarray:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.fetch_all_tiles_aiohttp)
