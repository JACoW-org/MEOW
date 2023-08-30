import logging as lg
from typing import Any, Callable

from anyio import Path, create_task_group, start_blocking_portal

from rdflib import URIRef
from rdflib.term import Literal
from unidecode import unidecode

from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionPaperData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.event_pdf_utils import draw_frame_anyio, pdf_metadata_qpdf

from meow.utils.xmp import DC, PDF, XMP, XMPMetadata

from concurrent.futures import as_completed


logger = lg.getLogger(__name__)


async def write_papers_metadata(proceedings_data: ProceedingsData, cookies: dict,
                                settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - write_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)

    logger.info(f'write_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    pdf_cache_dir: Path = Path('var', 'run', dir_name)
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    sessions_dict: dict[str, SessionData] = dict()
    for session in proceedings_data.sessions:
        sessions_dict[session.code] = session

    with start_blocking_portal() as portal:
        futures = [
            portal.start_task_soon(write_metadata_task,
                                   current_paper, sessions_dict,
                                   settings, pdf_cache_dir)
            for current_paper in papers_data
        ]

        for future in as_completed(futures):
            pass

    return proceedings_data


async def write_metadata_task(current_paper, sessions, settings, pdf_cache_dir):
    contribution: ContributionData = current_paper.contribution

    session: SessionData = sessions.get(contribution.session_code)
    current_file = current_paper.paper

    original_pdf_name = f"{current_file.filename}"
    original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

    jacow_pdf_name = f"{current_file.filename}_jacow"
    jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

    if await jacow_pdf_file.exists():
        await jacow_pdf_file.unlink()

    join_pdf_name = f"{current_file.filename}_join"
    join_pdf_file = Path(pdf_cache_dir, join_pdf_name)

    if await join_pdf_file.exists():
        await join_pdf_file.unlink()

        # logger.debug(f"{pdf_file} {pdf_name}")

        # await copy(str(original_pdf_file), str(jacow_pdf_file))

    header_data: dict | None = get_header_data(contribution)
    footer_data: dict | None = get_footer_data(contribution, session)

    # metadata_mutool = get_metadata_mutool(contribution)
    metadata_pikepdf = get_metadata_pikepdf(contribution)

    # xml_metadata_mutool = get_xml_metatdata_mutool(contribution)
    xml_metadata_pikepdf = get_xml_metatdata_pikepdf(contribution)

    pre_print: str = unidecode(settings.get('pre_print', 'This is a preprint')
                               if contribution.peer_reviewing_accepted else '')

    async def _task_one():
        await draw_frame_anyio(str(original_pdf_file), str(jacow_pdf_file),
                               contribution.page, pre_print, header_data,
                               footer_data, None, None, True)

        await pdf_metadata_qpdf(str(jacow_pdf_file), metadata_pikepdf, xml_metadata_pikepdf)

    async def _task_two():
        await draw_frame_anyio(str(original_pdf_file), str(join_pdf_file),
                               contribution.page, pre_print, header_data,
                               footer_data, None, None, False)

    async with create_task_group() as tg:
        tg.start_soon(_task_one)
        tg.start_soon(_task_two)


def get_metadata_mutool(contribution: ContributionData) -> dict[str, Any] | None:

    if not contribution.doi_data:
        return None

    # "author": "Author",
    # "producer": "Producer",
    # "creator": "Creator",
    # "title": "Title",
    # "format": None,
    # "encryption": None,
    # "creationDate": "CreationDate",
    # "modDate": "ModDate",
    # "subject": "Subject",
    # "keywords": "Keywords",
    # "trapped": "Trapped",

    metadata = dict(
        author=contribution.authors_meta,
        producer=contribution.producer_meta,
        creator=contribution.creator_meta,
        title=contribution.title_meta,
        format='application/pdf',
        encryption=None,
        creationDate=contribution.doi_data.reception_date_iso,
        modDate=contribution.doi_data.acceptance_date_iso,
        subject=contribution.track_meta,
        keywords=contribution.keywords_meta,
        trapped=None,
    )

    return metadata


def get_metadata_pikepdf(contribution: ContributionData) -> dict[str, Any] | None:

    if not contribution.doi_data:
        return None

    metadata = {
        '/Author': contribution.authors_meta,
        '/Producer': contribution.producer_meta,
        '/Creator': contribution.creator_meta,
        '/Title': contribution.title_meta,
        '/CreationDate': contribution.doi_data.reception_date_iso,
        '/ModDate': contribution.doi_data.acceptance_date_iso,
        '/Subject': contribution.track_meta,
        '/Keywords': contribution.keywords_meta,
    }

    # "/Author": "F. Pannek, S. Ackermann, E. Ferrari, L. Schaper, W. Hillert",
    # "/CreationDate": "17 August 22",
    # "/Creator": "Journals of Accelerator Conferences Website (JACoW)",
    # "/Keywords": "bunching, laser, radiation, electron, electronics",
    # "/ModDate": "25 August 22",
    # "/PTEX.Fullbanner": "This is pdfTeX, Version 3.14159265-2.6-1.40.20 ",
    # "/Subject": "PRIMO / Seeded FEL",
    # "/Title": "Sensitivity of Echo-Enabled Harmonic Generation to Seed Power Variations"

    return metadata


def get_xml_metatdata_mutool(contribution: ContributionData) -> str | None:

    if not contribution.doi_data:
        return None

    meta = XMPMetadata(contribution.doi_data.doi_url)

    meta.set(DC.title, Literal(contribution.title_meta))
    meta.set(DC.subject, Literal(contribution.track_meta))
    meta.set(DC.description, Literal(contribution.doi_data.abstract))
    meta.set(DC.language, Literal("en-us"))
    meta.set(URIRef('http://purl.org/dc/terms/format'),
             Literal("application/pdf"))
    meta.set(DC.creator, Literal(contribution.authors_meta))
    meta.set(PDF.Keywords, Literal(contribution.keywords_meta))
    meta.set(PDF.Producer, Literal(contribution.producer_meta))
    meta.set(XMP.CreatorTool, Literal(contribution.creator_tool_meta))
    meta.set(XMP.Identifier, Literal(contribution.doi_data.doi_identifier))
    meta.set(XMP.ModifyDate, Literal(
        contribution.doi_data.acceptance_date_iso))
    meta.set(XMP.MetadataDate, Literal(
        contribution.doi_data.acceptance_date_iso))
    meta.set(XMP.CreateDate, Literal(contribution.doi_data.reception_date_iso))

    return meta.to_xml()


def get_xml_metatdata_pikepdf(contribution: ContributionData) -> dict | None:

    if not contribution.doi_data:
        return None

    meta: dict = {
        'dc:title': contribution.title_meta,
        'dc:subject': contribution.track_meta,
        'dc:description': contribution.doi_data.abstract,
        'dc:language': 'en-us',
        'dc:creator': [contribution.authors_meta],
        'pdf:keywords': contribution.keywords_meta,
        # 'pdf:producer': contribution.producer_meta,
        'xmp:CreatorTool': contribution.creator_tool_meta,
        'xmp:Identifier': contribution.doi_data.doi_identifier,
        'xmp:ModifyDate': contribution.doi_data.acceptance_date_iso,
        # 'xmp:MetadataDate': contribution.doi_data.acceptance_date_iso,
        'xmp:CreateDate': contribution.doi_data.reception_date_iso,
    }

    # print(meta)

    return meta


def get_footer_data(contribution: ContributionData, session: SessionData) -> dict[str, str] | None:

    classificationHeader = unidecode(
        f'{contribution.track.title}' if contribution.track else '')
    sessionHeader = unidecode(
        f'{session.code}: {session.title}')

    footer_data = dict(
        classificationHeader=classificationHeader,
        sessionHeader=sessionHeader,
        contributionCode=contribution.code
    )

    return footer_data


def get_header_data(contribution: ContributionData) -> dict[str, str] | None:

    header_data = dict(
        series=unidecode(contribution.doi_data.series),
        venue=unidecode(
            f'{contribution.doi_data.conference_code},{contribution.doi_data.venue}'),
        isbn=contribution.doi_data.isbn,
        issn=contribution.doi_data.issn,
        doi=contribution.doi_data.doi_name
    ) if contribution.doi_data else None

    return header_data


def refill_contribution_metadata(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:

    current_page = 1

    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code

        try:
            if contribution_data.paper and contribution_data.paper.latest_revision:
                revision_data = contribution_data.paper.latest_revision
                file_data = revision_data.files[-1] \
                    if len(revision_data.files) > 0 \
                    else None

                if file_data is not None:

                    result: dict = results.get(file_data.uuid, {})
                    report: dict = result.get('report', {})

                    contribution_data.keywords = [
                        event_keyword_factory(keyword)
                        for keyword in result.get('keywords', [])
                    ]

                    contribution_data.page = current_page
                    contribution_data.metadata = report

                    if report and 'page_count' in report:
                        current_page += report.get('page_count', 0)

                # logger.info('contribution_data pages = %s - %s', contribution_data.page, contribution_data.page
                #   + result.get('report').get('page_count'))

        except IndexError as e:
            logger.warning(f'No keyword for contribution {code}')
            logger.error(e, exc_info=True)
        except Exception as e:
            logger.error(e, exc_info=True)

    return proceedings_data
