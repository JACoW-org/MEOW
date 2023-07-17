from asyncio import CancelledError, create_task
import logging
import time
from anyio import sleep

from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.exceptions import HTTPException

from meow.app.instances.application import app
from meow.app.instances.databases import dbs
from meow.services.local.credential.find_credential import (
    find_credential_by_secret)
from meow.utils.error import exception_to_string

from meow.utils.serialization import json_encode

logger = logging.getLogger(__name__)


async def publish(message: dict, task_id: str) -> str:
    topic_name: str = await __publish_key()

    message_id = await dbs.redis_client.publish(
        channel=topic_name, message=json_encode(message)
    )

    logger.debug(f"publish_task {topic_name} {task_id} {message_id}")

    return topic_name


async def kill(topic_name: str, task_id: str) -> None:
    message_id = await dbs.redis_client.publish(
        channel=topic_name, message=json_encode(dict(
            head=dict(
                code='task:kill',
                uuid=task_id,
            )
        ))
    )

    logger.debug(f"kill_task {topic_name} {task_id} {message_id}")


async def __publish_key() -> str:
    counter: int = await dbs.redis_client.incr('workers:stream:counter')

    workers: list[str] = await __workers()

    if len(workers) == 0:
        raise Exception("No PURR worker available.")

    topic_name: str = workers[counter % len(workers)]

    logger.debug(f"publish_key {topic_name} {counter} {workers}")

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


async def __websocket_error(ws: WebSocket, uuid: str, error: BaseException):
    try:

        to_send = {
            'head': {
                'code': 'task:error',
                'uuid': uuid,
                'time': int(time.time())
            },
            'body': {
                'method': '',
                'params': exception_to_string(error)
            }
        }

        logger.debug(f"send {to_send}")

        await ws.send_json(to_send)

    except BaseException as e:
        logger.error(e, exc_info=True)


async def __websocket_task(ws: WebSocket, id: str) -> None:
    """ """

    logger.debug("__websocket_task >>> BEGIN")

    worker: str = ''
    connected: bool = True

    async def monitor():
        logger.debug(f"start_monitor_{id}")

        while app.state.webapp_running and connected:

            if worker != '':

                exists = worker in (await __workers())

                logger.debug(f"check {worker} {exists}")

                if not exists:
                    await ws.close()
                    break

            await sleep(2)

        logger.debug(f"stop_monitor_{id}")

    monitor_task = create_task(monitor(), name=f"monitor_task_{id}")

    try:
        while app.state.webapp_running:
            message = await ws.receive_json(mode="text")

            # logger.warning(message)

            if message:
                # logger.debug(f"ws_to_r {message}")
                try:
                    worker = await publish(message, id)
                except BaseException as e:
                    logger.error("__websocket_task", e, exc_info=True)
                    await __websocket_error(ws, id, e)

    except WebSocketDisconnect:
        logger.info("__websocket_task >>> DISCONNECTED")
    except BaseException:
        logger.error("__websocket_task", exc_info=True)
    finally:
        try:
            connected = False
            monitor_task.cancel()
            # await kill(worker, id)
        except BaseException as e:
            logger.error("__websocket_task", e, exc_info=True)

    logger.warning("__websocket_task >>> END")


async def __open_websocket(ws: WebSocket, id: str):
    logger.info('open_websocket')

    await ws.accept()

    # app.active_connections.append(ws)
    app.active_connections[id] = ws


async def __close_websocket(ws: WebSocket, id: str):
    logger.info('close_websocket')

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
            await __websocket_task(ws, id)
            await __close_websocket(ws, id)

        else:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    except CancelledError as ce:
        logger.debug(ce, exc_info=False)
    except BaseException as be:
        logger.error("websocket_endpoint", be, exc_info=True)
        raise be

routes = [
    WebSocketRoute('/{api_key}/{task_id}', websocket_endpoint)
]
