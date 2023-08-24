from dataclasses import dataclass, asdict, field

import json
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.track_model import TrackData
from meow.models.local.event.final_proceedings.event_model import (
    AffiliationData, AttachmentData, EventData, KeywordData, PersonData)


@dataclass(kw_only=True, slots=True)
class FinalProceedingsTask:
    """"""

    code: str = field()
    text: str = field()


@dataclass(kw_only=True, slots=True)
class FinalProceedingsConfig:
    """ """

    # indica il nome del file d agenerare per sitinguere fp da pp
    static_site_type: str = field()

    # indica se le slide sono da includere o meno
    include_event_slides: bool = field()

    # indica se il link al paper debba essere assoluto o relativo
    absolute_pdf_link: bool = field()

    # indica se considerare come contribution pubblicate tutte
    # le verdi oppure le verdi che hanno rievuto il tag QA
    include_only_qa_green_contributions: bool = field()

    # indica se generare l'url per i doi interno al sito
    # oppure se puntare al sito https://doi.org
    generate_external_doi_url: bool = field()

    # indica se interrompere il task nel caso la validazione
    # pdf produca degli errori oppure mostrare un warning
    strict_pdf_check: bool = field()

    # indica se includere la generazione dei json relativi ai doi
    generate_doi_payload: bool = field()

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class ProceedingsData:
    """ """

    event: EventData
    contributions: list[ContributionData] = field(default_factory=list)
    attachments: list[AttachmentData] = field(default_factory=list)

    sessions: list[SessionData] = field(default_factory=list)
    classification: list[TrackData] = field(default_factory=list)
    author: list[PersonData] = field(default_factory=list)
    keyword: list[KeywordData] = field(default_factory=list)
    institute: list[AffiliationData] = field(default_factory=list)
    doi_per_institute: list[AffiliationData] = field(default_factory=list)

    conference_doi: dict = field(default_factory=dict)

    proceedings_volume_size: int = field(default=0)
    proceedings_brief_size: int = field(default=0)

    @property
    def conference_doi_payload(self) -> str:

        if not self.conference_doi:
            return '{}'

        data = dict(
            id=self.conference_doi.get('id'),
            type=self.conference_doi.get('type'),
            attributes=dict(
                doi=self.conference_doi.get('doi'),
                identifiers=self.conference_doi.get('identifiers'),
                creators=self.conference_doi.get('creators'),
                titles=self.conference_doi.get('titles'),
                publisher=self.conference_doi.get('publisher'),
                publicationYear=self.conference_doi.get('publicationYear'),
                subjects=self.conference_doi.get('subjects'),
                contributors=self.conference_doi.get('contributors'),
                dates=self.conference_doi.get('dates'),
                language=self.conference_doi.get('language'),
                types=self.conference_doi.get('types'),
                relatedIdentifiers=self.conference_doi.get(
                    'relatedIdentifiers'),
                sizes=self.conference_doi.get('sizes'),
                formats=self.conference_doi.get('formats'),
                rightsList=self.conference_doi.get('rightsList'),
                descriptions=self.conference_doi.get('descriptions'),
                url=self.conference_doi.get('url'),
                schemaVersion=self.conference_doi.get('schemaVersion')
            )
        )

        return json.dumps(dict(
            data=data
        ))

    def as_dict(self) -> dict:
        return asdict(self)
