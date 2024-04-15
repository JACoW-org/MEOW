import logging as lg
from typing import AsyncGenerator

from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette.routing import Route

from meow.app.sse import EventSourceResponse

from meow.services.local.credential.find_credential import (
    find_credential_by_secret)
from meow.utils.serialization import json_encode

logger = lg.getLogger(__name__)


async def sse_endpoint(req: Request) -> Response:
    try:
        task_id = req.path_params["key"]

        logger.info(f'task_id->{task_id}')

        cookie_api_key = req.cookies.get('X-API-KEY', None)
        header_api_key = req.headers.get('X-API-KEY', None)

        logger.info(f'cookie_api_key->{cookie_api_key}')
        logger.info(f'header_api_key->{header_api_key}')

        credential = await find_credential_by_secret(
            cookie_api_key if cookie_api_key else header_api_key
        )

        if credential:

            # await __open_websocket(ws)
            # await __websocket_tasks(ws)
            # await __close_websocket(ws)

            async def sse_async_gen() -> AsyncGenerator:
                try:
                    yield str(json_encode({'test': 'prova'}), "utf-8")

                except BaseException as e:
                    logger.info(f"Disconnected from client {req.client}")
                    raise e

            return EventSourceResponse(sse_async_gen())

        else:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    except BaseException as e:
        logger.error("websocket_endpoint", exc_info=True)
        raise e

    # wdg = req.path_params["wdg"]
    # key = req.path_params["key"]
    #
    # channel = f"{wdg}:{key}"
    #
    # async def ev_pub() -> AsyncGenerator:
    #     try:
    #         yield str(orjson.dumps(repository), "utf-8")
    #
    #         async with broadcast.subscribe(channel=channel) as subscriber:
    #             async for event in subscriber:
    #                 yield str(event, "utf-8")
    #
    #     except BaseException as e:
    #         logger.info(f"Disconnected from client {req.client}")
    #         raise e
    #
    # return EventSourceResponse(ev_pub())


routes = [
    Route("/{key:str}", endpoint=sse_endpoint, methods=["POST", "OPTIONS"]),
]
