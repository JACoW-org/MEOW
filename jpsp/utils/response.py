import datetime as dt
from typing import Any

import ujson as uj

from starlette.background import BackgroundTask
from starlette.responses import FileResponse
from starlette.responses import JSONResponse

from jpsp.utils.error import exception_to_string


class UJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        def default(o: Any) -> str | None:
            return o.isoformat() if isinstance(o, (dt.date, dt.datetime)) else None

        return uj.dumps(content,
                        sort_keys=True,
                        indent=1,
                        default=default  # type: ignore
                        ).encode("utf-8")


async def create_json_response(ok: bool, body: dict | None = None, status_code: int = 200) -> JSONResponse:
    return UJSONResponse(dict(ok=ok, body=body), status_code)

async def create_json_error_response(ok: bool, error: Exception | None = None, status_code: int = 400) -> JSONResponse:
    return UJSONResponse(dict(ok=ok, error=exception_to_string(error)), status_code=status_code)

async def create_file_response(path: str, filename: str, task: BackgroundTask) -> FileResponse:
    return FileResponse(path=path, filename=filename, background=task)
