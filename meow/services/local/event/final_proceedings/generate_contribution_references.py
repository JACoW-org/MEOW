import logging as lg
import re
from os import path

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import EventData

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    FinalProceedingsConfig, ProceedingsData)

from meow.tasks.local.reference.models import ContributionRef, ReferenceStatus, Reference
from meow.tasks.local.doi.utils import  generate_doi_name
from jinja2 import BytecodeCache, Environment, FileSystemLoader
from lxml.etree import XML, XSLT, fromstring, XMLParser

from anyio import open_file, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.utils.datetime import format_datetime_dashed, format_datetime_month_name, format_datetime_year_num
from typing import Callable


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


class JinjaXMLBuilder:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            auto_reload=False,
            cache_size=1024,
            autoescape=True,
            bytecode_cache=FileSystemCache("var/cache/reference"),
            loader=FileSystemLoader('jinja/reference')
        )

    async def build_reference_xml(self, contribution: ContributionRef) -> str:
        return await self.env.get_template('reference.xml.jinja')\
            .render_async(contribution.as_dict())


async def generate_contribution_references(proceedings_data: ProceedingsData, cookies: dict,
                                           settings: dict, config: FinalProceedingsConfig,
                                           callable: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - extract_contribution_references')

    total_files: int = len(proceedings_data.contributions)
    processed_files: int = 0

    xml_builder: JinjaXMLBuilder = JinjaXMLBuilder()

    xslt_functions: dict[str, XSLT] = await get_xslt_functions()

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    results: dict[str, Reference] = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for contribution_data in proceedings_data.contributions:
                tg.start_soon(reference_task, capacity_limiter, proceedings_data.event,
                              contribution_data, xml_builder, xslt_functions, settings,
                              config, callable, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:
                    processed_files = processed_files + 1

                    # logger.info(result)

                    result_code: str = result.get('code', None)
                    result_value: Reference | None = result.get('value', None)

                    if result_value is not None:
                        results[result_code] = result_value

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    proceedings_data = refill_contribution_reference(proceedings_data, results)

    return proceedings_data


async def get_xslt_functions() -> dict[str, XSLT]:

    xslt_functions: dict[str, XSLT] = dict()

    async def xslt_task(code: str, path: str) -> None:
        xslt_functions[code] = await get_xslt(path)

    async with create_task_group() as tg:
        tg.start_soon(xslt_task, 'bibtex', 'xslt/bibtex.xml')
        tg.start_soon(xslt_task, 'latex', 'xslt/latex.xml')
        tg.start_soon(xslt_task, 'word', 'xslt/word.xml')
        tg.start_soon(xslt_task, 'ris', 'xslt/ris.xml')
        tg.start_soon(xslt_task, 'endnote', 'xslt/endnote.xml')

    return xslt_functions


async def reference_task(capacity_limiter: CapacityLimiter, event: EventData,
                         contribution: ContributionData, xml_builder, xslt_functions: dict,
                         settings: dict, config: FinalProceedingsConfig, callable: Callable,
                         res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        await res.send({
            "code": contribution.code,
            "value": await build_contribution_reference(event, contribution, xml_builder,
                                                        xslt_functions, settings, config, callable)
        })


async def get_xslt(xslt_path: str) -> XSLT:
    async with await open_file(xslt_path) as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        return XSLT(xslt_root)  # type: ignore


async def build_contribution_reference(event: EventData, contribution: ContributionData,
                                       xml_builder, xslt_functions: dict, settings: dict,
                                       config: FinalProceedingsConfig, callable: Callable) -> Reference | None:

    xml_val: str = ''

    try:

        contribution_ref = await contribution_data_factory(event, contribution, settings, config, callable)

        if contribution_ref.is_citable():

            xml_val = await xml_builder.build_reference_xml(contribution_ref)

            doc = fromstring(xml_val, parser=XMLParser(
                encoding='utf-8', recover=True))

            return Reference(
                bibtex=await xslt_transform(xslt_functions, 'bibtex', doc),
                latex=await xslt_transform(xslt_functions, 'latex', doc),
                word=await xslt_transform(xslt_functions, 'word', doc),
                ris=await xslt_transform(xslt_functions, 'ris', doc),
                endnote=await xslt_transform(xslt_functions, 'endnote', doc)
            )

    except Exception as ex:
        logger.error(ex, exc_info=True)
        logger.error(xml_val)

    return None


async def contribution_data_factory(event: EventData, contribution: ContributionData, settings: dict,
                                    config: FinalProceedingsConfig, callable: Callable) -> ContributionRef:

    reference_status: str = ReferenceStatus.IN_PROCEEDINGS.value if contribution.has_paper(
    ) else ReferenceStatus.UNPUBLISHED.value

    reference_doi: str = generate_doi_name(
        context=settings.get('doi_context', '10.18429'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    ) if callable(contribution) > 0 else ''

    isbn: str = settings.get('isbn', '978-3-95450-227-1')
    issn: str = settings.get('issn', '2673-5490')

    booktitle_short: str = settings.get('booktitle_short', '')
    booktitle_long: str = settings.get('booktitle_long', '')
    series: str = settings.get('series', '')
    series_number: str = settings.get('series_number', '')

    number_of_pages = contribution.metadata.get(
        'page_count', 0) if contribution.metadata is not None else 0

    location: str = settings.get('location', '')

    conference_code = re.sub(r'[^a-zA-Z]', '', event.name).lower() + str(event.start.year)

    return ContributionRef(
        url=contribution.url,
        title=contribution.title,
        booktitle_short=booktitle_short,
        booktitle_long=booktitle_long,
        paper_code=contribution.code,
        conference_code=conference_code,
        series=series,
        series_number=series_number,
        venue=location,
        abstract=contribution.description,
        year=format_datetime_year_num(event.start),
        month=format_datetime_month_name(event.start),
        start_date=format_datetime_dashed(event.start),
        end_date=format_datetime_dashed(event.end),
        authors_list=contribution.authors_list,
        status=reference_status,
        start_page=contribution.page,
        number_of_pages=number_of_pages,
        doi=reference_doi,
        isbn=isbn,
        issn=issn,
        keywords=[k.name for k in contribution.keywords]
    )


async def xslt_transform(xslt_functions: dict[str, XSLT], code: str, doc) -> str:
    transform: XSLT | None = xslt_functions.get(code)
    value = transform(doc) if transform else None
    return str(value) if value else ''


def refill_contribution_reference(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:
    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code

        if code in results:
            contribution_data.reference = results[code]

    return proceedings_data
