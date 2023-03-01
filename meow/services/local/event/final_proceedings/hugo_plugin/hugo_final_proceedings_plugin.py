import logging as lg

from os import path

from io import BytesIO
from anyio import Path, run_process, create_task_group

from jinja2 import Environment, select_autoescape, FileSystemLoader, BytecodeCache

from meow.models.local.event.final_proceedings.track_model import TrackData

from anyio import create_task_group, CapacityLimiter, to_process

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import AffiliationData, EventData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData

from meow.services.local.event.final_proceedings.abstract_plugin.abstract_final_proceedings_plugin import AbstractFinalProceedingsPlugin
from meow.utils.filesystem import rmtree


logger = lg.getLogger(__name__)


class FileSystemCache(BytecodeCache):

    def __init__(self, directory):
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

    def __init__(self, id: str) -> None:
        self.env = Environment(
            enable_async=True,
            auto_reload=False,
            cache_size=1024,
            autoescape=select_autoescape(),
            bytecode_cache=FileSystemCache(f"var/cache/{id}"),
            loader=FileSystemLoader("jinja/final_proceedings"),
        )

    async def render(self, name: str, args: dict) -> str:
        return await self.env.get_template(name).render_async(args)

    async def render_config_toml(self, event: EventData) -> str:
        return await self.render("config.toml.jinja", dict(
            title=event.title,
            url=f'http://127.0.0.1:8000/{event.title}'
        ))

    async def render_home_page(self) -> str:
        return await self.render("home_page.html.jinja", dict())

    async def render_session_list(self, sessions: list[SessionData]) -> str:
        return await self.render("session_list.html.jinja", dict(
            sessions=[s.as_dict() for s in sessions]
        ))

    async def render_session_page(self, event: EventData, session: SessionData, contributions: list[ContributionData]) -> str:
        return await self.render("session_page.html.jinja", dict(
            event=event.as_dict(),
            session=session.as_dict(),
            contributions=[c.as_dict() for c in contributions],
            contributions_len=len(contributions)
        ))

    async def render_classification_list(self, classifications: list[TrackData]) -> str:
        return await self.render("classification_list.html.jinja", dict(
            classifications=[s.as_dict() for s in classifications]
        ))

    async def render_classification_page(self, event: EventData, classification: TrackData, contributions: list[ContributionData]) -> str:
        return await self.render("classification_page.html.jinja", dict(
            event=event.as_dict(),
            classification=classification.as_dict(),
            contributions=[c.as_dict() for c in contributions],
            contributions_len=len(contributions)
        ))

    async def render_author_list(self, authors: list[PersonData]) -> str:
        return await self.render("author_list.html.jinja", dict(
            authors=[s.as_dict() for s in authors]
        ))

    async def render_author_page(self, event: EventData, author: PersonData, contributions: list[ContributionData]) -> str:
        return await self.render("author_page.html.jinja", dict(
            event=event.as_dict(),
            author=author.as_dict(),
            contributions=[c.as_dict() for c in contributions],
            contributions_len=len(contributions)
        ))

    async def render_institute_list(self, institutes: list[AffiliationData]) -> str:
        return await self.render("institute_list.html.jinja", dict(
            institutes=[s.as_dict() for s in institutes]
        ))

    async def render_institute_page(self, event: EventData, institute: AffiliationData, authors: list[PersonData]) -> str:
        return await self.render("institute_page.html.jinja", dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            authors=[c.as_dict() for c in authors],
        ))

    async def render_institute_author_page(self, event: EventData, institute: AffiliationData, author: PersonData, contributions: list[ContributionData]) -> str:
        return await self.render("institute_author_page.html.jinja", dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            author=author.as_dict(),
            contributions=[c.as_dict() for c in contributions],
        ))

    async def render_keyword_list(self, keywords: list[KeywordData]) -> str:
        return await self.render("keyword_list.html.jinja", dict(
            keywords=[s.as_dict() for s in keywords]
        ))

    async def render_keyword_page(self, event: EventData, keyword: KeywordData, contributions: list[ContributionData]) -> str:
        return await self.render("keyword_page.html.jinja", dict(
            event=event.as_dict(),
            keyword=keyword.as_dict(),
            contributions=[c.as_dict() for c in contributions],
            contributions_len=len(contributions)
        ))

    async def render_doi_per_institute_list(self, institutes: list[AffiliationData]) -> str:
        return await self.render("doi_per_institute_list.html.jinja", dict(
            institutes=[s.as_dict() for s in institutes]
        ))

    async def render_doi_per_institute_page(self, event: EventData, institute: AffiliationData, contributions: list[ContributionData]) -> str:
        return await self.render("doi_per_institute_page.html.jinja", dict(
            event=event.as_dict(),
            institute=institute.as_dict(),
            contributions=[c.as_dict() for c in contributions],
            contributions_len=len(contributions)
        ))


