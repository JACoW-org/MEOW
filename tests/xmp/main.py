
from io import BytesIO

from anyio import Path

from meow.utils.xmp import DC, XMP, PDF, XMPMetadata
from rdflib.term import Literal
from rdflib import FOAF, Graph, RDF, URIRef, Seq

from fitz import Document


async def main() -> None:

    # read in metadata
    meta = XMPMetadata("https://doi.org/10.18429/JACoW-FEL2022-MOA03")

    meta.set(DC.date, Literal("CAT subject"))

    meta.set(DC.title, Literal("CAT title"))
    meta.set(DC.description, Literal("CAT description"))
    meta.set(DC.language, Literal("CAT language"))
    meta.set(DC.creator, Literal("CAT creator"))
    meta.set(URIRef('http://purl.org/dc/terms/format'), Literal("application/pdf"))
    meta.set(PDF.Keywords, Literal("CAT keywords"))
    meta.set(XMP.CreatorTool, Literal("CAT creator tool"))
    meta.set(XMP.Identifier, Literal("CAT dentifier"))
    meta.set(XMP.MetadataDate, Literal("CAT MetadataDate"))
    meta.set(XMP.CreateDate, Literal("CAT CreateDate"))

    doc = Document(filename='FRAI1.pdf')

    doc.set_xml_metadata(meta.to_xml())

    doc.save(filename='FRAI1.cat.pdf', linear=1,
             deflate=1, garbage=1, clean=1)
