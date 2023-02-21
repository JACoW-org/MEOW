import logging as lg

from meow.tasks.local.reference.models import ContributionRef, ConferenceStatus, Reference
from jinja2 import Environment, FileSystemLoader
from lxml.etree import XML, XSLT, fromstring, XMLParser
from anyio import open_file

logger = lg.getLogger(__name__)

class JinjaXMLBuilder:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            autoescape=True,
            loader=FileSystemLoader('jinja/reference')
        )
    
    async def build_reference_xml(self, contribution: ContributionRef) -> str:
        return await self.env.get_template('reference.xml.jinja').render_async(contribution.as_dict())

async def gen_contribution_references(event: dict):
    ''''''

    # TODO parallelize

    # factory of xslt functions
    xslt_functions = dict()

    # bibtex
    async with await open_file('xslt/bibtex.xml') as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        xslt_functions['bibtex'] = XSLT(xslt_root)

    # latex
    async with await open_file('xslt/latex.xml') as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        xslt_functions['latex'] = XSLT(xslt_root)

    # word
    async with await open_file('xslt/word.xml') as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        xslt_functions['word'] = XSLT(xslt_root)

    # RIS
    async with await open_file('xslt/ris.xml') as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        xslt_functions['ris'] = XSLT(xslt_root)

    # endNote
    async with await open_file('xslt/end-note.xml') as f:
        xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
        xslt_functions['endNote'] = XSLT(xslt_root)

    xml_builder = JinjaXMLBuilder()
    references = dict()

    # TODO refactor with new data structure
    # TODO parallelize task
    for session in event.get('sessions', []):
        for contribution in session.get('contributions', []):
            data = ContributionRef(
                conference_status=ConferenceStatus.UNPUBLISHED.value,
                conference_code=event.get('title'),
                venue=event.get('location'),
                start_date=event.get('start_dt').get('date'),
                end_date=event.get('end_dt').get('date'),
                paper_code=contribution.get('code'),
                primary_authors=contribution.get('primary_authors'),
                title=contribution.get('title'),
                abstract=contribution.get('description'),
                url=contribution.get('url')
            )

            if data.is_citable():
                # build contribution xml with jinja
                xml_val = await xml_builder.build_reference_xml(data)
                doc = fromstring(xml_val, parser=XMLParser(encoding='utf-8'))

                contrib_reference = Reference(
                    bibtex=xslt_functions.get('bibtex')(doc),
                    latex=xslt_functions.get('latex')(doc),
                    word=xslt_functions.get('word')(doc),
                    ris=xslt_functions.get('ris')(doc),
                    end_note=xslt_functions.get('endNote')(doc)
                )

                references[contribution.get('code')] = contrib_reference

        return references
