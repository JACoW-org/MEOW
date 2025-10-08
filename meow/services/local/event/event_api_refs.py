import json
import anyio
import orjson

import logging as lg

from datetime import datetime

from typing import AsyncGenerator
from asyncio import CancelledError

from meow.services.local.event.final_proceedings.collecting_event_sessions_and_contributions import (
    collecting_event_sessions_and_contributions,
)
from meow.services.local.event.common.adapting_final_proceedings import (
    adapting_proceedings,
)
from meow.services.local.event.final_proceedings.generate_contribution_references import (
    contribution_data_factory,
)
from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
)
from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsConfig,
)
from meow.utils.serialization import json_encode


from contextvars import Token
from meow.utils.logger import event_id_var

logger = lg.getLogger(__name__)


async def event_api_refs(
    event_id: str, event_url: str, indico_token: str
) -> AsyncGenerator:
    """ """

    token: Token = None

    try:
        if not event_id or event_id == "":
            # raise BaseException("Invalid event id")
            yield (
                orjson.dumps({"status": 400, "error": "Invalid event id"}).decode()
                + "\n"
            )

        token = event_id_var.set(event_id)

        if not indico_token or indico_token == "":
            # raise BaseException("Invalid indico token")
            yield (
                orjson.dumps({"status": 401, "error": "Invalid indico token"}).decode()
                + "\n"
            )

        ### Final Proceedings
        # config = ProceedingsConfig(
        #     strict_pdf_check=False,
        #     include_event_slides=True,
        #     generate_doi_payload=True,
        #     generate_external_doi_url=True,
        #     generate_hep_payload=True,
        #     include_only_qa_green_contributions=True,
        #     absolute_pdf_link=True,
        #     static_site_type="proceedings",
        # )

        ### Pre Press
        # config = ProceedingsConfig(
        #     strict_pdf_check=False,
        #     include_event_slides=False,
        #     generate_doi_payload=False,
        #     generate_external_doi_url=False,
        #     generate_hep_payload=False,
        #     include_only_qa_green_contributions=False,
        #     absolute_pdf_link=False,
        #     static_site_type="prepress",
        # )

        config = ProceedingsConfig(
            strict_pdf_check=False,
            include_event_slides=False,
            generate_doi_payload=False,
            generate_external_doi_url=False,
            generate_hep_payload=False,
            generate_ref_payload=True,
            include_only_qa_green_contributions=False,
            absolute_pdf_link=False,
            static_site_type="references",
        )

        async for r in _event_api_refs(
            event_id,
            event_url,
            indico_token,
            config,
        ):
            yield orjson.dumps(r).decode() + "\n"

        yield orjson.dumps({"status": 200}).decode() + "\n"

    except GeneratorExit:
        logger.error("Generator Exit")
    except CancelledError:
        logger.error("Task Cancelled")
    except BaseException as ex:
        # logger.error("Generic error", exc_info=True)

        # logger.info("ex.args:")
        # logger.info(orjson.dumps(ex.args).decode())
        # logger.info(ex.args)

        ex_arg = ex.args[0]

        if isinstance(ex_arg, dict):
            yield (
                orjson.dumps(
                    {"status": ex_arg.get("code"), "error": ex_arg.get("message")}
                ).decode()
                + "\n"
            )
        elif isinstance(ex_arg, str):
            yield orjson.dumps({"status": 500, "error": ex_arg}).decode() + "\n"
        else:
            yield (
                orjson.dumps({"status": 500, "error": "Generic error"}).decode() + "\n"
            )
    finally:
        event_id_var.reset(token)


async def _event_api_refs(
    event_id: str, event_url: str, indico_token: str, config: ProceedingsConfig
) -> AsyncGenerator:
    """ """

    [
        event,
        settings,
        sessions,
        contributions,
    ] = await collecting_event_sessions_and_contributions(
        event_id, event_url, indico_token
    )

    # region FILTER
    duplicate_of_alias: str = settings.get("duplicate_of_alias", "duplicate_of")

    cat_publish_alias: str | None = settings.get("cat_publish_alias", "CAT_publish")

    def filter_published_contributions(c: ContributionData) -> bool:
        if config.include_only_qa_green_contributions:
            return c.is_included_in_proceedings
        return c.is_included_in_prepress

    def filter_referenceable_contributions(c: ContributionData) -> bool:
        # schedulate (timeline ora e data)
        is_schedulated: bool = c.is_schedulated()

        # cat_duplicated
        duplicate_of_code: str | None = contribution.duplicate_of_code(
            duplicate_of_alias
        )

        is_deduplicated: bool = not (duplicate_of_code and len(duplicate_of_code) > 0)

        # cat_publish
        is_publish: bool = c.cat_publish(cat_publish_alias)

        logger.info(
            json_encode(
                {
                    "code": c.code,
                    "is_schedulated": is_schedulated,
                    "is_deduplicated": is_deduplicated,
                    "is_publish": is_publish,
                }
            ).decode()
        )

        # is_referenceable
        return is_schedulated and is_deduplicated and is_publish

    # endregion

    proceedings = await adapting_proceedings(
        event, sessions, contributions, [], {}, settings
    )

    # await generate_contribution_references(
    #     proceedings, {}, settings, config, filter_published_contributions
    # )

    # logger.info(f"sessions: {len(sessions)}")
    # logger.info(f"contributions: {len(contributions)}")

    # yield orjson.dumps(event).decode() + "\n"

    # for session in sessions:
    #     yield orjson.dumps(session).decode() + "\n"

    # {
    # "id":"1",
    # "name":"CONF2038",
    # "title":"32nd Full JACoW Conference Name (CONF2038)",
    # "hosted":"CONF2038 was hosted by The Laboratory in Laboratory in City, Prov/State, Country from 4 to 10 May, 2038.",
    # "timezone":"Europe/Warsaw",
    # "editorial":"Editor One (LAB) \nEditor Two (LAB)",
    # "location":"City, Prov/State, Country",
    # "date":"May, 4-10 2038",
    # "isbn":"123-4-56789-012-3",
    # "issn":"1234-5678",
    # "color":"#F39433",
    # "series":"Full JACoW Conference Name",
    # "series_number":"32",
    # "copyright_year":"2038",
    # "site_license_text":"Creative Commons Attribution 4.0",
    # "site_license_url":"https://creativecommons.org/licenses/by/4.0/",
    # "paper_license_icon_url":"https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by.png",
    # "paper_license_text":"Content from this work may be used under the terms of the CC BY 4.0 licence (© 2024). Any distribution of this work must maintain attribution to the author(s), title of the work, publisher, and DOI.",
    # "doi_url":"https://doi.org/10.18429/JACoW-CONF2038",
    # "doi_label":"10.18429/JACoW-CONF2038",
    # "start":"2024-08-18T17:00:00+02:00",
    # "end":"2024-08-23T13:20:00+02:00",
    # "path":"conf2038"
    # }

    yield proceedings.event.as_ref()

    for contribution in proceedings.contributions:
        if filter_referenceable_contributions(contribution):
            contribution_ref = await contribution_data_factory(
                proceedings.event,
                contribution,
                {},
                config,
                filter_published_contributions,
            )

            # logger.info(contribution_ref.code)

            yield contribution_ref.as_ref()

        else:
            logger.warning(f"not_referenceable={contribution.code}")

            # logger.warning(contribution.as_dict())

            logger.warning("\n\n")