class HugoFinalProceedingsPlugin(AbstractFinalProceedingsPlugin):
    """ HugoFinalProceedingsPlugin """

    def __init__(self, proceedings_data: ProceedingsData) -> None:
        """ """

        self.event = proceedings_data.event
        self.contributions = proceedings_data.contributions

        self.sessions = proceedings_data.sessions
        self.classifications = proceedings_data.classification
        self.authors = proceedings_data.author
        self.institutes = proceedings_data.institute
        self.keywords = proceedings_data.keyword

        self.init_paths()

    def init_paths(self) -> None:

        event_id: str = self.event.id

        self.tmp_dir = Path('var', 'tmp')

        self.cache_dir = Path('var', 'cache', event_id)

        self.src_dir = Path('var', 'run', f"{event_id}_hugo_src")
        self.out_dir = Path('var', 'run', f"{event_id}_hugo_src", "out")

        self.src_session_dir = \
            Path(self.src_dir, 'content', 'session')
        self.src_classification_dir = \
            Path(self.src_dir, 'content', 'classification')
        self.src_author_dir = \
            Path(self.src_dir, 'content', 'author')
        self.src_institute_dir = \
            Path(self.src_dir, 'content', 'institute')
        self.src_doi_per_institute_dir = \
            Path(self.src_dir, 'content', 'doi_per_institute')
        self.src_keyword_dir = \
            Path(self.src_dir, 'content', 'keyword')

    async def run(self) -> BytesIO:
        """ """

        await self.prepare()
        await self.run_build()
        await self.generate()

        zip = await self.compress()

        await self.clean()

        return zip

    async def run_prepare(self) -> None:
        await self.prepare()

    async def run_build(self) -> None:

        # await self.home()
        # await self.session()
        # await self.classification()
        # await self.author()
        # await self.institute()
        # await self.doi_per_institute()
        # await self.keyword()
        # await self.static()
        # await self.finalize()

        async with create_task_group() as tg:
            tg.start_soon(self.home)
            tg.start_soon(self.session)
            tg.start_soon(self.classification)
            tg.start_soon(self.author)
            tg.start_soon(self.institute)
            tg.start_soon(self.doi_per_institute)
            tg.start_soon(self.keyword)
            tg.start_soon(self.static)
            tg.start_soon(self.finalize)

    async def run_pack(self) -> BytesIO:
        await self.generate()
        zip = await self.compress()

        await self.clean()

        return zip

    async def prepare(self) -> None:
        """ """

        try:
            await rmtree(f"{await self.src_dir.absolute()}")
            await self.tmp_dir.mkdir(exist_ok=True, parents=True)
            await self.src_dir.mkdir(exist_ok=True, parents=True)

        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

        # try:
        #
        #     ssg_cmd = await self.ssg_cmd()
        #
        #     ssg_args = [f"{ssg_cmd}", "new", "site",
        #                 f"{self.src_dir}", "--force"]
        #
        #     result = await run_process(ssg_args)
        #
        #     if result.returncode == 0:
        #         logger.info(result.stdout.decode())
        #     else:
        #         logger.info(result.stderr.decode())
        #
        # except BaseException as e:
        #     logger.error("hugo:prepare", e, exc_info=True)

        try:

            # theme_dir = await Path(self.src_dir, 'themes/PaperMod').absolute()
            #
            # git_args = ["git", "clone", "https://github.com/adityatelange/hugo-PaperMod",
            #             f"{theme_dir}", "--depth=1"]
            #
            # theme_dir = await Path(self.src_dir, 'themes/hugo-book').absolute()
            #
            # git_args = ["git", "clone", "https://github.com/alex-shpak/hugo-book",
            #             f"{theme_dir}", "--depth=1"]
            #
            # theme_dir = await Path(self.src_dir, 'themes/hugo-xmin').absolute()
            #
            # git_args = ["git", "clone", "https://github.com/yihui/hugo-xmin.git",
            #             f"{theme_dir}", "--depth=1"]
            #
            # result = await run_process(git_args)
            #
            # if result.returncode == 0:
            #     logger.info(result.stdout.decode())
            # else:
            #     logger.info(result.stderr.decode())

            zip_cmd = await self.zip_cmd()

            site_assets_dir = await Path('assets', 'hugo-site.7z').absolute()
            site_output_dir = await self.tmp_dir.absolute()

            site_extract_args = [f"{zip_cmd}", "x", f"{site_assets_dir}",
                                 "-aoa", f"-o{site_output_dir}"]

            logger.debug(site_extract_args)

            result = await run_process(site_extract_args)

            if result.returncode == 0:
                logger.info(result.stdout.decode())
            else:
                logger.info(result.stderr.decode())

            await Path(self.tmp_dir, '0_hugo_src').rename(self.src_dir)

            await rmtree(f"{await Path(self.tmp_dir, '0_hugo_src').absolute()}")

        except BaseException as e:
            logger.error(e)

        try:

            zip_cmd = await self.zip_cmd()

            theme_assets_dir = await Path('assets', 'hugo-theme.7z').absolute()
            theme_output_dir = await Path(self.src_dir, 'themes').absolute()

            theme_extract_args = [f"{zip_cmd}", "x", f"{theme_assets_dir}",
                                  "-aoa", f"-o{theme_output_dir}"]

            logger.debug(theme_extract_args)

            result = await run_process(theme_extract_args)

            if result.returncode == 0:
                logger.info(result.stdout.decode())
            else:
                logger.info(result.stderr.decode())

        except BaseException as e:
            logger.error(e)

        try:

            await self.src_session_dir.mkdir(exist_ok=True, parents=True)
            await self.src_classification_dir.mkdir(exist_ok=True, parents=True)
            await self.src_author_dir.mkdir(exist_ok=True, parents=True)
            await self.src_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_doi_per_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_keyword_dir.mkdir(exist_ok=True, parents=True)

            await self.out_dir.mkdir(exist_ok=True, parents=True)
            await self.cache_dir.mkdir(exist_ok=True, parents=True)

        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

        try:
            self.template = JinjaTemplateRenderer(self.event.id)
            await Path(self.src_dir, 'config.toml').write_text(
                await self.template.render_config_toml(self.event)
            )
        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

    async def home(self) -> None:
        await Path(self.src_dir, 'content', '_index.html').write_text(
            await self.template.render_home_page()
        )

    async def session(self) -> None:
        """ """

        logger.info(f'render_session - {len(self.sessions)}')

        await Path(self.src_session_dir, '_index.html').write_text(
            await self.template.render_session_list(self.sessions)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, session: SessionData) -> None:
            async with capacity_limiter:
                curr_dir = Path(self.src_session_dir, session.code.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if c.session_code == session.code
                ]

                # logger.info(f"{session} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_session_page(self.event, session, contributions)
                )

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for session in self.sessions:
                if session and session.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, session)

    async def classification(self) -> None:
        """ """

        logger.info(f'render_classification - {len(self.classifications)}')

        await Path(self.src_classification_dir, '_index.html').write_text(
            await self.template.render_classification_list(self.classifications)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, classification: TrackData) -> None:
            async with capacity_limiter:
                curr_dir = Path(self.src_classification_dir,
                                classification.code.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if c.track and c.track.code == classification.code
                ]

                # logger.info(f"{classification} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_classification_page(
                        self.event, classification, contributions)
                )

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for classification in self.classifications:
                if classification and classification.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, classification)

    async def author(self) -> None:
        """ """

        logger.info(f'render_author - {len(self.authors)}')

        await Path(self.src_author_dir, '_index.html').write_text(
            await self.template.render_author_list(self.authors)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, author: PersonData) -> None:
            async with capacity_limiter:
                curr_dir = Path(self.src_author_dir, author.id.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if len(c.authors) > 0 and author in c.authors
                ]

                # logger.info(f"{author} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_author_page(
                        self.event, author, contributions)
                )

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for author in self.authors:
                if author and author.id:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, author)

    async def institute(self) -> None:
        """ """

        logger.info(f'render_institute - {len(self.institutes)}')

        await Path(self.src_institute_dir, '_index.html').write_text(
            await self.template.render_institute_list(self.institutes)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, institute: AffiliationData, author: PersonData) -> None:
            async with capacity_limiter:

                curr_dir = Path(self.src_institute_dir, institute.id.lower(), author.id.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if len(c.authors) > 0 and author in c.authors
                ]

                # logger.info(f"{institute} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_institute_author_page(
                        self.event, institute, author, contributions)
                )

        async def _render_institute(capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
            async with capacity_limiter:

                curr_dir = Path(self.src_institute_dir, institute.id.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                authors = [
                    c for c in self.authors
                    if c.affiliation == institute.name
                ]

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_institute_page(
                        self.event, institute, authors)
                )

                capacity_limiter = CapacityLimiter(6)
                async with create_task_group() as tg:
                    for author in authors:
                        if author and author.id:
                            tg.start_soon(_render_contribution,
                                          capacity_limiter, institute, author)

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for institute in self.institutes:
                if institute and institute.id:
                    tg.start_soon(_render_institute,
                                  capacity_limiter, institute)

    async def doi_per_institute(self) -> None:
        """ """

        logger.info(f'render_doi_per_institute - {len(self.institutes)}')

        await Path(self.src_doi_per_institute_dir, '_index.html').write_text(
            await self.template.render_doi_per_institute_list(self.institutes)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
            async with capacity_limiter:

                curr_dir = Path(self.src_doi_per_institute_dir,
                                institute.id.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if len(c.institutes) > 0 and institute in c.institutes
                ]

                # logger.info(f"{institute} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_doi_per_institute_page(
                        self.event, institute, contributions)
                )

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for institute in self.institutes:
                if institute and institute.id:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, institute)

    async def keyword(self) -> None:
        """ """

        logger.info(f'render_keyword - {len(self.keywords)}')

        await Path(self.src_keyword_dir, '_index.html').write_text(
            await self.template.render_keyword_list(self.keywords)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, keyword: KeywordData) -> None:
            async with capacity_limiter:
                curr_dir = Path(self.src_keyword_dir, keyword.code.lower())
                await curr_dir.mkdir(parents=True, exist_ok=True)

                contributions = [
                    c for c in self.contributions
                    if len(c.keywords) > 0 and keyword in c.keywords
                ]

                # logger.info(f"{keyword} -> {len(contributions)}")

                await Path(curr_dir, '_index.html').write_text(
                    await self.template.render_keyword_page(
                        self.event, keyword, contributions)
                )

        capacity_limiter = CapacityLimiter(6)
        async with create_task_group() as tg:
            for keyword in self.keywords:
                tg.start_soon(_render_contribution, capacity_limiter, keyword)

    async def static(self) -> None:
        pass

    async def finalize(self) -> None:
        pass

    async def ssg_cmd(self):
        return await Path('bin', 'hugo').absolute()

    async def generate(self) -> None:
        """ """

        try:

            ssg_cmd = await self.ssg_cmd()

            ssg_args = [f"{ssg_cmd}", "--source", f"{self.src_dir}",
                        "--destination", "out"]

            result = await run_process(ssg_args)

            if result.returncode == 0:
                logger.info(result.stdout.decode())
            else:
                logger.info(result.stderr.decode())

        except BaseException as e:
            logger.error("hugo:generate", e, exc_info=True)

    async def compress(self) -> BytesIO:
        """ """

        zip_cmd = await self.zip_cmd()
        out_dir_path = await self.out_dir.absolute()

        zip_file = Path(self.src_dir, "out.7z")
        zip_file_path = await zip_file.absolute()

        # 7z a /tmp/12/12.7z /tmp/12/out -m0=LZMA2:d=64k -mmt=4

        zip_args = [f"{zip_cmd}", "a", f"{zip_file_path}",
                    f"{out_dir_path}", "-m0=LZMA2:d=64k", "-mmt=4"]

        result = await run_process(zip_args)

        if result.returncode == 0:
            logger.info(result.stdout.decode())
        else:
            logger.info(result.stderr.decode())

        # logger.debug(result.stdout.decode())

        zip = await self.get_zip(zip_file_path)

        # await zip_file.unlink(True)

        return zip

    async def clean(self) -> None:
        """ """

        # TODO: to implement

        await self.src_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"temporary directory {await self.src_dir.absolute()}")
