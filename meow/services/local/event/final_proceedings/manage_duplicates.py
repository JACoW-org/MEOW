import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.contribution_model import (ContributionData,
                                                                          DuplicateContributionData)
from meow.utils.list import find
from typing import Callable

logger = lg.getLogger(__name__)


async def manage_duplicates(proceedings_data: ProceedingsData) -> ProceedingsData:
    """"""

    logger.info('event_final_proceedings - manage_duplicates')

    proceedings_data = resolve_duplicate_contributions(proceedings_data)

    return proceedings_data


def resolve_duplicate_contributions(proceedings_data: ProceedingsData) -> ProceedingsData:
    """ """

    for contribution in proceedings_data.contributions:
        duplicate_of_code: str | None = contribution.duplicate_of_code
        if duplicate_of_code:
            predicate = find_predicate(duplicate_of_code)
            duplicate_contribution: ContributionData | None = find(
                proceedings_data.contributions, predicate)
            contribution.duplicate_of = DuplicateContributionData(
                code=duplicate_contribution.code,
                session_code=duplicate_contribution.session_code,
                has_metadata=True if duplicate_contribution.metadata else False,
                doi_url=duplicate_contribution.doi_data.doi_url if duplicate_contribution.doi_data else '',
                doi_name=duplicate_contribution.doi_data.doi_name if duplicate_contribution.doi_data else '',
                doi_label=duplicate_contribution.doi_data.doi_label if duplicate_contribution.doi_data else '',
                doi_path=duplicate_contribution.doi_data.doi_path if duplicate_contribution.doi_data else '',
                doi_identifier=duplicate_contribution.doi_data.doi_identifier if duplicate_contribution.doi_data else '',
                reception=duplicate_contribution.reception,
                revisitation=duplicate_contribution.revisitation,
                acceptance=duplicate_contribution.acceptance,
                issuance=duplicate_contribution.issuance
            ) if duplicate_contribution else None

    return proceedings_data


def find_predicate(code: str) -> Callable[..., bool]:

    def _predicate(c: ContributionData) -> bool:
        return c.code == code

    return _predicate
