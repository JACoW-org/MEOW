import asyncio
import logging

from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from jpsp.app.instances.application import app
from jpsp.app.instances.databases import dbs

from jpsp.utils.serialization import json_encode

logger = logging.getLogger(__name__)




async def publish(message: dict):
    topic_name: str = await __publish_key()

    message_id = await dbs.redis_client.publish(
        channel=topic_name, message=json_encode(message)
    )

    logger.debug(f"publish_task {topic_name} {message_id}")

async def __publish_key() -> str:
    counter: int = await dbs.redis_client.incr('workers:stream:counter')

    workers: list[str] = await __workers()
    topic_name: str = workers[counter % len(workers)]

    logger.debug(f"publish_key {topic_name} {counter} {workers}")

    return topic_name

async def __workers():
    
    client_list = await dbs.redis_client.client_list()
    client_filter = lambda c: (str(c['name']).startswith('worker_'))
    
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
        while app.state.running:
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



async def __websocket_tasks(websocket):
    """ """

    done, pending = await asyncio.wait([
        __ws_to_r_handler(websocket),
    ], return_when=asyncio.FIRST_COMPLETED)

    # logger.debug(f"Done task: {done}")

    for task in pending:
        try:
            # logger.debug(f"Canceling task: {task}")
            task.cancel()
        except Exception as exc:
            logger.error(exc, exc_info=True)


async def __open_websocket(websocket: WebSocket):
    logger.warning('open_websocket')

    await websocket.accept()
    app.active_connections.append(websocket)


async def __close_websocket(websocket: WebSocket):
    logger.warning('close_websocket')

    app.active_connections.remove(websocket)


async def websocket_endpoint(websocket: WebSocket):
    try:
        # client_id: str = websocket.path_params["client_id"]
        # assert isinstance(client_id, str) and client_id != "", f"Invalid client_id: {client_id}"

        await __open_websocket(websocket)
        await __websocket_tasks(websocket)
        await __close_websocket(websocket)

    except RuntimeError:
        logger.error("websocket_endpoint", exc_info=True)


routes = [
    WebSocketRoute('/{client_id}', websocket_endpoint)
]
