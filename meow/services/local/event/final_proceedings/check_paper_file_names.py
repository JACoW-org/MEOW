import logging as lg
from typing import Callable

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def check_paper_file_names(proceedings_data: ProceedingsData,
                                 callback: Callable) -> list[str]:
    """Detect papers whose file is not named after the contribution code.

    Indico names the paper after the contribution code when it is uploaded
    (file type template ``{code}``): a different name means that the code
    changed after the upload. Parts of the site use the file name and others
    the code (see JACoW-org/MEOW#37), so the editors are warned. Not blocking.
    """

    logger.info("event_final_proceedings - check_paper_file_names")

    warnings: list[str] = []

    for contribution in proceedings_data.contributions:
        if not callback(contribution):
            continue

        paper_name: str | None = contribution.paper_name()
        if not paper_name or not contribution.code:
            continue

        stem = paper_name.rsplit(".", 1)[0] if "." in paper_name else paper_name
        if stem.strip().casefold() != contribution.code.strip().casefold():
            warnings.append(
                f"Paper file name mismatch: contribution {contribution.code} "
                f"has paper file '{paper_name}' instead of '{contribution.code}.pdf' "
                f"(contribution code changed after upload?)."
            )

    logger.warning(f"check_paper_file_names: {len(warnings)} warning(s) found.")
    for w in warnings:
        logger.warning(w)

    return warnings
