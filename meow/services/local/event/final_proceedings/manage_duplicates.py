import logging as lg
import re
from typing import Any, Callable

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


def is_duplicate_metadata_sync_enabled(settings: dict) -> bool:
    """Check if duplicate metadata synchronisation is enabled in settings (default True)."""
    candidate_keys = [
        "sync_duplicate_metadata",
        "duplicate_sync_metadata",
        "sync_duplicates",
        "sync_duplicate_of",
        "duplicate_of_sync",
    ]
    for key in candidate_keys:
        if key in settings:
            val = settings[key]
            if val is None:
                continue
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return bool(val)
            if isinstance(val, str):
                v = val.strip().lower()
                if v in ("false", "0", "no", "off", "disable", "disabled"):
                    return False
                if v in ("true", "1", "yes", "on", "enable", "enabled"):
                    return True
    return True


def _item_code(c: Any) -> str | None:
    if isinstance(c, dict):
        val = c.get("code")
        return str(val) if val is not None else None
    if hasattr(c, "code"):
        return str(c.code) if c.code is not None else None
    return None


def _item_ids(c: Any) -> list[str]:
    res: list[str] = []
    if isinstance(c, dict):
        for k in ("id", "friendly_id"):
            val = c.get(k)
            if val is not None:
                s = str(val).strip()
                if s and s not in res:
                    res.append(s)
    else:
        for attr in ("id", "friendly_id"):
            if hasattr(c, attr):
                val = getattr(c, attr)
                if val is not None:
                    s = str(val).strip()
                    if s and s not in res:
                        res.append(s)
    return res


def get_duplicate_of_code(
    contribution: Any, duplicate_of_alias: str | None = None
) -> str | None:
    """Extract duplicate_of reference value from ContributionData or dict."""
    if hasattr(contribution, "duplicate_of_code") and callable(
        getattr(contribution, "duplicate_of_code")
    ):
        return contribution.duplicate_of_code(duplicate_of_alias)

    if not isinstance(contribution, dict):
        return None

    dup_val = contribution.get("duplicate_of")
    if isinstance(dup_val, str) and dup_val.strip():
        return dup_val.strip()
    if isinstance(dup_val, dict) and dup_val.get("code"):
        return str(dup_val["code"]).strip()
    if hasattr(dup_val, "code") and dup_val.code:
        return str(dup_val.code).strip()

    aliases: list[str] = []
    for candidate in [duplicate_of_alias, "CAT_duplicate_of", "duplicate_of"]:
        if candidate and candidate.strip():
            c_norm = candidate.strip().casefold()
            if c_norm not in aliases:
                aliases.append(c_norm)

    field_values = contribution.get("field_values", [])
    if isinstance(field_values, list):
        for field in field_values:
            name = None
            val = None
            if isinstance(field, dict):
                name = field.get("name")
                val = field.get("value")
            elif hasattr(field, "name") and hasattr(field, "value"):
                name = field.name
                val = field.value
            if name and str(name).strip().casefold() in aliases and val:
                return str(val)

    return None


def find_duplicate_contribution(
    contributions: list[Any],
    duplicate_of_raw: str,
    current_contribution: Any | None = None,
) -> Any | None:
    """Find the original contribution referenced by duplicate_of_raw.

    Supports:
    - Programme code matching (e.g. 'THP123', case-insensitive)
    - Numeric Indico contribution ID matching (e.g. '12952')
    - Text phrases (e.g. 'Cloned from contribution: 12952')
    - Both ContributionData instances and raw dictionary representations.
    """
    if not duplicate_of_raw or not str(duplicate_of_raw).strip():
        return None

    raw = str(duplicate_of_raw).strip()
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
                or (
                    _item_code(c)
                    and _item_code(current_contribution)
                    and _item_code(c) == _item_code(current_contribution)
                )
            ):
                continue
            code = _item_code(c)
            if code and code.strip().lower() == cand_lower:
                return c

    # 2. Second priority: match by contribution ID / friendly_id
    for cand in candidates:
        cand_lower = cand.lower()
        for c in contributions:
            if current_contribution and (
                c is current_contribution
                or (
                    _item_ids(c)
                    and _item_ids(current_contribution)
                    and set(_item_ids(c)).intersection(
                        set(_item_ids(current_contribution))
                    )
                )
            ):
                continue
            for cid in _item_ids(c):
                if cid.lower() == cand_lower:
                    return c

    return None


