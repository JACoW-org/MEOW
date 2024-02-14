import logging as lg
from typing import Any, Callable

from anyio import Path, create_task_group

from rdflib import URIRef
from rdflib.term import Literal
from unidecode import unidecode

from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionPaperData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.event_pdf_utils import draw_frame_anyio, pdf_metadata_qpdf

from meow.utils.xmp import DC, PDF, XMP, XMPMetadata


logger = lg.getLogger(__name__)


async def write_papers_metadata(proceedings_data: ProceedingsData, cookies: dict,
                                settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - write_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(
        proceedings_data, callback)

    total_files: int = len(papers_data)

    logger.info(f'write_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    pdf_cache_dir: Path = Path('var', 'run', dir_name)
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    sessions_dict: dict[int, SessionData] = dict()
    for session in proceedings_data.sessions:
        sessions_dict[session.id] = session

    async with create_task_group() as tg:
        for current_paper in papers_data:
            tg.start_soon(write_metadata_task,
                          current_paper, sessions_dict,
                          settings, pdf_cache_dir)

    # with start_blocking_portal() as portal:
    #     futures = [
    #         portal.start_task_soon(write_metadata_task,
    #                                current_paper, sessions_dict,
    #                                settings, pdf_cache_dir)
    #         for current_paper in papers_data
    #     ]
    #
    #     for future in as_completed(futures):
    #         pass

    return proceedings_data


async def write_metadata_task(current_paper, sessions: dict[int, SessionData], settings, pdf_cache_dir):
    contribution: ContributionData = current_paper.contribution

    session = sessions.get(contribution.session_id)

    if not session:
        return None

    current_file = current_paper.paper

    original_pdf_name = f"{current_file.filename}"
    original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

    jacow_pdf_name = f"{current_file.filename}_jacow"
    jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

    await jacow_pdf_file.unlink(missing_ok=True)

    join_pdf_name = f"{current_file.filename}_join"
    join_pdf_file = Path(pdf_cache_dir, join_pdf_name)

    await join_pdf_file.unlink(missing_ok=True)

    header_data: dict | None = get_header_data(contribution)
    footer_data: dict | None = get_footer_data(contribution, session)

    # metadata_mutool = get_metadata_mutool(contribution)
    metadata_pikepdf: dict | None = get_metadata_pikepdf(contribution)

    # xml_metadata_mutool = get_xml_metatdata_mutool(contribution)
    xml_metadata_pikepdf: dict | None = get_xml_metatdata_pikepdf(contribution)

    pre_print: str = settings.get('pre_print', 'This is a preprint') \
        if contribution.peer_reviewing_accepted else ''

    # if pre_print != '':
    #     logger.info(f"code: {contribution.code} - preprint: {pre_print}")

    async def _task_jacow_files():
        await draw_frame_anyio(str(original_pdf_file), str(jacow_pdf_file),
                               contribution.page, pre_print, header_data,
                               footer_data, None, None, True)

        await pdf_metadata_qpdf(str(jacow_pdf_file), metadata_pikepdf,
                                xml_metadata_pikepdf)

    async def _task_concat_files():
        await draw_frame_anyio(str(original_pdf_file), str(join_pdf_file),
                               contribution.page, pre_print, header_data,
                               footer_data, None, None, False)

    async with create_task_group() as tg:
        tg.start_soon(_task_jacow_files)
        tg.start_soon(_task_concat_files)


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

    contrib_track = contribution.track.title if contribution.track else None

    classificationHeader = unidecode(contrib_track if contrib_track else '')
    sessionHeader = unidecode(f'{session.code}: {session.title}')

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
