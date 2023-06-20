import logging as lg
from typing import Any

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream
from meow.app.errors.service_error import ServiceError
from meow.models.local.common.auth import BasicAuthData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.tasks.local.doi.utils import generate_doi_identifier

from meow.utils.http import put_json
from meow.utils.serialization import json_decode, json_encode


logger = lg.getLogger(__name__)


async def hide_contribution_doi(proceedings_data: ProceedingsData, cookies: dict, settings: dict):
    """ """

    logger.info('hide_contribution_doi - hide_contribution_doi')

    doi_dir = Path('var', 'run', f'{proceedings_data.event.id}_doi')
    dir_exists = await doi_dir.exists()
    if not dir_exists:
        raise ServiceError("doi_dir not exists")

    results: list[dict] = []

    contributions_data: list[ContributionData] = [
        c for c in proceedings_data.contributions
    ]

    total_contributions: int = len(contributions_data)

    logger.info(f'hide_contribution_doi - ' +
                f'contributions: {total_contributions}')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_contribution in enumerate(contributions_data):
                tg.start_soon(_doi_task, capacity_limiter, total_contributions,
                              current_index, current_contribution, cookies, settings,
                              doi_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:

                    results.append(result)

                    logger.info(f"elaborated: {len(results)}" +
                                f" - {total_contributions}")
                    
                    yield result

                    if len(results) >= total_contributions:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except BaseException as ex:
            logger.error(ex, exc_info=True)


async def _doi_task(capacity_limiter: CapacityLimiter, total: int, index: int,
                    contribution: ContributionData, cookies: dict, settings: dict,
                    doi_dir: Path, stream: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        response: str | None = None
        error: str | None = None

        try:

            doi_file = Path(doi_dir, f'{contribution.code}.json')

            doi_exists = await doi_file.exists()

            if doi_exists:

                logger.info(str(doi_file))

                doi_raw = await doi_file.read_text()
                
                doi_dict = json_decode(doi_raw)

                # {
                #  "data": {
                #    "type": "dois",
                #    "attributes": {
                #      "event": "publish",
                #      "doi": "10.5438/0012",
                #      "url": "https://schema.datacite.org/meta/kernel-4.0/index.html",
                #      "xml": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4NCjxyZXNvdXJjZSB4bWxucz0iaHR0cDovL2RhdGFjaXRlLm9yZy9zY2hlbWEva2VybmVsLTQiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTpzY2hlbWFMb2NhdGlvbj0iaHR0cDovL2RhdGFjaXRlLm9yZy9zY2hlbWEva2VybmVsLTQgaHR0cDovL3NjaGVtYS5kYXRhY2l0ZS5vcmcvbWV0YS9rZXJuZWwtNC9tZXRhZGF0YS54c2QiPg0KCTxpZGVudGlmaWVyIGlkZW50aWZpZXJUeXBlPSJET0kiPjEwLjU0MzgvMDAxMjwvaWRlbnRpZmllcj4NCgk8Y3JlYXRvcnM+DQoJCTxjcmVhdG9yPg0KCQkJPGNyZWF0b3JOYW1lPkRhdGFDaXRlIE1ldGFkYXRhIFdvcmtpbmcgR3JvdXA8L2NyZWF0b3JOYW1lPg0KCQk8L2NyZWF0b3I+DQoJPC9jcmVhdG9ycz4NCgk8dGl0bGVzPg0KCQk8dGl0bGU+RGF0YUNpdGUgTWV0YWRhdGEgU2NoZW1hIERvY3VtZW50YXRpb24gZm9yIHRoZSBQdWJsaWNhdGlvbiBhbmQgQ2l0YXRpb24gb2YgUmVzZWFyY2ggRGF0YSB2NC4wPC90aXRsZT4NCgk8L3RpdGxlcz4NCgk8cHVibGlzaGVyPkRhdGFDaXRlIGUuVi48L3B1Ymxpc2hlcj4NCgk8cHVibGljYXRpb25ZZWFyPjIwMTY8L3B1YmxpY2F0aW9uWWVhcj4NCgk8Y29udHJpYnV0b3JzPg0KCQk8Y29udHJpYnV0b3IgY29udHJpYnV0b3JUeXBlPSJQcm9qZWN0TGVhZGVyIj4NCgkJCTxjb250cmlidXRvck5hbWU+U3RhcnIsIEpvYW48L2NvbnRyaWJ1dG9yTmFtZT4NCgkJCTxnaXZlbk5hbWU+Sm9hbjwvZ2l2ZW5OYW1lPg0KCQkJPGZhbWlseU5hbWU+U3RhcnI8L2ZhbWlseU5hbWU+DQoJCQk8bmFtZUlkZW50aWZpZXIgbmFtZUlkZW50aWZpZXJTY2hlbWU9Ik9SQ0lEIiBzY2hlbWVVUkk9Imh0dHA6Ly9vcmNpZC5vcmciPjAwMDAtMDAwMi03Mjg1LTAyN1g8L25hbWVJZGVudGlmaWVyPg0KCQkJPGFmZmlsaWF0aW9uPkNhbGlmb3JuaWEgRGlnaXRhbCBMaWJyYXJ5PC9hZmZpbGlhdGlvbj4NCgkJPC9jb250cmlidXRvcj4NCgkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iUHJvamVjdExlYWRlciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPlNtYWVsZSwgTWFkZWxlaW5lIGRlPC9jb250cmlidXRvck5hbWU+DQoJCQk8Z2l2ZW5OYW1lPk1hZGVsZWluZSBkZTwvZ2l2ZW5OYW1lPg0KCQkJPGZhbWlseU5hbWU+U21hZWxlPC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPlRVIERlbGZ0PC9hZmZpbGlhdGlvbj4NCgkJPC9jb250cmlidXRvcj4NCgkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iRWRpdG9yIj4NCgkJCTxjb250cmlidXRvck5hbWU+QXNodG9uLCBKYW48L2NvbnRyaWJ1dG9yTmFtZT4NCgkJCTxnaXZlbk5hbWU+SmFuPC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5Bc2h0b248L2ZhbWlseU5hbWU+DQoJCQk8YWZmaWxpYXRpb24+QnJpdGlzaCBMaWJyYXJ5PC9hZmZpbGlhdGlvbj4NCgkJPC9jb250cmlidXRvcj4NCgkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iRWRpdG9yIj4NCgkJCTxjb250cmlidXRvck5hbWU+QmFydG9uLCBBbXk8L2NvbnRyaWJ1dG9yTmFtZT4NCgkJCTxnaXZlbk5hbWU+QW15PC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5CYXJ0b248L2ZhbWlseU5hbWU+DQoJCQk8YWZmaWxpYXRpb24+UHVyZHVlIFVuaXZlcnNpdHkgTGlicmFyeTwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPkJyYWRmb3JkLCBUaW5hPC9jb250cmlidXRvck5hbWU+DQoJCQk8Z2l2ZW5OYW1lPlRpbmE8L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPkJyYWRmb3JkPC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPk5SQy9DSVNUSTwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPkNpb2xla+KAkEZpZ2llbCwgQW5uZTwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5Bbm5lPC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5DaW9sZWstRmlnaWVsPC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPkluaXN04oCQQ05SUzwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPkRpZXRpa2VyLCBTdGVmYW5pZTwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5TdGVmYW5pZTwvZ2l2ZW5OYW1lPg0KCQkJPGZhbWlseU5hbWU+RGlldGlrZXI8L2ZhbWlseU5hbWU+DQoJCQk8YWZmaWxpYXRpb24+RVRIIFrDvHJpY2g8L2FmZmlsaWF0aW9uPg0KCQk8L2NvbnRyaWJ1dG9yPg0KCQk8Y29udHJpYnV0b3IgY29udHJpYnV0b3JUeXBlPSJFZGl0b3IiPg0KCQkJPGNvbnRyaWJ1dG9yTmFtZT5FbGxpb3R0LCBKYW5uZWFuPC9jb250cmlidXRvck5hbWU+DQoJCQk8Z2l2ZW5OYW1lPkphbm5lYW48L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPkVsbGlvdDwvZmFtaWx5TmFtZT4NCgkJCTxhZmZpbGlhdGlvbj5ET0UvT1NUSTwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPkdlbmF0LCBCZXJyaXQ8L2NvbnRyaWJ1dG9yTmFtZT4NCgkJCTxnaXZlbk5hbWU+QmVycml0PC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5HZW5hdDwvZmFtaWx5TmFtZT4NCgkJCTxhZmZpbGlhdGlvbj5USUI8L2FmZmlsaWF0aW9uPg0KCQk8L2NvbnRyaWJ1dG9yPg0KCQk8Y29udHJpYnV0b3IgY29udHJpYnV0b3JUeXBlPSJFZGl0b3IiPg0KCQkJPGNvbnRyaWJ1dG9yTmFtZT5IYXJ6ZW5ldHRlciwgS2Fyb2xpbmU8L2NvbnRyaWJ1dG9yTmFtZT4NCgkJCTxnaXZlbk5hbWU+S2Fyb2xpbmU8L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPkhhcnplbmV0dGVyPC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPkdFU0lTPC9hZmZpbGlhdGlvbj4NCgkJPC9jb250cmlidXRvcj4NCgkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iRWRpdG9yIj4NCgkJCTxjb250cmlidXRvck5hbWU+SGlyc2NobWFubiwgQmFyYmFyYTwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5CYXJiYXJhPC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5IaXJzY2htYW5uPC9mYW1pbHlOYW1lPg0KCQkJPG5hbWVJZGVudGlmaWVyIG5hbWVJZGVudGlmaWVyU2NoZW1lPSJPUkNJRCIgc2NoZW1lVVJJPSJodHRwOi8vb3JjaWQub3JnIj4wMDAwLTAwMDMtMDI4OS0wMzQ1PC9uYW1lSWRlbnRpZmllcj4NCgkJCTxhZmZpbGlhdGlvbj5FVEggWsO8cmljaDwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPkpha29ic3NvbiwgU3RlZmFuPC9jb250cmlidXRvck5hbWU+DQoJCQk8Z2l2ZW5OYW1lPlN0ZWZhbjwvZ2l2ZW5OYW1lPg0KCQkJPGZhbWlseU5hbWU+SmFrb2Jzc29uPC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPlNORDwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPk1haWxsb3V4LCBKZWFu4oCQWXZlczwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5KZWFuLVl2ZXM8L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPk1haWxsb3V4PC9mYW1pbHlOYW1lPg0KCQkJPGFmZmlsaWF0aW9uPk5SQy9DSVNUSTwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCTxjb250cmlidXRvciBjb250cmlidXRvclR5cGU9IkVkaXRvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPk5ld2JvbGQsIEVsaXphYmV0aDwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5FbGl6YWJldGg8L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPk5ld2JvbGQ8L2ZhbWlseU5hbWU+DQoJCQk8bmFtZUlkZW50aWZpZXIgbmFtZUlkZW50aWZpZXJTY2hlbWU9Ik9SQ0lEIiBzY2hlbWVVUkk9Imh0dHA6Ly9vcmNpZC5vcmciPjAwMDAtMDAwMi04MjU1LTkwMTM8L25hbWVJZGVudGlmaWVyPg0KCQkJPGFmZmlsaWF0aW9uPkJyaXRpc2ggTGlicmFyeTwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJCQkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iRWRpdG9yIj4NCgkJCTxjb250cmlidXRvck5hbWU+TmllbHNlbiwgTGFycyBIb2xtIDwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5MYXJzIEhvbG08L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPk5pZWxzZW48L2ZhbWlseU5hbWU+DQoJCQk8bmFtZUlkZW50aWZpZXIgbmFtZUlkZW50aWZpZXJTY2hlbWU9Ik9SQ0lEIiBzY2hlbWVVUkk9Imh0dHA6Ly9vcmNpZC5vcmciPjAwMDAtMDAwMS04MTM1LTM0ODk8L25hbWVJZGVudGlmaWVyPg0KCQkJPGFmZmlsaWF0aW9uPkNFUk48L2FmZmlsaWF0aW9uPg0KCQk8L2NvbnRyaWJ1dG9yPg0KCQk8Y29udHJpYnV0b3IgY29udHJpYnV0b3JUeXBlPSJFZGl0b3IiPg0KCQkJPGNvbnRyaWJ1dG9yTmFtZT5ZYWhpYSwgTW9oYW1lZDwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5Nb2hhbWVkPC9naXZlbk5hbWU+DQoJCQk8ZmFtaWx5TmFtZT5ZYWhpYTwvZmFtaWx5TmFtZT4NCgkJCTxhZmZpbGlhdGlvbj5JbmlzdC1DTlJTPC9hZmZpbGlhdGlvbj4NCgkJPC9jb250cmlidXRvcj4NCgkJPGNvbnRyaWJ1dG9yIGNvbnRyaWJ1dG9yVHlwZT0iU3VwZXJ2aXNvciI+DQoJCQk8Y29udHJpYnV0b3JOYW1lPlppZWRvcm4sIEZyYXVrZTwvY29udHJpYnV0b3JOYW1lPg0KCQkJPGdpdmVuTmFtZT5GcmF1a2U8L2dpdmVuTmFtZT4NCgkJCTxmYW1pbHlOYW1lPlppZWRvcm48L2ZhbWlseU5hbWU+DQoJCQk8bmFtZUlkZW50aWZpZXIgbmFtZUlkZW50aWZpZXJTY2hlbWU9Ik9SQ0lEIiBzY2hlbWVVUkk9Imh0dHA6Ly9vcmNpZC5vcmciPjAwMDAtMDAwMi0xMTQzLTc4MVg8L25hbWVJZGVudGlmaWVyPg0KCQkJPGFmZmlsaWF0aW9uPlRJQjwvYWZmaWxpYXRpb24+DQoJCTwvY29udHJpYnV0b3I+DQoJPC9jb250cmlidXRvcnM+DQoJPGxhbmd1YWdlPmVuZzwvbGFuZ3VhZ2U+DQoJPHJlc291cmNlVHlwZSByZXNvdXJjZVR5cGVHZW5lcmFsPSJUZXh0Ij5Eb2N1bWVudGF0aW9uPC9yZXNvdXJjZVR5cGU+DQoJPHJlbGF0ZWRJZGVudGlmaWVycz4NCgkJPHJlbGF0ZWRJZGVudGlmaWVyIHJlbGF0ZWRJZGVudGlmaWVyVHlwZT0iRE9JIiByZWxhdGlvblR5cGU9IkRvY3VtZW50cyI+MTAuNTQzOC8wMDEzPC9yZWxhdGVkSWRlbnRpZmllcj4NCgkJPHJlbGF0ZWRJZGVudGlmaWVyIHJlbGF0ZWRJZGVudGlmaWVyVHlwZT0iRE9JIiByZWxhdGlvblR5cGU9IklzTmV3VmVyc2lvbk9mIj4xMC41NDM4LzAwMTA8L3JlbGF0ZWRJZGVudGlmaWVyPg0KCTwvcmVsYXRlZElkZW50aWZpZXJzPg0KCTxzaXplcz4NCgkJPHNpemU+NDUgcGFnZXM8L3NpemU+DQoJPC9zaXplcz4NCgk8Zm9ybWF0cz4NCgkJPGZvcm1hdD5hcHBsaWNhdGlvbi9wZGY8L2Zvcm1hdD4NCgk8L2Zvcm1hdHM+DQoJPHZlcnNpb24+NC4wPC92ZXJzaW9uPg0KCTxkZXNjcmlwdGlvbnM+DQoJCTxkZXNjcmlwdGlvbiBkZXNjcmlwdGlvblR5cGU9IlRhYmxlT2ZDb250ZW50cyI+MSBJbnRyb2R1Y3Rpb248YnIvPg0KMS4xIFRoZSBEYXRhQ2l0ZSBDb25zb3J0aXVtPGJyLz4NCjEuMiBEYXRhQ2l0ZSBDb21tdW5pdHkgUGFydGljaXBhdGlvbjxici8+DQoxLjMgVGhlIE1ldGFkYXRhIFNjaGVtYTxici8+DQoxLjQgVmVyc2lvbiA0LjAgVXBkYXRlPGJyLz4NCjIgRGF0YUNpdGUgTWV0YWRhdGEgUHJvcGVydGllczxici8+DQoyLjEgT3ZlcnZpZXc8YnIvPg0KMi4yIENpdGF0aW9uPGJyLz4NCjIuMyBEYXRhQ2l0ZSBQcm9wZXJ0aWVzPGJyLz4NCjMgWE1MIEV4YW1wbGU8YnIvPg0KNCBYTUwgU2NoZW1hPGJyLz4NCjUgT3RoZXIgRGF0YUNpdGUgU2VydmljZXM8YnIvPg0KQXBwZW5kaWNlczxici8+DQpBcHBlbmRpeCAxOiBDb250cm9sbGVkIExpc3QgRGVmaW5pdGlvbnM8YnIvPg0KQXBwZW5kaXggMjogRWFybGllciBWZXJzaW9uIFVwZGF0ZSBOb3RlczwvZGVzY3JpcHRpb24+DQoJPC9kZXNjcmlwdGlvbnM+DQo8L3Jlc291cmNlPg0K"
                #  }
                # }

                attributes = doi_dict.get('data', {}).get('attributes', {})
                attributes['event'] = 'hide'

                doi_json = json_encode(doi_dict).decode('utf-8')

                doi_identifier: str = generate_doi_identifier(
                    context=settings.get('doi_context', '10.18429'),
                    organization=settings.get('doi_organization', 'JACoW'),
                    conference=settings.get('doi_conference', 'CONF-YY'),
                    contribution=contribution.code
                )

                proto = f"https:"
                host = f"api.test.datacite.org"
                context = f"dois"
                path = f"{doi_identifier}"

                doi_url = f"{proto}//{host}/{context}/{path}".lower()

                logger.info(f"{doi_file} -> {doi_url}")

                # logger.info(doi_data)
                # logger.info(doi_json)

                auth = BasicAuthData(login='CERN.JACOW',
                                     password='DataCite.cub-gwd')

                headers = {'Content-Type': 'application/vnd.api+json'}

                response = await put_json(url=doi_url, data=doi_json, headers=headers, auth=auth)

        except BaseException as ex:
            error = str(ex)
            logger.error(ex, exc_info=True)

        await send_res(stream, total, index, contribution, response=response, error=error)


async def send_res(stream: MemoryObjectSendStream, total: int, index: int, contribution: ContributionData, response: Any, error=None):
    doi = response.get('data', None) if response else None

    await stream.send({
        "total": total,
        "index": index,
        "code": contribution.code,
        "doi": doi,
        "error": error
    })
