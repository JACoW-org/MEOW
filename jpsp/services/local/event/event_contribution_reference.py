import logging as lg

from typing import AsyncGenerator

from datetime import datetime

from jpsp.tasks.local.reference.reference import Contribution, Citation, Conference, Reference, ConferenceStatus

from jinja2 import Environment, select_autoescape, FileSystemLoader
from lxml.etree import XML, XSLT, fromstring, tostring, XMLParser
from anyio import open_file, run


logger = lg.getLogger(__name__)

class JinjaXMLBuilder:

    def __init__(self) -> None:
        self.env = Environment(
            enable_async=True,
            autoescape=select_autoescape(),
            loader=FileSystemLoader('jinja/reference')
        )
    
    async def build_reference_xml(self, contribution: Contribution) -> str:
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

    xml_builder = JinjaXMLBuilder()
    # conference_code = event.get('title')
    # conference_date = datetime.strptime(event.get('start_dt').get('date'), '%Y-%m-%d')
    # conference_location = event.get('location')

    # conference = Conference(
    #     status=ConferenceStatus.UNPUBLISHED,
    #     code=conference_code,
    #     month=conference_date.month,
    #     year=conference_date.year,
    #     venue=conference_location
    # )

    for session in event.get('sessions', []):
        # logger.info(session)
        
        for contribution in session.get('contributions', []):
            #logger.info(contribution)

            data = Contribution(
                conference_status=ConferenceStatus.UNPUBLISHED.value,
                conference_code=event.get('title'),
                venue=event.get('location'),
                start_date=event.get('start_dt').get('date'),
                end_date=event.get('end_dt').get('date'),
                paper_code=contribution.get('code'),
                primary_authors=contribution.get('primary_authors'),
                title=contribution.get('title'),
                url=contribution.get('url')
            )

            if data.is_citable():
                # build contribution xml with jinja
                xml_val = await xml_builder.build_reference_xml(data)
                doc = fromstring(xml_val, parser=XMLParser(encoding='utf-8'))

                bibtex_ref = xslt_functions.get('bibtex')(doc)
                latex_ref = xslt_functions.get('latex')(doc)

                references=dict(
                    code=contribution.get('code'),
                    bibtex=str(bibtex_ref, encoding='utf-8'),
                    latex=str(latex_ref, encoding='utf-8')
                )

                # bibtex
                # async with await open_file('xslt/bibtex.xml') as f:
                #     xslt_root = XML(await f.read(), XMLParser(encoding='utf-8'))
                #     xslt_tran = XSLT(xslt_root)

                #     result = str(xslt_tran(doc), encoding='utf-8')

                #     # print(result)

                #     references['bibtex'] = result

                yield dict(
                    type='progress',
                    value=references
                )

            # reference = Reference(
            #     paper_id=contribution.get('code'),
            #     authors=contribution.get('primary_authors'),
            #     title=session['title'],
            #     url=contribution.get('url')
            # )

            # citation = Citation(conference, reference)

            # if citation.is_citable():
                
            #     logger.info(f'\n{citation.to_latex()}')

            #     yield dict(
            #         type='progress',
            #         value=dict(
            #             code=contribution.get('code'),
            #             bibtex=citation.to_bibtex(),
            #             latex=citation.to_latex(),
            #             word=citation.to_word(),
            #             ris=citation.to_ris(),
            #             xml=citation.to_xml(),
            #         )
            #     )


    yield dict(
        type='final',
        value={}
    )
