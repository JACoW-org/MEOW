import logging
import pathlib
from typing import Any, AsyncIterable

import io
import ujson
import aiohttp

from anyio import open_file

from jpsp.app.config import conf

logger = logging.getLogger(__name__)


class HttpClientSessions:
    __sessions: list[aiohttp.ClientSession] = []

    @classmethod
    def add_client_session(cls, sess: aiohttp.ClientSession):
        cls.__sessions.append(sess)

    @classmethod
    def del_client_session(cls, sess: aiohttp.ClientSession):
        cls.__sessions.remove(sess)

    @classmethod
    async def close_client_sessions(cls):
        logging.info('close_client_sessions >>>')
        for sess in cls.__sessions:
            try:
                logging.info(f'close_client_session >>> {sess}')
                await sess.close()
            except Exception as e:
                pass


async def fetch_chunks(url: str) -> AsyncIterable:
    """ Fetch chunks function """

    async with aiohttp.ClientSession(
            json_serialize=ujson.dumps,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)

            async with client.get(url) as resp:
                assert resp.status == 200
                async for chunk in resp.content.iter_chunked(16 * 1024):
                    yield chunk
        finally:
            HttpClientSessions.del_client_session(client)


async def fetch_json(url: str) -> Any:
    """ Fetch json function """

    async with aiohttp.ClientSession(
            json_serialize=ujson.dumps,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)
            async with client.get(url) as resp:
                assert resp.status == 200
                return await resp.json()
        finally:
            HttpClientSessions.del_client_session(client)


async def download_json(url: str) -> Any:
    """ Download json function """

    print('download_json -->', url)

    return await fetch_json(url)


async def download_file(url: str, file: pathlib.Path) -> None:
    """ Download file function """

    print('download_file -->', url)

    async with await open_file(file, mode='wb') as f:
        async for chunk in fetch_chunks(url):
            await f.write(chunk)

        print('download_file -->', file)


async def download_stream(url: str) -> io.BytesIO:
    """ Download file function """

    print('download_stream -->', url)
    
    f = io.BytesIO()

    async for chunk in fetch_chunks(url):
        f.write(chunk)

    f.seek(0)
    
    return f
