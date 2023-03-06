import logging as lg
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import EventData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

from meow.tasks.local.reference.models import ContributionRef, ConferenceStatus, Reference
from jinja2 import Environment, FileSystemLoader
from lxml.etree import XML, XSLT, fromstring, XMLParser

from anyio import open_file, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError
from anyio.streams.memory import MemoryObjectSendStream

from meow.utils.datetime import format_datetime_full


logger = lg.getLogger(__name__)


class JinjaXMLBuilder:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            autoescape=True,
            loader=FileSystemLoader('jinja/reference')
        )

    async def build_reference_xml(self, contribution: ContributionRef) -> str:
        return await self.env.get_template('reference.xml.jinja')\
            .render_async(contribution.as_dict())


async def extract_contribution_references(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    total_files: int = len(proceedings_data.contributions)
    processed_files: int = 0

    if total_files == 0:
        raise Exception('no contributions found')

    xslt_functions: dict[str, XSLT] = await get_xslt_functions()

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(6)

    results: dict[str, Reference] = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for contribution_data in proceedings_data.contributions:
                tg.start_soon(reference_task, capacity_limiter, proceedings_data.event,
                              contribution_data, xslt_functions, send_stream.clone())

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

        except ClosedResourceError as e:
            logger.error(e)

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
                         contribution: ContributionData, xslt_functions: dict,
                         res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        await res.send({
            "code": contribution.code,
            "value": await build_contribution_reference(event, contribution, xslt_functions)
        })


async def get_xslt(xslt_path: str) -> XSLT:
    async with await open_file(xslt_path) as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        return XSLT(xslt_root)


async def build_contribution_reference(event: EventData, contribution: ContributionData, 
                                       xslt_functions: dict) -> Reference | None:

    contribution_ref = await contribution_data_factory(event, contribution)

    if contribution_ref.is_citable():

        xml_val = await JinjaXMLBuilder().build_reference_xml(contribution_ref)
        doc = fromstring(xml_val, parser=XMLParser(encoding='utf-8'))

        return Reference(
            bibtex=await xslt_transform(xslt_functions, 'bibtex', doc),
            latex=await xslt_transform(xslt_functions, 'latex', doc),
            word=await xslt_transform(xslt_functions, 'word', doc),
            ris=await xslt_transform(xslt_functions, 'ris', doc),
            endnote=await xslt_transform(xslt_functions, 'endnote', doc)
        )

    return None


async def contribution_data_factory(event: EventData, contribution: ContributionData) -> ContributionRef:
    return ContributionRef(
        url=contribution.url,
        title=contribution.title,
        paper_code=contribution.code,
        conference_code=event.title,
        venue=event.location,
        abstract=contribution.description,
        start_date=format_datetime_full(event.start),
        end_date=format_datetime_full(event.end),
        primary_authors=contribution.primary_authors,
        conference_status=ConferenceStatus.UNPUBLISHED.value,
        start_page=contribution.page,
        number_of_pages=contribution.metadata.get(
            'report', {}).get('page_count', 0)
        if contribution.metadata is not None else 0
    )


async def xslt_transform(xslt_functions: dict[str, XSLT], code: str, doc) -> str:
    transform: XSLT | None = xslt_functions.get(code)
    value = transform(doc) if transform else None
    return str(value) if value else ''


def refill_contribution_reference(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:
    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code
        try:
            if code in results:
                contribution_data.reference = results[code]
        except Exception:
            logger.warning(f'No reference for contribution {code}')

    return proceedings_data
