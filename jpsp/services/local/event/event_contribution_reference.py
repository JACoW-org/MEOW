import logging as lg

from typing import AsyncGenerator


from jpsp.tasks.local.reference.reference import Citation, Conference, ConferenceStatus, Reference


logger = lg.getLogger(__name__)


async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """
    
    conference = Conference(ConferenceStatus.IN_PROCEEDINGS, event.get('title', ''))

    for session in event.get('sessions', []):
        # logger.info(session)
        
        for contribution in session.get('contributions', []):
            #logger.info(contribution)
            
            reference = Reference(paper_id=contribution.get('code'), authors=contribution.get('primary_authors'), title=session['title'], url=contribution.get('url'))
            citation = Citation(conference, reference)

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
