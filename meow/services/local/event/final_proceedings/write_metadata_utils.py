import logging as lg
import pathlib
from typing import Any

from anyio import Path

from rdflib import URIRef
from rdflib.term import Literal
from unidecode import unidecode

from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
)

from meow.models.local.event.final_proceedings.session_model import SessionData

from meow.utils.xmp import DC, PDF, XMP, XMPMetadata


logger = lg.getLogger(__name__)


def get_metadata_mutool(contribution: ContributionData) -> dict[str, Any] | None:
    if not contribution.doi_data:
        return None

    # "author": "Author",
    # "producer": "Producer",
    # "creator": "Creator",
    # "title": "Title",
    # "format": None,
    # "encryption": None,
    # "creationDate": "CreationDate",
    # "modDate": "ModDate",
    # "subject": "Subject",
    # "keywords": "Keywords",
    # "trapped": "Trapped",

    metadata = dict(
        author=contribution.authors_meta,
        producer=contribution.producer_meta,
        creator=contribution.creator_meta,
        title=contribution.title_meta,
        format="application/pdf",
        encryption=None,
        creationDate=contribution.doi_data.reception_date_iso,
        modDate=contribution.doi_data.acceptance_date_iso,
        subject=contribution.track_meta,
        keywords=contribution.keywords_meta,
        trapped=None,
    )

    return metadata


def get_metadata_pikepdf(contribution: ContributionData) -> dict[str, Any] | None:
    if not contribution.doi_data:
        return None

    metadata = {
        "/Author": contribution.authors_meta,
        "/Producer": contribution.producer_meta,
        "/Creator": contribution.creator_meta,
        "/Title": contribution.title_meta,
        "/CreationDate": contribution.doi_data.reception_date_iso,
        "/ModDate": contribution.doi_data.acceptance_date_iso,
        "/Subject": contribution.track_meta,
        "/Keywords": contribution.keywords_meta,
    }

    # "/Author": "F. Pannek, S. Ackermann, E. Ferrari, L. Schaper, W. Hillert",
    # "/CreationDate": "17 August 22",
    # "/Creator": "Journals of Accelerator Conferences Website (JACoW)",
    # "/Keywords": "bunching, laser, radiation, electron, electronics",
    # "/ModDate": "25 August 22",
    # "/PTEX.Fullbanner": "This is pdfTeX, Version 3.14159265-2.6-1.40.20 ",
    # "/Subject": "PRIMO / Seeded FEL",
    # "/Title": "Sensitivity of Echo-Enabled Harmonic Generation to Seed Power Variations"

    return metadata


def get_xml_metatdata_mutool(contribution: ContributionData) -> str | None:
    if not contribution.doi_data:
        return None

    meta = XMPMetadata(contribution.doi_data.doi_url)

    meta.set(DC.title, Literal(contribution.title_meta))
    meta.set(DC.subject, Literal(contribution.track_meta))
    meta.set(DC.description, Literal(contribution.doi_data.abstract))
    meta.set(DC.language, Literal("en-us"))
    meta.set(URIRef("http://purl.org/dc/terms/format"), Literal("application/pdf"))
    meta.set(DC.creator, Literal(contribution.authors_meta))
    meta.set(PDF.Keywords, Literal(contribution.keywords_meta))
    meta.set(PDF.Producer, Literal(contribution.producer_meta))
    meta.set(XMP.CreatorTool, Literal(contribution.creator_tool_meta))
    meta.set(XMP.Identifier, Literal(contribution.doi_data.doi_identifier))
    meta.set(XMP.ModifyDate, Literal(contribution.doi_data.acceptance_date_iso))
    meta.set(XMP.MetadataDate, Literal(contribution.doi_data.acceptance_date_iso))
    meta.set(XMP.CreateDate, Literal(contribution.doi_data.reception_date_iso))

    return meta.to_xml()


def get_xml_metatdata_pikepdf(contribution: ContributionData) -> dict | None:
    if not contribution.doi_data:
        return None

    meta: dict = {
        "dc:title": contribution.title_meta,
        "dc:subject": contribution.track_meta,
        "dc:description": contribution.doi_data.abstract,
        "dc:language": "en-us",
        "dc:creator": [contribution.authors_meta],
        "pdf:keywords": contribution.keywords_meta,
        # 'pdf:producer': contribution.producer_meta,
        "xmp:CreatorTool": contribution.creator_tool_meta,
        "xmp:Identifier": contribution.doi_data.doi_identifier,
        "xmp:ModifyDate": contribution.doi_data.acceptance_date_iso,
        # 'xmp:MetadataDate': contribution.doi_data.acceptance_date_iso,
        "xmp:CreateDate": contribution.doi_data.reception_date_iso,
    }

    # print(meta)

    return meta


def get_footer_data(
    contribution: ContributionData, session: SessionData
) -> dict[str, str] | None:
    contrib_track = contribution.track.title if contribution.track else None

    classificationHeader = unidecode(contrib_track if contrib_track else "")
    sessionHeader = unidecode(
        f"{session.code}: {session.title}" if session.code else session.title
    )

    footer_data = dict(
        classificationHeader=classificationHeader,
        sessionHeader=sessionHeader,
        contributionCode=contribution.code,
    )

    return footer_data


def get_header_data(contribution: ContributionData) -> dict[str, str] | None:
    header_data = (
        dict(
            series=unidecode(contribution.doi_data.series),
            venue=unidecode(
                f"{contribution.doi_data.conference_code}, {contribution.doi_data.venue}"
            ),
            isbn=contribution.doi_data.isbn,
            issn=contribution.doi_data.issn,
            doi=contribution.doi_data.doi_name,
        )
        if contribution.doi_data
        else None
    )

    return header_data


async def get_side_data(settings: dict, pdf_cache_dir: Path) -> dict[str, str]:
    license_filename: str = settings.get("paper_license_icon_url", None)
    license_logo = None
    if license_filename:
        license_logo = await Path(
            pdf_cache_dir, license_filename.split("/")[-1]
        ).read_bytes()
    else:
        license_logo = pathlib.Path("cc_by.png").read_bytes()
    side_data = {
        "license_text": settings.get(
            "paper_license_text",
            "",
        ),
        "license_logo": license_logo,
    }

    return side_data
