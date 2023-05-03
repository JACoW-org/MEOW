import logging as lg

from io import BytesIO
from anyio import Path, run_process, create_task_group
from numpy import short


from meow.models.local.event.final_proceedings.track_model import TrackData

from anyio import create_task_group, CapacityLimiter

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_jinja_template_renderer import JinjaTemplateRenderer
from meow.tasks.local.doi.models import ContributionDOI

from meow.services.local.event.final_proceedings.abstract_plugin.abstract_final_proceedings_plugin import AbstractFinalProceedingsPlugin
from meow.utils.filesystem import cptree, rmtree


logger = lg.getLogger(__name__)


class HugoFinalProceedingsPlugin(AbstractFinalProceedingsPlugin):
    """ HugoFinalProceedingsPlugin """

    def __init__(self, proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> None:
        """ """

        self.settings = settings
        self.proceedings = proceedings_data
        self.event = proceedings_data.event
        self.attachments = proceedings_data.attachments
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

        self.src_dir = Path('var', 'run', f"{event_id}_hugo_src")
        self.out_dir = Path('var', 'run', f"{event_id}_hugo_src", "out")

        self.src_layouts_dir = \
            Path(self.src_dir, 'layouts')
        self.src_layouts_partials_dir = \
            Path(self.src_dir, 'layouts', 'partials')
        self.src_layouts_partials_session_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'session')
        self.src_layouts_partials_classification_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'classification')
        self.src_layouts_partials_author_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'author')
        self.src_layouts_partials_institute_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'institute')
        self.src_layouts_partials_doi_per_institute_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'doi_per_institute')

        self.src_layouts_partials_keyword_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'keyword')

        self.src_layouts_partials_contributions_dir = \
            Path(self.src_dir, 'layouts', 'partials', 'contributions')
        self.src_contributions_dir = \
            Path(self.src_dir, 'content', 'contributions')
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
        self.src_doi_dir = \
            Path(self.src_dir, 'content', 'doi')
        self.src_ref_dir = \
            Path(self.src_dir, 'content', 'reference')

    async def run(self) -> None:
        """ """

        await self.prepare()
        await self.run_build()
        await self.generate()
        await self.compress()
        await self.clean()

    async def run_prepare(self) -> None:
        await self.prepare()

    async def run_build(self) -> None:

        logger.info('event_final_proceedings - plugin.build')

        await self.render_home()
        await self.render_contributions()
        await self.render_session()
        await self.render_classification()
        await self.render_author()
        await self.render_institute()
        await self.render_doi_per_institute()
        await self.render_keyword()
        await self.render_doi_contributions()
        await self.render_references()
        await self.static()
        await self.finalize()

        # async with create_task_group() as tg:
        #     tg.start_soon(self.home)
        #     tg.start_soon(self.session)
        #     tg.start_soon(self.classification)
        #     tg.start_soon(self.author)
        #     tg.start_soon(self.institute)
        #     tg.start_soon(self.doi_per_institute)
        #     tg.start_soon(self.keyword)
        #     tg.start_soon(self.doi)
        #     tg.start_soon(self.reference)
        #     tg.start_soon(self.static)
        #     tg.start_soon(self.finalize)

    async def prepare(self) -> None:
        """ """

        try:
            await rmtree(f"{await self.src_dir.absolute()}")
            await self.tmp_dir.mkdir(exist_ok=True, parents=True)
            await self.src_dir.mkdir(exist_ok=True, parents=True)

            site_assets_dir = Path('assets', '0_hugo_src')

            logger.info(f"cptree -> {site_assets_dir} - {self.src_dir}")

            await rmtree(f"{self.src_dir}")
            await cptree(f"{site_assets_dir}", f"{self.src_dir}")

            await self.src_layouts_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_session_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_classification_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_author_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_doi_per_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_keyword_dir.mkdir(exist_ok=True, parents=True)
            await self.src_layouts_partials_contributions_dir.mkdir(exist_ok=True, parents=True)

            await self.src_contributions_dir.mkdir(exist_ok=True, parents=True)
            await self.src_session_dir.mkdir(exist_ok=True, parents=True)
            await self.src_classification_dir.mkdir(exist_ok=True, parents=True)
            await self.src_author_dir.mkdir(exist_ok=True, parents=True)
            await self.src_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_doi_per_institute_dir.mkdir(exist_ok=True, parents=True)
            await self.src_keyword_dir.mkdir(exist_ok=True, parents=True)
            await self.src_doi_dir.mkdir(exist_ok=True, parents=True)
            await self.src_ref_dir.mkdir(exist_ok=True, parents=True)

            await self.out_dir.mkdir(exist_ok=True, parents=True)

            self.template = JinjaTemplateRenderer()

            await Path(self.src_dir, 'config.toml').write_text(
                await self.template.render_config_toml(self.event, self.attachments, self.settings)
            )
        except BaseException as e:
            logger.error("hugo:prepare", e, exc_info=True)

    async def render_home(self) -> None:
        await Path(self.src_dir, 'layouts', 'index.html').write_text(
            await self.template.render_home_page(self.event,
                                                 self.attachments,
                                                 self.proceedings.proceedings_volume_size,
                                                 self.proceedings.proceedings_brief_size)
        )

    async def render_contributions(self) -> None:

        async def _render_contribution(capacity_limiter: CapacityLimiter, contribution: ContributionData) -> None:
            async with capacity_limiter:

                # logger.info(f"{session} -> {len(contributions)}")

                code = contribution.code.lower()

                base_path = Path(self.src_dir, 'layouts',
                                 'partials', 'contributions')

                if contribution.code:
                    await Path(base_path, f"{code}.html").write_text(
                        await self.template.render_contribution_partial(contribution)
                    )

                if contribution.code and contribution.is_qa_approved and contribution.doi_data:
                    await Path(base_path, f"{code}_doi.html").write_text(
                        await self.template.render_doi_partial(self.event, contribution.doi_data)
                    )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for contribution in self.contributions:
                if contribution and contribution.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, contribution)

    async def render_session(self) -> None:
        """ """

        logger.info(f'render_session - {len(self.sessions)}')

        session_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'session', 'list.html')

        await session_partial_dir.write_text(
            await self.template.render_session_partial(self.sessions)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, session: SessionData) -> None:
            async with capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if c.session_code == session.code
                ]

                # logger.info(f"{session} -> {len(contributions)}")

                await Path(self.src_session_dir, f'{session.code.lower()}.md').write_text(
                    await self.template.render_session_page(self.event, session, contributions)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for session in self.sessions:
                if session and session.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, session)

    async def render_classification(self) -> None:
        """ """

        logger.info(f'render_classification - {len(self.classifications)}')

        classification_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'classification', 'list.html')

        await classification_partial_dir.write_text(
            await self.template.render_classification_partial(self.classifications)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, classification: TrackData) -> None:
            async with capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if c.track and c.track.code == classification.code
                ]

                # logger.info(f"{session} -> {len(contributions)}")

                await Path(self.src_classification_dir, f'{classification.code.lower()}.md').write_text(
                    await self.template.render_classification_page(self.event, classification, contributions)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for classification in self.classifications:
                if classification and classification.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, classification)

        # await Path(self.src_classification_dir, '_index.html').write_text(
        #     await self.template.render_classification_list(self.classifications)
        # )
