import asyncio
import logging

from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from jpsp.app.instances.application import app
from jpsp.app.instances.services import srs

logger = logging.getLogger(__name__)


async def __ws_to_r_handler(ws: WebSocket):
    """ """

    logger.info("ws_to_r_handler >>> BEGIN")

    try:
        while app.state.running:
            message = await ws.receive_json(mode="text")
            # logger.debug(message)
            if message:
                logger.debug(f"ws_to_r {message}")
                await srs.workers_manager.publish(message)

    except WebSocketDisconnect:
        logger.info("ws_to_r_handler >>> DISCONNECTED")
    except RuntimeError:
        logger.error("ws_to_r:exc", exc_info=True)

    logger.info("ws_to_r_handler >>> END")


async def __r_to_ws_handler(ws: WebSocket):
    """ """

    logger.info("r_to_ws_handler >>> BEGIN")

    await srs.ws_manager.subscribe()

    logger.info("r_to_ws_handler >>> END")


async def __websocket_tasks(websocket):
    """ """

    done, pending = await asyncio.wait([
        __ws_to_r_handler(websocket),
        # __r_to_ws_handler(websocket)
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
    await srs.ws_manager.connect(websocket)


async def __close_websocket(websocket: WebSocket):
    logger.warning('close_websocket')

    await srs.ws_manager.disconnect(websocket)


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
