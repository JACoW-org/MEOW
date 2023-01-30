import asyncio
import logging

from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.exceptions import HTTPException

from jpsp.app.instances.application import app
from jpsp.app.instances.databases import dbs
from jpsp.services.local.credential.find_credential import find_credential_by_secret

from jpsp.utils.serialization import json_encode

logger = logging.getLogger(__name__)


async def publish(message: dict):
    topic_name: str = await __publish_key()

    message_id = await dbs.redis_client.publish(
        channel=topic_name, message=json_encode(message)
    )

    logger.info(f"publish_task {topic_name} {message_id}")


async def __publish_key() -> str:
    counter: int = await dbs.redis_client.incr('workers:stream:counter')

    workers: list[str] = await __workers()
    topic_name: str = workers[counter % len(workers)]

    logger.info(f"publish_key {topic_name} {counter} {workers}")

    return topic_name


async def __workers():

    def client_filter(c) -> bool: 
        return (str(c['name']).startswith('worker_'))

    client_list = await dbs.redis_client.client_list('pubsub')
    
    workers: list[str] = sorted(list(map(
        lambda w: str(w['name']),
        filter(
            client_filter,
            client_list
        )
    )))

    logger.debug(f"__workers {workers} ")

    return workers


async def __ws_to_r_handler(ws: WebSocket):
    """ """

    logger.info("ws_to_r_handler >>> BEGIN")

    try:
        while app.state.webapp_running:
            message = await ws.receive_json(mode="text")
            # logger.debug(message)
            if message:
                # logger.debug(f"ws_to_r {message}")
                await publish(message)

    except WebSocketDisconnect:
        logger.info("ws_to_r_handler >>> DISCONNECTED")
    except RuntimeError:
        logger.error("ws_to_r:exc", exc_info=True)

    logger.info("ws_to_r_handler >>> END")


async def __websocket_tasks(ws: WebSocket, id: str):
    """ """

    done, pending = await asyncio.wait([
        __ws_to_r_handler(ws),
    ], return_when=asyncio.FIRST_COMPLETED)

    # logger.debug(f"Done task: {done}")

    for task in pending:
        try:
            # logger.debug(f"Canceling task: {task}")
            task.cancel()
        except Exception as exc:
            logger.error(exc, exc_info=True)


async def __open_websocket(ws: WebSocket, id: str):
    logger.warning('open_websocket')

    await ws.accept()
    
    # app.active_connections.append(ws)
    app.active_connections[id] = ws


async def __close_websocket(ws: WebSocket, id: str):
    logger.warning('close_websocket')

    # app.active_connections.remove(ws)
    del app.active_connections[id]


async def websocket_endpoint(ws: WebSocket):
    try:
               
        id: str = ws.path_params.get("task_id", None)
        
        assert isinstance(id, str), f"Invalid task_id: {id}"

        # cookie_api_key = ws.cookies.get('X-API-KEY', None)
        # header_api_key = ws.headers.get('X-API-KEY', None)
        # logger.info(f'cookie_api_key->{cookie_api_key}')
        # logger.info(f'header_api_key->{header_api_key}')
        
        # credential = await find_credential_by_secret(
        #     cookie_api_key if cookie_api_key is not None else header_api_key
        # )
        
        api_key: str = ws.path_params.get("api_key", None)
        credential = await find_credential_by_secret(api_key)

        if credential is not None:

            await __open_websocket(ws, id)
            await __websocket_tasks(ws, id)
            await __close_websocket(ws, id)

        else:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    except asyncio.exceptions.CancelledError as e:
        pass
    except BaseException as e:
        logger.error("websocket_endpoint", exc_info=True)
        raise e

routes = [
    WebSocketRoute('/{api_key}/{task_id}', websocket_endpoint)
]
