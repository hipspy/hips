# Licensed under a 3-clause BSD style license - see LICENSE.rst
import aiohttp
import asyncio
import urllib.request
import concurrent.futures
import numpy as np
from typing import Generator
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta

__all__ = [
    'HipsTileFetcher',
]

__doctest_skip__ = [
    'HipsTileFetcher',
]


class HipsTileFetcher:
    """Fetch a list of HiPS tiles.

    Parameters
    ----------
    geometry : dict or `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    hips_survey : str or `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile
    precise : bool
        Use the precise drawing algorithm
    """

    def __init__(self, tile_indices: np.ndarray, hips_order: int, hips_survey: HipsSurveyProperties, tile_format: str,
                 progress_bar: bool, use_aiohttp: bool) -> None:
        self.tile_indices = tile_indices
        self.hips_order = hips_order
        self.hips_survey = hips_survey
        self.tile_format = tile_format

    def fetch_tile_threaded(self, url: str, session: aiohttp.client.ClientSession) -> Generator:
        """Fetch a HiPS tile asynchronously."""
        with urllib.request.urlopen(url, timeout=60) as conn:
            return conn.read()

    @property
    def tiles(self) -> np.ndarray:
        """Generator function to fetch HiPS tiles from a remote URL."""
        tile_urls, tile_metas = [], []
        for healpix_pixel_index in self.tile_indices:
            tile_meta = HipsTileMeta(
                order=self.hips_order,
                ipix=healpix_pixel_index,
                frame=self.hips_survey.astropy_frame,
                file_format=self.tile_format,
            )
            tile_urls.append(self.hips_survey.tile_url(tile_meta))
            tile_metas.append(tile_meta)

        raw_responses = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(self.fetch_tile_threaded, url, 60): url for url in tile_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                # try:
                raw_responses.append(future.result())
                # except Exception as exc:
                #     print('%r generated an exception: %s' % (url, exc))
                # else:
                #     print('%r page is %d bytes' % (url, len(future.result())))


        #
        # tasks = []
        # async with aiohttp.ClientSession() as session:
        #     for idx, url in enumerate(tile_urls):
        #         task = asyncio.ensure_future(self.fetch_tile_threaded(url.format(idx), session))
        #         tasks.append(task)
        #
        #     raw_responses = await asyncio.gather(*tasks)
        #
        tiles = []
        for idx, raw_data in enumerate(raw_responses):
            tiles.append(HipsTile(tile_metas[idx], raw_data))
        return tiles

    # async def fetch_tile_threaded(self, url: str, session: aiohttp.client.ClientSession) -> Generator:
    #     """Fetch a HiPS tile asynchronously."""
    #     async with session.get(url) as response:
    #         return await response.read()
    #
    # @property
    # async def tiles(self) -> np.ndarray:
    #     """Generator function to fetch HiPS tiles from a remote URL."""
    #     tile_urls, tile_metas = [], []
    #     for healpix_pixel_index in self.tile_indices:
    #         tile_meta = HipsTileMeta(
    #             order=self.hips_order,
    #             ipix=healpix_pixel_index,
    #             frame=self.hips_survey.astropy_frame,
    #             file_format=self.tile_format,
    #         )
    #         tile_urls.append(self.hips_survey.tile_url(tile_meta))
    #         tile_metas.append(tile_meta)
    #
    #     tasks = []
    #     async with aiohttp.ClientSession() as session:
    #         for idx, url in enumerate(tile_urls):
    #             task = asyncio.ensure_future(self.fetch_tile_threaded(url.format(idx), session))
    #             tasks.append(task)
    #
    #         raw_responses = await asyncio.gather(*tasks)
    #
    #     tiles = []
    #     for idx, raw_data in enumerate(raw_responses):
    #         tiles.append(HipsTile(tile_metas[idx], raw_data))
    #     return tiles