import logging as lg

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from meow.services.local.credential.find_credential import find_credential_by_secret

# from meow.services.local.abstract_booklet.create_abstract_booklet \
#     import create_abstract_booklet_from_event

# from meow.services.local.abstract_booklet.export_abstract_booklet \
#     import export_abstract_booklet_to_odt

# from meow.services.local.abstract_booklet.extract_abstract_booklet \
#     import create_abstract_booklet_from_entities

# from meow.services.local.conference.event_pdf_check import event_pdf_check

# from meow.services.local.conference.delete_conference import del_conference_entity
# from meow.services.local.conference.find_conference import get_conference_entity
# from meow.services.local.conference.save_conference import put_conference_entity

# from meow.services.local.credential.find_credential import find_credential_by_secret

# from meow.utils.response import create_json_response, create_json_error_response
# from meow.utils.serialization import json_decode

logger = lg.getLogger(__name__)


async def api_list_endpoint() -> JSONResponse:
    return JSONResponse({'method': 'list'})


async def api_ping_endpoint(req: Request) -> JSONResponse:

    api_key: str = str(req.path_params['api_key'])
    credential = await find_credential_by_secret(api_key)

    if credential is not None:
        return JSONResponse({
            'method': 'ping',
            'params': {
                'id': credential.id
            }
        })

    raise HTTPException(status_code=401, detail="Invalid API Key")


async def api_info_endpoint(req: Request) -> JSONResponse:

    event_id: int = int(req.path_params['event_id'])
    api_key: str = str(req.path_params['api_key'])
    credential = await find_credential_by_secret(api_key)

    if credential is not None:
        return JSONResponse({
            'method': 'info',
            'params': {
                'event_id': event_id,
                'pre_press': True,
                'datacite_json': True,
                'final_proceedings': True,
                'proceedings_archive': True,
            }
        })

    raise HTTPException(status_code=401, detail="Invalid API Key")


# async def api_del_conference(req: Request) -> JSONResponse:
#     """ """
#
#     try:
#         conference_id: str = req.path_params['id']
#
#         await del_conference_entity(conference_id)
#
#         return await create_json_response(
#             ok=True
#         )
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return await create_json_error_response(
#             ok=False, error=error
#         )


# async def api_put_conference(req: Request) -> JSONResponse:
#     """ """
#
#     try:
#         conference_id: str = req.path_params['id']
#
#         logger.info(f'>>> api_put_conference >>> 0')
#
#         conference = await put_conference_entity(conference_id)
#
#         logger.info(f'>>> api_put_conference >>> 1')
#
#         return await create_json_response(
#             ok=True, body=dict(conference)
#         )
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return await create_json_error_response(
#             ok=False, error=error
#         )


# async def api_get_conference(req: Request) -> JSONResponse:
#     """ """
#
#     try:
#
#         credential = await find_credential_by_secret(
#             req.headers.get('X-API-KEY', None)
#         )
#
#         if credential is not None:
#             conference_id: str = req.path_params['id']
#             conference = await get_conference_entity(conference_id)
#
#             if conference is not None:
#                 return await create_json_response(
#                     ok=True, body=dict(conference)
#                 )
#
#             return await create_json_error_response(
#                 ok=False, status_code=404,
#                 error=Exception("Conference not found")
#             )
#
#         return await create_json_error_response(
#             ok=False, status_code=401,
#             error=Exception("Invalid API Key")
#         )
#
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return await create_json_error_response(
#             ok=False, error=error
#         )


# async def api_ab_conference_json(req: Request) -> Response:
#     """ """
#
#     try:
#         conference_id: str = req.path_params['id']
#
#         abstract_booklet = await create_abstract_booklet_from_entities(conference_id)
#
#         return await create_json_response(
#             ok=True, body=abstract_booklet
#         )
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return await create_json_error_response(
#             ok=False, error=error
#         )

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


# async def api_task_event_ab_odt(req: Request) -> Response:
#     """ """
#
#     try:
#
#         params: dict = json_decode(str(await req.body(), 'utf-8'))
#
#         event: dict = params.get('event', dict())
#         cookies: dict = params.get('cookies', dict())
#         settings: dict = params.get('settings', dict())
#
#         abstract_booklet = await create_abstract_booklet_from_event(event, cookies, settings)
#
#         abstract_booklet_odt = export_abstract_booklet_to_odt(abstract_booklet, event, cookies, settings)
#
#         filename: str = f"{event.get('title', '')}_abstract_booklet.odt"
#
#         return StreamingResponse(abstract_booklet_odt,
#                                  headers={
#                                      'Content-Type': 'application/vnd.oasis.opendocument.text',
#                                      'Content-Disposition': f'attachment; filename="{filename}"'
#                                  })
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return Response(
#             status_code=500
#         )


# async def api_task_check_pdf(req: Request) -> Response:
#     """ """
#
#     try:
#
#         params: dict = json_decode(str(await req.body(), 'utf-8'))
#
#         contributions: list[dict] = params.get("contributions", [])
#         cookies: dict = params.get('cookies', dict())
#         settings: dict = params.get('settings', dict())
#
#         event_pdf_report = list()
#
#         async for progress in event_pdf_check(contributions, cookies, settings):
#             event_pdf_report.append(progress)
#
#         return await create_json_response(
#             ok=True, body={'reports': event_pdf_report}
#         )
#
#     except Exception as error:
#         logger.error(error, exc_info=True)
#
#         return await create_json_error_response(
#             ok=False, error=error
#         )


routes = [
    Route('/', api_list_endpoint,
          methods=['GET', 'POST', 'PUT', 'DELETE']),

    Route('/ping/{api_key}', api_ping_endpoint,
          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']),

    Route('/info/{event_id}/{api_key}', api_info_endpoint,
          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']),

    # Obsolete
    # Route('/conference/{id}/del', api_del_conference,
    #       methods=['GET', 'POST', 'PUT', 'DELETE']),
    # Route('/conference/{id}/put', api_put_conference,
    #       methods=['GET', 'POST', 'PUT', 'DELETE']),
    # Route('/conference/{id}/get', api_get_conference,
    #       methods=['GET', 'POST', 'PUT', 'DELETE']),
    # Route('/conference/{id}/ab.json', api_ab_conference_json,
    #       methods=['GET', 'POST', 'PUT', 'DELETE']),

    # API to run event_ab task
    # Route('/task-event-ab.odt', api_task_event_ab_odt,
    #       methods=['PUT']),

    # API to run check_pdf task
    # Route('/task-check-pdf', api_task_check_pdf,
    #       methods=['PUT']),

    # API to create task
    #
    # Route('/task/{code}', api_endpoint,
    #       methods=['GET', 'POST', 'PUT', 'DELETE']),
]
