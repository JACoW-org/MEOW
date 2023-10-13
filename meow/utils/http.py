import asyncio
import logging
from typing import Any, AsyncIterable

import io
import aiohttp

from anyio import open_file, Path

from meow.app.config import conf
from meow.models.local.common.auth import BasicAuthData
from meow.utils.serialization import json_encode

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
            except Exception:
                pass


async def fetch_chunks(url: str, headers: dict = {}, cookies: dict = {}) -> AsyncIterable:
    """ Fetch chunks function """

    def json_serialize(val):
        return str(json_encode(val), 'utf-8')

    async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            json_serialize=json_serialize,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)

            async with client.get(url) as resp:
                if resp.ok:
                    async for chunk in resp.content.iter_chunked(16 * 1024):
                        yield chunk
                else:
                    raise BaseException(
                        f"invalid response status {resp.status}")
        finally:
            HttpClientSessions.del_client_session(client)


async def fetch_json(url: str, headers: dict = {}, cookies: dict = {}, auth: BasicAuthData | None = None) -> Any:
    """ Fetch json function """

    def json_serialize(val):
        return str(json_encode(val), 'utf-8')

    basic_auth = aiohttp.BasicAuth(
        auth.login, auth.password) \
        if auth else None

    async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            auth=basic_auth,
            json_serialize=json_serialize,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)
            async with client.get(url) as resp:
                try:
                    if resp.ok:
                        return await resp.json()
                    raise BaseException(
                        # f"invalid response status {resp.status}"
                        dict(code=resp.status,
                             message=f"invalid response status {resp.status}")
                    )
                except BaseException as ex:
                    logger.error(ex, exc_info=True)
                    raise ex
        except asyncio.TimeoutError as ex:
            logger.error(ex, exc_info=True)
            raise BaseException(dict(code=504, message="timeout exception"))
        finally:
            HttpClientSessions.del_client_session(client)


async def delete_json(url: str, headers: dict = {}, cookies: dict = {}, auth: BasicAuthData | None = None) -> Any:
    """ Delete json function """

    def json_serialize(val):
        return str(json_encode(val), 'utf-8')

    basic_auth = aiohttp.BasicAuth(
        auth.login, auth.password) \
        if auth else None

    async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            auth=basic_auth,
            json_serialize=json_serialize,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)
            async with client.delete(url) as resp:
                try:
                    if resp.ok:
                        return
                    raise BaseException(
                        # f"invalid response status {resp.status}"
                        dict(code=resp.status,
                             message=f"invalid response status {resp.status}")
                    )
                except BaseException as ex:
                    logger.error(ex, exc_info=True)
                    raise ex
        except asyncio.TimeoutError as ex:
            logger.error(ex, exc_info=True)
            raise BaseException(dict(code=504, message="timeout exception"))
        finally:
            HttpClientSessions.del_client_session(client)


async def put_json(url: str, data: Any, headers: dict = {}, cookies: dict = {},
                   auth: BasicAuthData | None = None) -> Any:
    """ Send HTTP PUT json function """

    def json_serialize(val):
        return str(json_encode(val), 'utf-8')

    basic_auth = aiohttp.BasicAuth(
        auth.login, auth.password) \
        if auth else None

    async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            auth=basic_auth,
            json_serialize=json_serialize,
            timeout=aiohttp.ClientTimeout(
                total=conf.HTTP_REQUEST_TIMEOUT_SECONDS
            )
    ) as client:
        try:
            HttpClientSessions.add_client_session(client)
            async with client.put(url, data=data) as resp:
                try:
                    body: str = ''
                    if resp.ok:
                        return await resp.json()
                    try:
                        body = await resp.text()
                    except BaseException as ex:
                        logger.error(ex, exc_info=True)
                    raise BaseException(
                        # f"invalid response status" + f" {resp.status} - {body}"
                        dict(
                            code=resp.status, message="invalid response status" + f" {resp.status} - {body}")
                    )
                except BaseException as ex:
                    logger.error(ex, exc_info=True)
                    raise ex
        except asyncio.TimeoutError as ex:
            logger.error(ex, exc_info=True)
            raise BaseException(dict(code=504, message="timeout exception"))
        except BaseException as ex:
            logger.error(ex, exc_info=True)
            raise ex
        finally:
            HttpClientSessions.del_client_session(client)


async def download_json(url: str, headers: dict = {}, cookies: dict = {}) -> Any:
    """ Download json function """

    # logger.info(f'download_json --> {url}')

    return await fetch_json(url, headers=headers, cookies=cookies)


async def download_file(url: str, file: Path, headers: dict = {}, cookies: dict = {}) -> None:
    """ Download file function """

    # print('download_file -->', url)

    async with await open_file(file, mode='wb') as f:
        async for chunk in fetch_chunks(url, headers=headers, cookies=cookies):
            await f.write(chunk)

        # print('download_file -->', file)


async def download_stream(url: str, headers: dict = {}, cookies: dict = {}) -> io.BytesIO:
    """ Download file function """

    # print(f'download_stream --> {url} --> {headers} --> {cookies}')

    f = io.BytesIO()

    async for chunk in fetch_chunks(url, headers=headers, cookies=cookies):
        f.write(chunk)

    f.seek(0)

    return f
