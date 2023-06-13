from dataclasses import dataclass, asdict, field

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import AffiliationData, AttachmentData, EventData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.track_model import TrackData


@dataclass(kw_only=True, slots=True)
class FinalProceedingsConfig:
    """ """
    
    # indica se le slide sono da includere o meno
    include_event_slides: bool = field()
    
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

    proceedings_volume_size: int = field(default=0)
    proceedings_brief_size: int = field(default=0)

    def as_dict(self) -> dict:
        return asdict(self)
