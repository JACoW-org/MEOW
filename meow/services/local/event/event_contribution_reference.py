import logging as lg

from typing import AsyncGenerator

from datetime import datetime

from meow.tasks.local.reference.models import ContributionRef, ConferenceStatus

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


async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

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

    for session in event.get('sessions', []):
        # logger.info(session)
        
        for contribution in session.get('contributions', []):
            #logger.info(contribution)

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

                bibtex_ref = xslt_functions.get('bibtex')(doc)
                latex_ref = xslt_functions.get('latex')(doc)
                word_ref = xslt_functions.get('word')(doc)
                ris_ref = xslt_functions.get('ris')(doc)
                end_note_ref = xslt_functions.get('endNote')(doc)

                references=dict(
                    code=contribution.get('code'),
                    bibtex=str(bibtex_ref, encoding='utf-8'),
                    latex=str(latex_ref, encoding='utf-8'),
                    word=str(word_ref, encoding='utf-8'),
                    ris=str(ris_ref, encoding='utf-8'),
                    endNote=str(end_note_ref, encoding='utf-8')
                )

                yield dict(
                    type='progress',
                    value=references
                )


    yield dict(
        type='final',
        value={}
    )
