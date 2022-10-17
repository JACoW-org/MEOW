import logging as lg

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.responses import StreamingResponse
from starlette.routing import Route

from jpsp.services.local.conference.abstract_booklet import create_abstract_booklet_from_entities, create_abstract_booklet_from_event, \
    export_abstract_booklet_to_odt

from jpsp.services.local.conference.check_pdf import event_pdf_check

from jpsp.services.local.conference.delete_conference import del_conference_entity
from jpsp.services.local.conference.find_conference import get_conference_entity
from jpsp.services.local.conference.save_conference import put_conference_entity

from jpsp.services.local.credential.find_credential import find_credential_by_secret

from jpsp.utils.response import create_json_response, create_json_error_response
from jpsp.utils.serialization import json_decode

logger = lg.getLogger(__name__)


async def api_list_endpoint() -> JSONResponse:
    return JSONResponse({'code': 'list'})


async def api_endpoint(req: Request) -> JSONResponse:
    code: str = req.path_params['code']

    # await obj.workers_manager.queue.put(code)

    return JSONResponse(dict(code=code))


async def api_del_conference(req: Request) -> JSONResponse:
    """ """

    try:
        conference_id: str = req.path_params['id']

        await del_conference_entity(conference_id)

        return await create_json_response(
            ok=True
        )
    except Exception as error:
        logger.error(error, exc_info=True)

        return await create_json_error_response(
            ok=False, error=error
        )


async def api_put_conference(req: Request) -> JSONResponse:
    """ """

    try:
        conference_id: str = req.path_params['id']

        logger.info(f'>>> api_put_conference >>> 0')

        conference = await put_conference_entity(conference_id)

        logger.info(f'>>> api_put_conference >>> 1')

        return await create_json_response(
            ok=True, body=dict(conference)
        )
    except Exception as error:
        logger.error(error, exc_info=True)

        return await create_json_error_response(
            ok=False, error=error
        )


async def api_get_conference(req: Request) -> JSONResponse:
    """ """

    try:

        credential = await find_credential_by_secret(
            req.headers.get('X-API-Key', None)
        )

        if credential is not None:
            conference_id: str = req.path_params['id']
            conference = await get_conference_entity(conference_id)

            if conference is not None:
                return await create_json_response(
                    ok=True, body=dict(conference)
                )

            return await create_json_error_response(
                ok=False, status_code=404,
                error=Exception("Conference not found")
            )

        return await create_json_error_response(
            ok=False, status_code=401,
            error=Exception("Invalid API Key")
        )

    except Exception as error:
        logger.error(error, exc_info=True)

        return await create_json_error_response(
            ok=False, error=error
        )


async def api_ab_conference_json(req: Request) -> Response:
    """ """

    try:
        conference_id: str = req.path_params['id']

        abstract_booklet = await create_abstract_booklet_from_entities(conference_id)

        return await create_json_response(
            ok=True, body=abstract_booklet
        )
    except Exception as error:
        logger.error(error, exc_info=True)

        return await create_json_error_response(
            ok=False, error=error
        )


# async def api_ab_conference_rtf(req: Request) -> Response:
#     """ """
#
#     try:
#         conference_id: str = req.path_params['id']
#
#         abstract_booklet = await create_abstract_booklet_from_entities(conference_id)
#
#         abstract_booklet_rtf = export_abstract_booklet_to_rtf(abstract_booklet)
#
#         filename: str = f"abstract_booklet_{conference_id}.rtf"
#
#         return StreamingResponse(abstract_booklet_rtf,
#                                  headers={
#                                      'Content-Type': 'application/rtf; charset=UTF-8',
#                                      'Content-Disposition': f'attachment; filename="{filename}"'
#                                  })
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return Response(
#             status_code=500
#         )


async def api_ab_conference_odt(req: Request) -> Response:
    """ """

    try:
        conference_id: str = req.path_params['id']

        abstract_booklet = await create_abstract_booklet_from_entities(conference_id)

        abstract_booklet_odt = export_abstract_booklet_to_odt(abstract_booklet)

        filename: str = f"abstract_booklet_{conference_id}.odt"

        return StreamingResponse(abstract_booklet_odt,
                                 headers={
                                     'Content-Type': 'application/vnd.oasis.opendocument.text',
                                     'Content-Disposition': f'attachment; filename="{filename}"'
                                 })
    except Exception as error:
        logger.error(error, exc_info=True)

        return Response(
            status_code=500
        )


async def api_generate_event_ab_odt(req: Request) -> Response:
    """ """

    try:

        event: dict = json_decode(str(await req.body(), 'utf-8'))

        abstract_booklet = await create_abstract_booklet_from_event(event)

        abstract_booklet_odt = export_abstract_booklet_to_odt(abstract_booklet)

        filename: str = f"{event.get('title', '')}_abstract_booklet.odt"

        return StreamingResponse(abstract_booklet_odt,
                                 headers={
                                     'Content-Type': 'application/vnd.oasis.opendocument.text',
                                     'Content-Disposition': f'attachment; filename="{filename}"'
                                 })
    except Exception as error:
        logger.error(error, exc_info=True)

        return Response(
            status_code=500
        )


async def api_event_pdf_check(req: Request) -> Response:
    """ """

    try:

        params: dict = json_decode(str(await req.body(), 'utf-8'))

        check_pdf_input: list[dict] = params.get("contributions", [])

        event_pdf_report = await event_pdf_check(check_pdf_input)

        return await create_json_response(
            ok=True, body={'reports': event_pdf_report}
        )
        
    except Exception as error:
        logger.error(error, exc_info=True)

        return await create_json_error_response(
            ok=False, error=error
        )


routes = [
    Route('/', api_list_endpoint,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/conference/{id}/del', api_del_conference,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/conference/{id}/put', api_put_conference,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/conference/{id}/get', api_get_conference,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/conference/{id}/ab.json', api_ab_conference_json,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/conference/{id}/ab.odt', api_ab_conference_odt,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
    Route('/generate-event-ab.odt', api_generate_event_ab_odt,
          methods=['PUT']),
    Route('/event-pdf-check', api_event_pdf_check,
          methods=['PUT']),
    Route('/task/{code}', api_endpoint,
          methods=['GET', 'POST', 'PUT', 'DELETE']),
]
