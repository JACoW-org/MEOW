import logging as lg

import io

from anyio import Path

from typing import AsyncGenerator

import shutil

from anyio import sleep, create_task_group, run

from jinja2 import Environment, select_autoescape, FileSystemLoader, Template

from jpsp.services.local.event.final_proceedings.abstract_plugin.abstract_final_proceedings_plugin import AbstractFinalProceedingsPlugin


from anyio import open_file
from anyio import Path
from anyio import run_process
from anyio.streams.file import FileReadStream

from jpsp.utils.datetime import format_datetime_full, format_datetime_time


logger = lg.getLogger(__name__)


class JinjaTemplateRenderer:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            autoescape=select_autoescape(),
            loader=FileSystemLoader(
                "jpsp/services/local/event/final_proceedings/hugo_plugin/jinja"),
        )

    async def render(self, name: str, args: dict) -> str:
        return await self.env.get_template(name).render_async(args)

    async def render_config_toml(self, event: dict) -> str:
        return await self.render("config.toml.jinja", dict(
            title=event.get('title', None),
            url='http://127.0.0.1:8000/'
        ))

    async def render_home_page(self) -> str:
        return await self.render("home_page.html.jinja", dict())

    async def render_session_list(self, sessions: list[dict]) -> str:
        return await self.render("session_list.html.jinja", dict(
            sessions=sessions
        ))

    async def render_contribution_list(self, session: dict) -> str:
        return await self.render("contribution_list.html.jinja", dict(
            session_code=session.get('code', None),
            session_title=session.get('title', ''),
            session_start=format_datetime_full(session.get('start', None)),
            session_end=format_datetime_time(session.get('end', None)),
            session_conveners=session.get('conveners', []),
            contributions=session.get('contributions', [])
        ))


class HugoFinalProceedingsPlugin(AbstractFinalProceedingsPlugin):
    """ HugoFinalProceedingsPlugin """

    def __init__(self, final_proceedings: dict) -> None:
        """ """

        self.template = JinjaTemplateRenderer()

        self.event: dict = final_proceedings.get('event', None)
        self.sessions: list = final_proceedings.get('sessions', [])

        self.src_dir = Path('var', 'run', f"{self.event.get('id')}_hugo_src")
        self.out_dir = Path(
            'var', 'run', f"{self.event.get('id')}_hugo_src", "out")

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
            await self.src_dir.mkdir(exist_ok=True, parents=True)

        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

        try:

            ssg_cmd = await self.ssg_cmd()

            ssg_args = [f"{ssg_cmd}", "new", "site",
                        f"{self.src_dir}", "--force"]

            result = await run_process(ssg_args)

            if result.returncode == 0:
                logger.info(result.stdout.decode())
            else:
                logger.info(result.stderr.decode())

        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

        try:

            theme_dir = await Path(self.src_dir, 'themes/PaperMod').absolute()

            git_args = ["git", "clone", "https://github.com/adityatelange/hugo-PaperMod",
                        f"{theme_dir}", "--depth=1"]

            theme_dir = await Path(self.src_dir, 'themes/hugo-book').absolute()

            git_args = ["git", "clone", "https://github.com/alex-shpak/hugo-book",
                        f"{theme_dir}", "--depth=1"]
            
            theme_dir = await Path(self.src_dir, 'themes/hugo-xmin').absolute()

            git_args = ["git", "clone", "https://github.com/yihui/hugo-xmin.git",
                        f"{theme_dir}", "--depth=1"]

            result = await run_process(git_args)

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
        await Path(self.src_session_dir, '_index.md').write_text(
            await self.template.render_session_list(self.sessions)
        )

        async with create_task_group() as tg:
            for session in self.sessions:
                tg.start_soon(self.contribution, session)

    async def contribution(self, session: dict):

        curr_dir = Path(self.src_session_dir, session.get('code', None))

        await curr_dir.mkdir(parents=True, exist_ok=True)

        await Path(curr_dir, '_index.md').write_text(
            await self.template.render_contribution_list(session)
        )

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
