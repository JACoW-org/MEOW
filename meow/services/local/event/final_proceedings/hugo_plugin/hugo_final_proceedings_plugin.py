import logging as lg

import io
import json

from anyio import Path

import shutil

from anyio import create_task_group

from jinja2 import Environment, select_autoescape, FileSystemLoader, filters
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import EventData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData

from meow.services.local.event.final_proceedings.abstract_plugin.abstract_final_proceedings_plugin import AbstractFinalProceedingsPlugin

from anyio import Path, run_process

from meow.utils.datetime import format_datetime_full, format_datetime_time


logger = lg.getLogger(__name__)


class JinjaTemplateRenderer:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            autoescape=select_autoescape(),
            loader=FileSystemLoader("jinja/final_proceedings"),
        )

    async def render(self, name: str, args: dict) -> str:
        return await self.env.get_template(name).render_async(args)

    async def render_config_toml(self, event: EventData) -> str:
        return await self.render("config.toml.jinja", dict(
            title=event.title,
            url='http://127.0.0.1:8000/'
        ))

    async def render_home_page(self) -> str:
        return await self.render("home_page.html.jinja", dict())

    async def render_session_list(self, sessions: list[dict]) -> str:
        return await self.render("session_list.html.jinja", dict(
            sessions=sessions
        ))

    async def render_contribution_list(self, event: EventData, session: SessionData, contributions: list[ContributionData]) -> str:
        return await self.render("contribution_list.html.jinja", dict(
            event_code=event.title,
            session_code=session.code,
            session_title=session.title,
            session_start=format_datetime_full(session.start),
            session_end=format_datetime_time(session.end),
            session_conveners=[c.as_dict() for c in session.conveners],
            contributions=[c.as_dict() for c in contributions]
        ))


class HugoFinalProceedingsPlugin(AbstractFinalProceedingsPlugin):
    """ HugoFinalProceedingsPlugin """

    def __init__(self, proceedings_data: ProceedingsData) -> None:
        """ """

        self.template = JinjaTemplateRenderer()

        self.event = proceedings_data.event
        self.sessions = proceedings_data.sessions
        self.contributions = proceedings_data.contributions

        self.init_paths()

    def init_paths(self) -> None:

        event_id: str = self.event.id

        self.tmp_dir = Path('var', 'tmp')

        self.src_dir = Path('var', 'run', f"{event_id}_hugo_src")
        self.out_dir = Path('var', 'run', f"{event_id}_hugo_src", "out")

        self.src_session_dir = Path(self.src_dir, 'content', 'session')
        self.src_classification_dir = Path(
            self.src_dir, 'content', 'classification')
        self.src_author_dir = Path(self.src_dir, 'content', 'author')
        self.src_institute_dir = Path(self.src_dir, 'content', 'institute')
        self.src_doi_per_institute_dir = Path(
            self.src_dir, 'content', 'doi_per_institute')
        self.src_keyword_dir = Path(self.src_dir, 'content', 'keyword')

    async def run(self):
        """ """

        await self.prepare()

        async with create_task_group() as tg:
            tg.start_soon(self.home)
            tg.start_soon(self.session)
            tg.start_soon(self.classification)
            tg.start_soon(self.author)
            tg.start_soon(self.institute)
            tg.start_soon(self.doi_per_institute)
            tg.start_soon(self.keyword)
            tg.start_soon(self.finalize)

        await self.generate()
        zip = await self.compress()

        await self.clean()

        return zip

    async def prepare(self) -> None:
        """ """

        try:

            shutil.rmtree(f"{await self.src_dir.absolute()}", ignore_errors=True)

            # await self.src_dir.rmdir()
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

            shutil.rmtree(f"{await Path(self.tmp_dir, '0_hugo_src').absolute()}", ignore_errors=True)

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

        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

        try:
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
        await Path(self.src_session_dir, '_index.html').write_text(
            await self.template.render_session_list([
                s.as_dict() for s in self.sessions
            ])
        )

        async def _session_contribution(session: SessionData) -> None:
            curr_dir = Path(self.src_session_dir, session.code.lower())
            await curr_dir.mkdir(parents=True, exist_ok=True)

            await Path(curr_dir, '_index.html').write_text(
                await self.template.render_contribution_list(self.event, session, [
                    c for c in self.contributions
                    if c.session_code == session.code
                ])
            )

        async with create_task_group() as tg:
            for session in self.sessions:
                tg.start_soon(_session_contribution, session)

    async def classification(self) -> None:
        pass

    async def author(self) -> None:
        pass

    async def institute(self) -> None:
        pass

    async def doi_per_institute(self) -> None:
        pass

    async def keyword(self) -> None:
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

    async def compress(self) -> io.BytesIO:
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

        await zip_file.unlink(True)

        return zip

    async def clean(self) -> None:
        """ """

        # TODO: to implement

        await self.src_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"temporary directory {await self.src_dir.absolute()}")
