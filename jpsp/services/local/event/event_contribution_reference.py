import logging as lg

from typing import AsyncGenerator

from datetime import datetime

from jpsp.tasks.local.reference.reference import Citation, Conference, Reference, ConferenceStatus


logger = lg.getLogger(__name__)


async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    conference_code = event.get('title')
    conference_date = datetime.strptime(event.get('start_dt').get('date'), '%Y-%m-%d')
    conference_location = event.get('location')

    conference = Conference(
        status=ConferenceStatus.UNPUBLISHED,
        code=conference_code,
        month=conference_date.month,
        year=conference_date.year,
        venue=conference_location
    )

    for session in event.get('sessions', []):
        # logger.info(session)
        
        for contribution in session.get('contributions', []):
            #logger.info(contribution)

            reference = Reference(
                paper_id=contribution.get('code'),
                authors=contribution.get('primary_authors'),
                title=session['title'],
                url=contribution.get('url')
            )

            citation = Citation(conference, reference)

            if citation.is_citable():
                
                logger.info(f'\n{citation.to_bibtex()}')

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
