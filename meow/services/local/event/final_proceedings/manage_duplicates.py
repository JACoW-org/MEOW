import logging as lg
import re
from typing import Callable

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)
from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
    DuplicateContributionData,
)

logger = lg.getLogger(__name__)

EXTRACT_ID_RE = re.compile(
    r"^(?:cloned\s+from(?:\s+contribution)?|duplicate\s+of|contribution)\s*[:#\s]+\s*([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


def extract_target_identifier(raw: str) -> str:
    """Extract a candidate contribution code or numeric ID from raw string."""
    if not raw:
        return ""
    val = raw.strip()
    m = EXTRACT_ID_RE.match(val)
    if m:
        return m.group(1).strip()
    return val.strip(" .:#")


def find_duplicate_contribution(
    contributions: list[ContributionData],
    duplicate_of_raw: str,
    current_contribution: ContributionData | None = None,
) -> ContributionData | None:
    """Find the original contribution referenced by duplicate_of_raw.

    Supports:
    - Programme code matching (e.g. 'THP123', case-insensitive)
    - Numeric Indico contribution ID matching (e.g. '12952')
    - Text phrases (e.g. 'Cloned from contribution: 12952')
    """
    if not duplicate_of_raw or not duplicate_of_raw.strip():
        return None

    raw = duplicate_of_raw.strip()
    extracted = extract_target_identifier(raw)
    cleaned_raw = raw.strip(" .:#")

    candidates: list[str] = []
    for cand in [extracted, cleaned_raw]:
        if cand and cand not in candidates:
            candidates.append(cand)

    # 1. First priority: match by programme code (case-insensitive)
    for cand in candidates:
        cand_lower = cand.lower()
        for c in contributions:
            if current_contribution and (
                c is current_contribution
                or (c.code and current_contribution.code and c.code == current_contribution.code)
            ):
                continue
            if c.code and c.code.strip().lower() == cand_lower:
                return c

    # 2. Second priority: match by contribution ID
    for cand in candidates:
        cand_lower = cand.lower()
        for c in contributions:
            if current_contribution and (
                c is current_contribution
                or (
                    c.id is not None
                    and current_contribution.id is not None
                    and str(c.id).strip() == str(current_contribution.id).strip()
                )
            ):
                continue
            if c.id is not None and str(c.id).strip().lower() == cand_lower:
                return c

    return None


async def manage_duplicates(
    proceedings_data: ProceedingsData, settings: dict
) -> ProceedingsData:
    """"""

    logger.info("event_final_proceedings - manage_duplicates")

    proceedings_data = resolve_duplicate_contributions(
        proceedings_data, settings.get("duplicate_of_alias", "duplicate_of")
    )

    return proceedings_data


def resolve_duplicate_contributions(
    proceedings_data: ProceedingsData, duplicate_of_alias: str
) -> ProceedingsData:
    """Resolve duplicate contributions and synchronise metadata from original."""

    for contribution in proceedings_data.contributions:
        duplicate_of_code: str | None = contribution.duplicate_of_code(
            duplicate_of_alias
        )
        if duplicate_of_code:
            duplicate: ContributionData | None = find_duplicate_contribution(
                proceedings_data.contributions,
                duplicate_of_code,
                current_contribution=contribution,
            )

            if duplicate:
                logger.info(
                    f"Resolved duplicate contribution: {contribution.code} -> "
                    f"original={duplicate.code} (id={duplicate.id})"
                )

                contribution.duplicate_of = DuplicateContributionData(
                    code=duplicate.code,
                    session_id=duplicate.session_id,
                    session_code=duplicate.session_code,
                    has_metadata=True if duplicate.metadata else False,
                    doi_url=duplicate.doi_data.doi_url if duplicate.doi_data else "",
                    doi_name=duplicate.doi_data.doi_name if duplicate.doi_data else "",
                    doi_label=duplicate.doi_data.doi_label
                    if duplicate.doi_data
                    else "",
                    doi_path=duplicate.doi_data.doi_path if duplicate.doi_data else "",
                    doi_identifier=duplicate.doi_data.doi_identifier
                    if duplicate.doi_data
                    else "",
                    reception=duplicate.reception,
                    revisitation=duplicate.revisitation,
                    acceptance=duplicate.acceptance,
                    issuance=duplicate.issuance,
                )

                # Synchronise metadata (CAT issue #35)
                # 1. Title
                if duplicate.title is not None:
                    contribution.title = duplicate.title

                # 2. Abstract (description)
                if duplicate.description is not None:
                    contribution.description = duplicate.description

                # 3. Authors and affiliations
                contribution.primary_authors = list(duplicate.primary_authors)
                contribution.coauthors = list(duplicate.coauthors)
                contribution.authors = list(duplicate.authors)
                contribution.institutes = list(duplicate.institutes)

                # 4. Keywords
                if duplicate.keywords:
                    contribution.keywords = list(duplicate.keywords)
            else:
                logger.warning(
                    f"Could not resolve duplicate contribution for {contribution.code}: "
                    f"'{duplicate_of_code}'"
                )

    return proceedings_data


def find_predicate(code: str) -> Callable[..., bool]:
    extracted = extract_target_identifier(code).lower()
    raw = code.strip(" .:#").lower()

    def _predicate(c: ContributionData) -> bool:
        c_code = c.code.strip().lower() if c.code else ""
        c_id = str(c.id).strip().lower() if c.id is not None else ""
        return c_code in (extracted, raw) or c_id in (extracted, raw)

    return _predicate