#
        # async def _render_contribution(capacity_limiter: CapacityLimiter, classification: TrackData) -> None:
        #     async with capacity_limiter:
        #         curr_dir = Path(self.src_classification_dir,
        #                         classification.code.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         contributions = [
        #             c for c in self.contributions
        #             if c.track and c.track.code == classification.code
        #         ]
#
        #         # logger.info(f"{classification} -> {len(contributions)}")
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_classification_page(
        #                 self.event, classification, contributions)
        #         )
#
        # capacity_limiter = CapacityLimiter(4)
        # async with create_task_group() as tg:
        #     for classification in self.classifications:
        #         if classification and classification.code:
        #             tg.start_soon(_render_contribution,
        #                           capacity_limiter, classification)

    async def render_author(self) -> None:
        """ """

        logger.info(f'render_author - {len(self.authors)}')

        author_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'author', 'list.html')

        await author_partial_dir.write_text(
            await self.template.render_author_partial(self.authors)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, author: PersonData) -> None:
            async with capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if len(c.authors) > 0 and author in c.authors
                ]

                # logger.info(f"{author} -> {len(contributions)}")

                await Path(self.src_author_dir, f'{author.id.lower()}.md').write_text(
                    await self.template.render_author_page(self.event, author, contributions)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for author in self.authors:
                if author and author.id:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, author)

        # await Path(self.src_author_dir, '_index.html').write_text(
        #     await self.template.render_author_list(self.authors)
        # )
