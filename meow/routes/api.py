import logging as lg

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse

from meow.services.local.credential.find_credential import find_credential_by_secret

from meow.services.local.event.event_api_refs import event_api_refs
from meow.services.local.event.event_api_clear import event_api_clear
from meow.services.local.event.event_api_info import event_api_info

logger = lg.getLogger(__name__)


async def api_root_endpoint() -> JSONResponse:
    return JSONResponse({"method": "root"})


async def api_ping_endpoint(req: Request) -> JSONResponse:
    """Ping endpoint"""

    try:
        headers: dict = req.headers
        params: dict = req.path_params

        event_id, api_key = get_event_id_and_api_key(headers, params)
        credential = await find_credential_by_secret(api_key)

        if not credential:
            # raise HTTPException(status_code=401, detail="Invalid API Key")
            return JSONResponse(content={"error": "Invalid API Key"}, status_code=401)

        return JSONResponse(
            {
                "method": "ping",
                "params": {
                    "user": credential.user,
                    "host": credential.host,
                    "date": credential.date,
                },
            }
        )
    except BaseException as ex:
        return response_for_base_exception(ex)
    except Exception as ex:
        return response_for_exception(ex)


async def api_info_endpoint(req: Request) -> JSONResponse:
    """Info endpoint"""

    try:
        headers: dict = req.headers
        params: dict = req.path_params

        event_id, api_key = get_event_id_and_api_key(headers, params)
        credential = await find_credential_by_secret(api_key)

        if not credential:
            # raise HTTPException(status_code=401, detail="Invalid API Key")
            return JSONResponse(content={"error": "Invalid API Key"}, status_code=401)

        result = await event_api_info(str(event_id))
        params = result.get("value") if result else None
        return JSONResponse({"method": "info", "params": params})
    except BaseException as ex:
        return response_for_base_exception(ex)
    except Exception as ex:
        return response_for_exception(ex)


async def api_clear_endpoint(req: Request) -> JSONResponse:
    """This function clears the subfolders related to the given event id"""

    try:
        headers: dict = req.headers
        params: dict = req.path_params

        event_id, api_key = get_event_id_and_api_key(headers, params)
        credential = await find_credential_by_secret(api_key)

        if not credential:
            return JSONResponse(content={"error": "Invalid API Key"}, status_code=401)

        await event_api_clear(str(event_id))
        return JSONResponse({"method": "clear", "status": "success"})
    except BaseException as ex:
        return response_for_base_exception(ex)
    except Exception as ex:
        return response_for_exception(ex)


async def api_refs_endpoint(req: Request) -> StreamingResponse:
    """This function returns a stream of contributions references"""

    try:
        headers: dict = req.headers
        params: dict = req.path_params

        event_id, api_key = get_event_id_and_api_key(headers, params)
        credential = await find_credential_by_secret(api_key)

        if not credential:
            return JSONResponse(content={"error": "Invalid API Key"}, status_code=401)

        json_body: dict = await req.json()

        event_url: str = str(json_body.get("event_url"))
        indico_token: str = str(json_body.get("indico_token"))

        return StreamingResponse(
            event_api_refs(event_id, event_url, indico_token),
            media_type="application/jsonl",
        )
    except BaseException as ex:
        return response_for_base_exception(ex)
    except Exception as ex:
        return response_for_exception(ex)


def response_for_exception(ex):
    """return a json response for an exception"""

    logger.error(ex, exc_info=True)
    return JSONResponse(content={"error": "Generic error"}, status_code=500)


def response_for_base_exception(ex):
    """return a json response for a base exception"""

    logger.error(ex, exc_info=True)

    ex_arg = ex.args[0]

    if isinstance(ex_arg, dict):
        return JSONResponse(
            content={"error": ex_arg.get("message")}, status_code=ex_arg.get("code")
        )

    return JSONResponse(content={"error": str(ex)}, status_code=500)


def get_event_id_and_api_key(headers: dict, params: dict):
    """ """
    
    event_id: int = int(params.get("event_id", 0))
    api_key: str = str(params.get("api_key", ""))

    if api_key and len(api_key) > 0:
        return event_id, api_key

    auth_header: str = headers.get("Authorization", "Bearer ")

    auth_parts = auth_header.split()

    if len(auth_parts) > 1:
        return event_id, auth_parts[1]

    return event_id, ""


routes = [
    Route(
        "/",
        api_root_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/ping",
        api_ping_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/ping/{api_key}",
        api_ping_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/info/{event_id}",
        api_info_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/info/{event_id}/{api_key}",
        api_info_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/clear/{event_id}",
        api_clear_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/clear/{event_id}/{api_key}",
        api_clear_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/refs/{event_id}",
        api_refs_endpoint,
        methods=["PUT", "OPTIONS"],
    ),
    Route(
        "/refs/{event_id}/{api_key}",
        api_refs_endpoint,
        methods=["PUT", "OPTIONS"],
    ),
]