async def manage_duplicates(
    proceedings_data: ProceedingsData, settings: dict
) -> ProceedingsData:
    """"""

    logger.info("event_final_proceedings - manage_duplicates")

    duplicate_of_alias = settings.get("duplicate_of_alias", "duplicate_of")
    sync_metadata = is_duplicate_metadata_sync_enabled(settings)

    proceedings_data = resolve_duplicate_contributions(
        proceedings_data, duplicate_of_alias, sync_metadata=sync_metadata
    )

    return proceedings_data


def resolve_duplicate_contributions(
    proceedings_data: ProceedingsData,
    duplicate_of_alias: str,
    sync_metadata: bool = True,
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

                # Synchronise metadata (CAT issue #35) if enabled
                if sync_metadata:
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


def resolve_duplicate_contributions_dicts(
    contributions: list[dict],
    settings: dict,
) -> list[dict]:
    """Resolve duplicate contributions and synchronise metadata for contribution dicts (e.g. in Abstract Booklet)."""
    duplicate_of_alias = settings.get("duplicate_of_alias", "duplicate_of")
    sync_metadata = is_duplicate_metadata_sync_enabled(settings)

    for contribution in contributions:
        if not isinstance(contribution, dict):
            continue

        duplicate_of_code = get_duplicate_of_code(contribution, duplicate_of_alias)
        if duplicate_of_code:
            duplicate = find_duplicate_contribution(
                contributions,
                duplicate_of_code,
                current_contribution=contribution,
            )

            if duplicate and isinstance(duplicate, dict):
                logger.info(
                    f"Resolved duplicate contribution dict: {contribution.get('code')} -> "
                    f"original={duplicate.get('code')} (id={duplicate.get('id')})"
                )
                contribution["duplicate_of"] = duplicate.get("code")

                if sync_metadata:
                    # 1. Title
                    if duplicate.get("title") is not None:
                        contribution["title"] = duplicate["title"]

                    # 2. Abstract (description)
                    if duplicate.get("description") is not None:
                        contribution["description"] = duplicate["description"]

                    # 3. Authors and affiliations
                    if (
                        "primary_authors" in duplicate
                        and duplicate["primary_authors"] is not None
                    ):
                        contribution["primary_authors"] = [
                            dict(a) if isinstance(a, dict) else a
                            for a in duplicate["primary_authors"]
                        ]
                    if "coauthors" in duplicate and duplicate["coauthors"] is not None:
                        contribution["coauthors"] = [
                            dict(a) if isinstance(a, dict) else a
                            for a in duplicate["coauthors"]
                        ]
                    if "authors" in duplicate and duplicate["authors"] is not None:
                        contribution["authors"] = [
                            dict(a) if isinstance(a, dict) else a
                            for a in duplicate["authors"]
                        ]
                    if (
                        "institutes" in duplicate
                        and duplicate["institutes"] is not None
                    ):
                        contribution["institutes"] = [
                            dict(i) if isinstance(i, dict) else i
                            for i in duplicate["institutes"]
                        ]

                    # 4. Keywords
                    if duplicate.get("keywords"):
                        contribution["keywords"] = list(duplicate["keywords"])

                    # 5. Speakers (fallback if duplicate has no speaker assigned)
                    if not contribution.get("speakers") and duplicate.get("speakers"):
                        contribution["speakers"] = [
                            dict(s) if isinstance(s, dict) else s
                            for s in duplicate["speakers"]
                        ]
            else:
                logger.warning(
                    f"Could not resolve duplicate contribution for {contribution.get('code', contribution.get('id'))}: "
                    f"'{duplicate_of_code}'"
                )

    return contributions


def find_predicate(code: str) -> Callable[..., bool]:
    extracted = extract_target_identifier(code).lower()
    raw = code.strip(" .:#").lower()

    def _predicate(c: ContributionData) -> bool:
        c_code = c.code.strip().lower() if c.code else ""
        c_id = str(c.id).strip().lower() if c.id is not None else ""
        return c_code in (extracted, raw) or c_id in (extracted, raw)

    return _predicate
