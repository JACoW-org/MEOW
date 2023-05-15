from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import AffiliationData, AttachmentData, EventData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.track_model import TrackData

from meow.tasks.local.doi.models import ContributionDOI


from jinja2 import Environment, FileSystemLoader, select_autoescape


from datetime import datetime
import logging as lg

from os import path
from jinja2 import BytecodeCache

import minify_html
from meow.utils.collections import (get_authors_initials_dict, get_institutes_initials_dict,
    get_keywords_initials_dict, group_authors_by_last_initial_for_render,
    group_institutes_by_initial, group_keywords_by_initial)


logger = lg.getLogger(__name__)


class FileSystemCache(BytecodeCache):

    def __init__(self, directory):
        from pathlib import Path
        Path(directory).mkdir(parents=True, exist_ok=True)

        self.directory = directory

    def load_bytecode(self, bucket):
        filename = path.join(self.directory, bucket.key)
        if path.exists(filename):
            with open(filename, 'rb') as f:
                bucket.load_bytecode(f)

    def dump_bytecode(self, bucket):
        filename = path.join(self.directory, bucket.key)
        with open(filename, 'wb') as f:
            bucket.write_bytecode(f)


class JinjaTemplateRenderer:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            auto_reload=False,
            cache_size=1024,
            autoescape=select_autoescape(),
            bytecode_cache=FileSystemCache("var/cache/final_proceedings"),
            loader=FileSystemLoader("jinja/final_proceedings"),
        )

    async def render(self, name: str, args: dict, minify: bool = False) -> str:
        html = await self.env.get_template(name).render_async(args)
        return html if minify == False else minify_html.minify(
            html, remove_processing_instructions=True)

    async def render_config_toml(self, event: EventData, attachments: list[AttachmentData], settings: dict) -> str:
        return await self.render("config.toml.jinja", dict(
            event=event.as_dict(),
            settings=settings,
            attachments=[a.as_dict() for a in attachments],
        ))

    async def render_home_page(self, event: EventData, attachments: list[AttachmentData], volume_size: int, brief_size: int) -> str:
        return await self.render("home_page.html.jinja", minify=True, args=dict(
            event=event.as_dict(),
            attachments=[a.as_dict() for a in attachments],
            volume_size=volume_size,
            brief_size=brief_size,
            datetime_now=datetime.now()
        ))

    async def render_contribution_partial(self, contribution: ContributionData) -> str:
        return await self.render("contribution_partial.html.jinja", minify=True, args=dict(
            contribution=contribution.as_dict()
        ))

    async def render_session_partial(self, sessions: list[SessionData]) -> str:
        return await self.render("session_partial.html.jinja", minify=True, args=dict(
            sessions=[s.as_dict() for s in sessions]
        ))

    async def render_session_page(self, event: EventData, session: SessionData, contributions: list[ContributionData]) -> str:
        return await self.render("session_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            session=session.as_dict(),
            contributions=[c.as_dict() for c in contributions]
        ))

    async def render_classification_partial(self, classifications: list[TrackData]) -> str:
        return await self.render("classification_partial.html.jinja", minify=True, args=dict(
            classifications=[s.as_dict() for s in classifications]
        ))

    async def render_classification_page(self, event: EventData, classification: TrackData, contributions: list[ContributionData]) -> str:
        return await self.render("classification_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            classification=classification.as_dict(),
            contributions=[c.as_dict() for c in contributions]
        ))

    async def render_author_partial(self, authors: list[PersonData]) -> str:
        return await self.render("author_partial.html.jinja", minify=True, args=dict(
            initials=get_authors_initials_dict(authors),
            authors_groups=group_authors_by_last_initial_for_render(authors)
        ))

    async def render_author_page(self, event: EventData, author: PersonData, contributions: list[ContributionData]) -> str:
        return await self.render("author_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            author=author.as_dict(),
            contributions=[c.as_dict() for c in contributions]
        ))

    async def render_institute_partial(self, institutes: list[AffiliationData], authorsGroups: dict[str, list[dict]]) -> str:
        return await self.render("institute_partial.html.jinja", minify=True, args=dict(
            authorsGroups=authorsGroups,
            institutes_groups=group_institutes_by_initial(institutes),
            initials=get_institutes_initials_dict(institutes)
        ))

    async def render_institute_page(self, event: EventData, institute: AffiliationData, author: PersonData, contributions: list[ContributionData]) -> str:
        return await self.render("institute_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            author=author.as_dict(),
            contributions=[c.as_dict() for c in contributions],
        ))

    async def render_institute_author_page(self, event: EventData, institute: AffiliationData, author: PersonData, contributions: list[ContributionData]) -> str:
        return await self.render("institute_author_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            author=author.as_dict(),
            contributions=[c.as_dict() for c in contributions],
        ))

    async def render_keyword_partial(self, keywords: list[KeywordData]) -> str:
        return await self.render("keyword_partial.html.jinja", minify=True, args=dict(
            initials=get_keywords_initials_dict(keywords),
            keywords_groups=group_keywords_by_initial(keywords)
        ))

    async def render_keyword_page(self, event: EventData, keyword: KeywordData, contributions: list[ContributionData]) -> str:
        return await self.render("keyword_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            keyword=keyword.as_dict(),
            contributions=[c.as_dict() for c in contributions]
        ))

    async def render_doi_per_institute_list(self, institutes: list[AffiliationData]) -> str:
        return await self.render("doi_per_institute_list.html.jinja", minify=False, args=dict(
            institutes=[s.as_dict() for s in institutes]
        ))

    async def render_doi_per_institute_partial(self, institutes: list[AffiliationData], contributionsGroups: dict[str, list[dict]]) -> str:
        return await self.render("doi_per_institute_partial.html.jinja", minify=True, args=dict(
            institutes=[s.as_dict() for s in institutes],
            contributionsGroups=contributionsGroups
        ))

    async def render_doi_per_institute_page(self, event: EventData, institute: AffiliationData, contribution: ContributionData) -> str:
        return await self.render("doi_per_institute_page.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            contribution=contribution.as_dict()
        ))

    async def render_doi_list(self, event: EventData, contributions: list[ContributionData]):
        return await self.render("doi_list.html.jinja", minify=False, args=dict(
            event=event.as_dict(),
            contributions=[c.as_dict() for c in contributions]
        ))

    async def render_doi_contribution(self, contribution: ContributionDOI) -> str:
        return await self.render("doi_page.html.jinja", minify=False, args=dict(
            contribution=contribution.as_dict()
        ))

    async def render_doi_partial(self, event: EventData, contribution: ContributionDOI) -> str:
        return await self.render("doi_partial.html.jinja", minify=True, args=dict(
            event=event.as_dict(),
            contribution=contribution.as_dict()
        ))

    async def render_reference(self, contribution_code: str, contribution_title: str,
                               reference_type: str, reference: str) -> str:
        return await self.render("reference_base.html.jinja", minify=False, args=dict(
            contribution_code=contribution_code,
            contribution_title=contribution_title,
            reference_type=reference_type,
            reference=reference
        ))