#
        # async def _render_contribution(capacity_limiter: CapacityLimiter, author: PersonData) -> None:
        #     async with capacity_limiter:
        #         curr_dir = Path(self.src_author_dir, author.id.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         contributions = [
        #             c for c in self.contributions
        #             if len(c.authors) > 0 and author in c.authors
        #         ]
#
        #         # logger.info(f"{author} -> {len(contributions)}")
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_author_page(
        #                 self.event, author, contributions)
        #         )
#
        # capacity_limiter = CapacityLimiter(4)
        # async with create_task_group() as tg:
        #     for author in self.authors:
        #         if author and author.id:
        #             tg.start_soon(_render_contribution,
        #                           capacity_limiter, author)

    async def render_institute(self) -> None:
        """ """

        logger.info(f'render_institute - {len(self.institutes)}')

        institute_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'institute', 'list.html')

        authorsGroups: dict[str, list[dict]] = {}

        for author in self.authors:
            if not author.affiliation in authorsGroups:
                authorsGroups[author.affiliation] = []
            authorsGroups[author.affiliation].append(dict(
                code=author.code,
                short=author.short
            ))

        await institute_partial_dir.write_text(
            await self.template.render_institute_partial(self.institutes, authorsGroups)
        )

        async def _render_contribution(contribution_capacity_limiter: CapacityLimiter, institute: AffiliationData, author: PersonData) -> None:
            async with contribution_capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if len(c.authors) > 0 and author in c.authors
                ]

                # logger.info(f"{institute} -> {len(contributions)}")

                await Path(self.src_institute_dir, f'{author.code.lower()}.md').write_text(
                    await self.template.render_institute_page(self.event, institute, author, contributions)
                )

        async def _render_institute(institute_capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
            async with institute_capacity_limiter:

                authors = [
                    c for c in self.authors
                    if c.affiliation == institute.name
                ]

                # logger.info(f"{institute} -> {len(authors)}")

                contribution_capacity_limiter = CapacityLimiter(4)
                async with create_task_group() as tg:
                    for author in authors:
                        if author and author.id:
                            tg.start_soon(_render_contribution,
                                          contribution_capacity_limiter,
                                          institute, author)

        institute_capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for institute in self.institutes:
                if institute and institute.id:
                    tg.start_soon(_render_institute,
                                  institute_capacity_limiter,
                                  institute)

        # await Path(self.src_institute_dir, '_index.html').write_text(
        #     await self.template.render_institute_list(self.institutes)
        # )
#
        # async def _render_contribution(capacity_limiter: CapacityLimiter, institute: AffiliationData, author: PersonData) -> None:
        #     async with capacity_limiter:
#
        #         curr_dir = Path(self.src_institute_dir,
        #                         institute.id.lower(), author.id.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         contributions = [
        #             c for c in self.contributions
        #             if len(c.authors) > 0 and author in c.authors
        #         ]
#
        #         # logger.info(f"{institute} -> {len(contributions)}")
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_institute_author_page(
        #                 self.event, institute, author, contributions)
        #         )
#
        # async def _render_institute(capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
        #     async with capacity_limiter:
#
        #         curr_dir = Path(self.src_institute_dir, institute.id.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         authors = [
        #             c for c in self.authors
        #             if c.affiliation == institute.name
        #         ]
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_institute_page(
        #                 self.event, institute, authors)
        #         )
#
        #         capacity_limiter = CapacityLimiter(4)
        #         async with create_task_group() as tg:
        #             for author in authors:
        #                 if author and author.id:
        #                     tg.start_soon(_render_contribution,
        #                                   capacity_limiter, institute, author)
#
        # capacity_limiter = CapacityLimiter(4)
        # async with create_task_group() as tg:
        #     for institute in self.institutes:
        #         if institute and institute.id:
        #             tg.start_soon(_render_institute,
        #                           capacity_limiter, institute)

    async def render_doi_per_institute(self) -> None:
        """ """

        logger.info(f'render_doi_per_institute - {len(self.institutes)}')

        doi_per_institute_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'doi_per_institute', 'list.html')

        contributionsGroups: dict[str, list[dict]] = {}

        for institute in self.institutes:
            contributionsGroups[institute.name] = [
                dict(code=c.code, title=c.title,
                     is_qa_approved=c.is_qa_approved,
                     doi_data=c.doi_data)
                for c in self.contributions
                if c.is_qa_approved and c.doi_data
                and institute in c.institutes
            ]

        institutes: list = [
            i for i in self.institutes
            if len(contributionsGroups[i.name]) > 0
        ]

        # logger.info(f'render_doi_per_institute - {contributionsGroups}')

        await doi_per_institute_partial_dir.write_text(
            await self.template.render_doi_per_institute_partial(institutes, contributionsGroups)
        )

        async def _render_contribution(contribution_capacity_limiter: CapacityLimiter, contribution: ContributionData):
            async with contribution_capacity_limiter:
                await Path(self.src_doi_per_institute_dir, f'{contribution.code.lower()}.md').write_text(
                    await self.template.render_doi_per_institute_page(self.event, institute, contribution)
                )

        async def _render_doi_per_institute(doi_per_institute_capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
            async with doi_per_institute_capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if len(c.institutes) > 0 and institute in c.institutes
                ]

                # logger.info(f"{institute} -> {len(contributions)}")

                contribution_capacity_limiter = CapacityLimiter(4)
                async with create_task_group() as tg:
                    for contribution in contributions:
                        tg.start_soon(_render_contribution,
                                      contribution_capacity_limiter,
                                      contribution)

        doi_per_institute_capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for institute in self.institutes:
                if institute and institute.id:
                    tg.start_soon(_render_doi_per_institute,
                                  doi_per_institute_capacity_limiter,
                                  institute)

        # logger.info(f'render_doi_per_institute - {len(self.institutes)}')
#
        # await Path(self.src_doi_per_institute_dir, '_index.html').write_text(
        #     await self.template.render_doi_per_institute_list(self.institutes)
        # )
#
        # async def _render_contribution(capacity_limiter: CapacityLimiter, institute: AffiliationData) -> None:
        #     async with capacity_limiter:
#
        #         curr_dir = Path(self.src_doi_per_institute_dir,
        #                         institute.id.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         contributions = [
        #             c for c in self.contributions
        #             if len(c.institutes) > 0 and institute in c.institutes
        #         ]
#
        #         # logger.info(f"{institute} -> {len(contributions)}")
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_doi_per_institute_page(
        #                 self.event, institute, contributions)
        #         )
#
        # capacity_limiter = CapacityLimiter(4)
        # async with create_task_group() as tg:
        #     for institute in self.institutes:
        #         if institute and institute.id:
        #             tg.start_soon(_render_contribution,
        #                           capacity_limiter, institute)

    async def render_keyword(self) -> None:
        """ """

        logger.info(f'render_keyword - {len(self.keywords)}')

        keyword_partial_dir = Path(
            self.src_dir, 'layouts', 'partials', 'keyword', 'list.html')

        await keyword_partial_dir.write_text(
            await self.template.render_keyword_partial(self.keywords)
        )

        async def _render_contribution(capacity_limiter: CapacityLimiter, keyword: KeywordData) -> None:
            async with capacity_limiter:

                contributions = [
                    c for c in self.contributions
                    if len(c.keywords) > 0 and keyword in c.keywords
                ]

                # logger.info(f"{session} -> {len(contributions)}")

                await Path(self.src_keyword_dir, f'{keyword.code.lower()}.md').write_text(
                    await self.template.render_keyword_page(self.event, keyword, contributions)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for keyword in self.keywords:
                if keyword and keyword.code:
                    tg.start_soon(_render_contribution,
                                  capacity_limiter, keyword)

        # await Path(self.src_keyword_dir, '_index.html').write_text(
        #     await self.template.render_keyword_list(self.keywords)
        # )
#
        # async def _render_contribution(capacity_limiter: CapacityLimiter, keyword: KeywordData) -> None:
        #     async with capacity_limiter:
        #         curr_dir = Path(self.src_keyword_dir, keyword.code.lower())
        #         await curr_dir.mkdir(parents=True, exist_ok=True)
#
        #         contributions = [
        #             c for c in self.contributions
        #             if len(c.keywords) > 0 and keyword in c.keywords
        #         ]
#
        #         # logger.info(f"{keyword} -> {len(contributions)}")
#
        #         await Path(curr_dir, '_index.html').write_text(
        #             await self.template.render_keyword_page(
        #                 self.event, keyword, contributions)
        #         )
#
        # capacity_limiter = CapacityLimiter(4)
        # async with create_task_group() as tg:
        #     for keyword in self.keywords:
        #         tg.start_soon(_render_contribution, capacity_limiter, keyword)

    async def render_doi_contributions(self) -> None:
        """"""

        logger.info(f"render_doi_contributions")

        await Path(self.src_doi_dir, '_index.html').write_text(
            await self.template.render_doi_list(self.event, self.contributions)
        )

        async def _render_doi_contribution(capacity_limiter: CapacityLimiter, code: str, doi_contribution: ContributionDOI) -> None:
            async with capacity_limiter:

                # logger.info(f"{code} - {doi_contribution.title}")

                await Path(self.src_doi_dir, f"{code.lower()}.md").write_text(
                    await self.template.render_doi_contribution(doi_contribution)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:
            for contribution in self.contributions:
                if contribution.is_qa_approved and contribution.code and contribution.doi_data:
                    tg.start_soon(_render_doi_contribution, capacity_limiter,
                                  contribution.code, contribution.doi_data)

    async def render_references(self) -> None:
        """"""

        logger.info(f"render_references")

        async def _render_reference_contribution(capacity_limiter: CapacityLimiter, contribution_code: str,
                                                 contribution_title: str, reference_type: str,
                                                 reference: str) -> None:
            async with capacity_limiter:
                await Path(self.src_ref_dir, f"{contribution_code.lower()}-{reference_type}.html").write_text(
                    await self.template.render_reference(contribution_code, contribution_title, reference_type, reference)
                )

        capacity_limiter = CapacityLimiter(4)
        async with create_task_group() as tg:

            # generate all references for every contribution
            for contribution in self.contributions:
                if contribution.reference:
                    reference_dict = contribution.reference.as_dict()
                    for reference_type in reference_dict:
                        tg.start_soon(_render_reference_contribution, capacity_limiter, contribution.code,
                                      contribution.title, reference_type,
                                      reference_dict.get(reference_type))

    async def static(self) -> None:
        pass

    async def finalize(self) -> None:
        pass

    async def ssg_cmd(self):
        return await Path('bin', 'hugo').absolute()

    async def generate(self) -> None:
        """ """

        logger.info('event_final_proceedings - plugin.generate')

        try:

            ssg_cmd = await self.ssg_cmd()

            ssg_args = [f"{ssg_cmd}", "--templateMetrics",
                        "--source", f"{self.src_dir}",
                        "--destination", "out"]

            result = await run_process(ssg_args)

            if result.returncode == 0:
                logger.info(result.stdout.decode())
            else:
                logger.info(result.stderr.decode())

        except BaseException as e:
            logger.error("hugo:generate", e, exc_info=True)

    async def compress(self) -> None:
        """ """

        logger.info('event_final_proceedings - plugin.compress')

        zip_cmd = await self.zip_cmd()
        out_dir_path = await self.out_dir.absolute()

        zip_file = Path(self.src_dir, "out.7z")
        zip_file_path = await zip_file.absolute()

        # 7z a /tmp/12/12.7z /tmp/12/out -m0=LZMA2:d=64k -mmt=4

        # "7z.exe" a -t7z -m0=LZMA2:d64k:fb32 -ms=8m -mmt=30 -mx=1 -- "F:\BACKUP" "D:\Source"
        # -t7z sets the archive type to 7-Zip.
        # -m0=LZMA2:d64k:fb32 defines the usage of LZMA2 compression method with a dictionary size of 64 KB and a word size (fast bytes) of 32.
        # -ms=8m enables solid mode with a solid block size of 8 MB.
        # -mmt=30 enables multi-threading mode with up to 30 threads.
        # -mx=1 selects fastest compressing as level of compression.

        zip_args = [f"{zip_cmd}", "a",
                    "-t7z", "-m0=LZMA2:d64k:fb32",
                    "-ms=8m", "-mmt=8", "-mx=1", "--",
                    f"{zip_file_path}", f"{out_dir_path}",]

        result = await run_process(zip_args)

        if result.returncode == 0:
            logger.info(result.stdout.decode())
        else:
            logger.info(result.stderr.decode())

        # logger.debug(result.stdout.decode())

        # zip = await self.get_zip(zip_file_path)

        # await zip_file.unlink(True)

        # return zip

    async def clean(self) -> None:
        """ """

        # TODO: to implement

        await self.src_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"temporary directory {await self.src_dir.absolute()}")
