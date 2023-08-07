import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.contribution_model import (ContributionData,
                                                                          DuplicateContributionData)
from meow.utils.list import find
from typing import Callable

logger = lg.getLogger(__name__)


async def manage_duplicates(proceedings_data: ProceedingsData, settings: dict) -> ProceedingsData:
    """"""

    logger.info('event_final_proceedings - manage_duplicates')

    proceedings_data = resolve_duplicate_contributions(proceedings_data, settings.get('duplicate_of_alias', 'duplicate_of'))

    return proceedings_data


def resolve_duplicate_contributions(proceedings_data: ProceedingsData, duplicate_of_alias: str) -> ProceedingsData:
    """ """

    for contribution in proceedings_data.contributions:
        duplicate_of_code: str | None = contribution.duplicate_of_code(duplicate_of_alias)
        if duplicate_of_code:
            predicate = find_predicate(duplicate_of_code)
            duplicate: ContributionData | None = find(
                proceedings_data.contributions, predicate)
            contribution.duplicate_of = DuplicateContributionData(
                code=duplicate.code,
                session_code=duplicate.session_code,
                has_metadata=True if duplicate.metadata else False,
                doi_url=duplicate.doi_data.doi_url if duplicate.doi_data else '',
                doi_name=duplicate.doi_data.doi_name if duplicate.doi_data else '',
                doi_label=duplicate.doi_data.doi_label if duplicate.doi_data else '',
                doi_path=duplicate.doi_data.doi_path if duplicate.doi_data else '',
                doi_identifier=duplicate.doi_data.doi_identifier if duplicate.doi_data else '',
                reception=duplicate.reception,
                revisitation=duplicate.revisitation,
                acceptance=duplicate.acceptance,
                issuance=duplicate.issuance
            ) if duplicate else None

    return proceedings_data


def find_predicate(code: str) -> Callable[..., bool]:

    def _predicate(c: ContributionData) -> bool:
        return c.code == code

    return _predicate
