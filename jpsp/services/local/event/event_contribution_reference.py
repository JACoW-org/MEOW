import logging as lg

from typing import AsyncGenerator


from jpsp.tasks.local.reference.reference import Citation


logger = lg.getLogger(__name__)


async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    for session in event.get('sessions', []):
        # logger.info(session)
        
        for contribution in session.get('contributions', []):
            #logger.info(contribution)
            
            citation = Citation(
                conference_code='FEL22',
                paper_id=contribution.get('code'),
                authors=contribution.get('primary_authors'),
                title= session['title'],
                book_title='book_title',
                pages='pages',
                paper='paper',
                venue='venue',
                url=contribution.get('url')
                )

            yield dict(
                type='progress',
                value=dict(
                code=contribution.get('code'),
                bibtex=citation.to_bibtex(),
                latex=citation.to_latex(),
                word=citation.to_word(),
                ris=citation.to_ris(),
                xml=citation.to_xml(),
            )
            )


    yield dict(
        type='final',
        value={}
    )
