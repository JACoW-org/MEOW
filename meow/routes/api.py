import logging as lg

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse
from starlette.exceptions import HTTPException

from meow.services.local.credential.find_credential import find_credential_by_secret

from meow.services.local.event.event_api_refs import event_api_refs
from meow.services.local.event.event_api_clear import event_api_clear
from meow.services.local.event.event_api_info import event_api_info

logger = lg.getLogger(__name__)


async def api_root_endpoint() -> JSONResponse:
    return JSONResponse({"method": "root"})


async def api_ping_endpoint(req: Request) -> JSONResponse:
    api_key: str = str(req.path_params["api_key"])
    credential = await find_credential_by_secret(api_key)

    if credential:
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

    raise HTTPException(status_code=401, detail="Invalid API Key")


async def api_info_endpoint(req: Request) -> JSONResponse:
    event_id: int = int(req.path_params["event_id"])
    api_key: str = str(req.path_params["api_key"])
    credential = await find_credential_by_secret(api_key)

    if credential:
        result = await event_api_info(str(event_id))
        params = result.get("value") if result else None

        return JSONResponse({"method": "info", "params": params})

    raise HTTPException(status_code=401, detail="Invalid API Key")


async def api_clear_endpoint(req: Request) -> JSONResponse:
    """This function clears the subfolders related to the given event id"""

    event_id: int = int(req.path_params["event_id"])
    api_key: str = str(req.path_params["api_key"])
    credential = await find_credential_by_secret(api_key)

    if credential:
        await event_api_clear(str(event_id))

        return JSONResponse({"method": "clear", "status": "success"})

    raise HTTPException(status_code=401, detail="Invalid API Key")


async def api_refs_endpoint(req: Request) -> StreamingResponse:
    """This function returns a stream of contributions references"""

    event_id: int = int(req.path_params["event_id"])
    api_key: str = str(req.path_params["api_key"])
    credential = await find_credential_by_secret(api_key)

    if credential:
        json_body: dict = await req.json()

        event_url: str = str(json_body.get("event_url"))
        indico_token: str = str(json_body.get("indico_token"))

        return StreamingResponse(
            event_api_refs(event_id, event_url, indico_token),
            media_type="application/jsonl",
        )

    raise HTTPException(status_code=401, detail="Invalid API Key")


routes = [
    Route(
        "/",
        api_root_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/ping/{api_key}",
        api_ping_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/info/{event_id}/{api_key}",
        api_info_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/clear/{event_id}/{api_key}",
        api_clear_endpoint,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/refs/{event_id}/{api_key}",
        api_refs_endpoint,
        methods=["PUT", "OPTIONS"],
    ),
]
