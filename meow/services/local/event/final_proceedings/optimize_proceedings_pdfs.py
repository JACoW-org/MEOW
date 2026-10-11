import logging as lg
from datetime import datetime
from typing import Callable

from anyio import Path

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsConfig,
    ProceedingsData,
)
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    pdf_linearize_final_qpdf,
    pdf_optimize_with_metadata,
)
from meow.utils.datetime import format_datetime_doi_iso

logger = lg.getLogger(__name__)


def get_vol_xmp_metadata(event_title):
    return {
        "dc:title": f"{event_title} - Proceedings Volume",
        "dc:subject": "Proceedings Volume",
        "dc:language": "en-us",
        "dc:creator": ["JACoW - Joint Accelerator Conferences Website"],
        "xmp:CreatorTool": "JACoW Conference Assembly Tool (CAT)",
        "xmp:ModifyDate": format_datetime_doi_iso(datetime.now()),
        "xmp:CreateDate": format_datetime_doi_iso(datetime.now()),
    }


def get_vol_metadata(event_title):
    return {
        "/Author": "JACoW - Joint Accelerator Conferences Website",
        "/Producer": "JACoW Conference Assembly Tool (CAT)",
        "/Creator": "JACoW Conference Assembly Tool (CAT)",
        "/Title": f"{event_title} - Proceedings Volume",
        "/CreationDate": format_datetime_doi_iso(datetime.now()),
        "/ModDate": format_datetime_doi_iso(datetime.now()),
        "/Subject": "The complete volume of papers",
        "/Keywords": f"JACoW, {event_title}, Proceedings",
    }


def get_brief_xmp_metadata(event_title):
    return {
        "dc:title": f"{event_title} - Proceedings at a Glance",
        "dc:subject": "Proceedings at a Glance",
        "dc:language": "en-us",
        "dc:creator": ["JACoW - Joint Accelerator Conferences Website"],
        "pdf:keywords": f"JACoW, {event_title}, Proceedings at a Glance",
        "xmp:CreatorTool": "JACoW Conference Assembly Tool (CAT)",
        "xmp:ModifyDate": format_datetime_doi_iso(datetime.now()),
        "xmp:CreateDate": format_datetime_doi_iso(datetime.now()),
    }


def get_brief_metadata(event_title):
    return {
        "/Author": "JACoW - Joint Accelerator Conferences Website",
        "/Producer": "JACoW Conference Assembly Tool (CAT)",
        "/Creator": "JACoW Conference Assembly Tool (CAT)",
        "/Title": f"{event_title} - Proceedings at a Glance",
        "/CreationDate": format_datetime_doi_iso(datetime.now()),
        "/ModDate": format_datetime_doi_iso(datetime.now()),
        "/Subject": "First page only of all papers with hyperlinks to complete versions",
        "/Keywords": f"JACoW, {event_title}, Proceedings at a Glance",
    }


DEFAULT_GARBAGE = 4


def get_garbage_level(settings: dict) -> int:
    """Garbage collection level (0-4) from the PURR setting `pdf_optimize_garbage`.

    4 (default) merges duplicate objects and streams: the best reduction, but
    slower. If the optimization fails, a lower level (e.g. 2) can be set and
    the generation repeated.
    """
    value = settings.get("pdf_optimize_garbage")

    if value in (None, ""):
        return DEFAULT_GARBAGE

    try:
        level = int(value)
    except (TypeError, ValueError):
        level = -1

    if not 0 <= level <= 4:
        logger.warning(f"invalid pdf_optimize_garbage={value!r}, using {DEFAULT_GARBAGE}")
        return DEFAULT_GARBAGE

    return level


async def optimize_proceedings_pdfs(
    proceedings_data: ProceedingsData,
    cookies: dict,
    settings: dict,
    config: ProceedingsConfig,
    callback: Callable,
) -> tuple[ProceedingsData, list[str]]:
    logger.info("event_final_proceedings - optimize_proceedings_pdfs")

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title
    cache_dir = Path("var", "run", f"{event_id}_tmp")
    client_logs: list[str] = []
    garbage = get_garbage_level(settings)

    for pdf_name, label, size_attr, docinfo_fn, xmp_fn in [
        (
            f"{event_id}_proceedings_brief.pdf",
            "Proceedings at a Glance",
            "proceedings_brief_size",
            get_brief_metadata,
            get_brief_xmp_metadata,
        ),
        (
            f"{event_id}_proceedings_volume.pdf",
            "Proceedings Volume",
            "proceedings_volume_size",
            get_vol_metadata,
            get_vol_xmp_metadata,
        ),
    ]:
        src = Path(cache_dir, pdf_name)
        tmp = Path(cache_dir, f"{pdf_name}.opt.pdf")
        lin = Path(cache_dir, f"{pdf_name}.lin.pdf")

        if not await src.exists():
            continue

        try:
            size_before = (await src.stat()).st_size
            logger.info(f"{label} [{pdf_name}] before: {size_before:,} bytes ({size_before / 1_000_000:.2f} MB)")

            if await pdf_optimize_with_metadata(
                str(src),
                str(tmp),
                docinfo_fn(event_title),
                xmp_fn(event_title),
                garbage,
            ) != 0:
                raise RuntimeError(f"Error optimizing {pdf_name} (garbage={garbage})")

            # linearization last: any later rewrite of the file would drop it
            if await pdf_linearize_final_qpdf(str(tmp), str(lin)) != 0:
                raise RuntimeError(f"Error linearizing {pdf_name}")

            await tmp.unlink()
            await src.unlink()
            await lin.rename(src)

            size_after = (await src.stat()).st_size
            reduction = (1 - size_after / size_before) * 100
            logger.info(f"{label} [{pdf_name}] after:  {size_after:,} bytes ({size_after / 1_000_000:.2f} MB) — reduction: {reduction:.1f}%")

            setattr(proceedings_data, size_attr, size_after)
            client_logs.append(f"{label}: {size_before / 1_000_000:.2f} MB → {size_after / 1_000_000:.2f} MB ({reduction:.1f}% reduction, garbage={garbage})")
        except Exception as be:
            logger.error(be, exc_info=True)
            await tmp.unlink(missing_ok=True)
            await lin.unlink(missing_ok=True)
            client_logs.append(
                f"{label}: optimization failed, the original file is kept"
                f" (pdf_optimize_garbage={garbage}; to retry with a lighter"
                f" garbage collection set the setting to 2 or lower)"
            )

    return proceedings_data, client_logs
