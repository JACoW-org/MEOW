from rdflib import RDF, URIRef, Namespace, Graph, plugin
from rdflib.serializer import Serializer
from rdflib.plugins.serializers.rdfxml import XMLSerializer
import io
import re
from datetime import date, datetime, tzinfo, timedelta
# import rdfhelpers


class XMPSerializer(XMLSerializer):

    TOOLNAME = "JACoW Conference Assembly Tool (CAT)"
    XMP_NS = "adobe:ns:meta/"
    XMP_NAME = "xmpmeta"
    XMP_TAG_OPEN = '<x:{0}'.format(XMP_NAME).encode('utf-8')
    XMP_TAG_CLOSE = '</x:{0}>'.format(XMP_NAME).encode('utf-8')
    XMP_TAG_OPEN_FULL = \
        '<x:{0} xmlns:x="{1}" x:xmptk="{2}">\n'.format(
            XMP_NAME, XMP_NS, TOOLNAME).encode('utf-8')

    # We cannot use RDF.li because RDF is a closed namespace
    RDFLI = str(RDF) + "li"

    def __init__(self, store):
        super().__init__(store)

    def serialize(self, stream, base=None, encoding=None, xmpfile=None, **args):
        stream.write(self.XMP_TAG_OPEN_FULL)
        xmlstream = io.BytesIO()
        super().serialize(xmlstream, base=base, encoding=encoding, **args)
        rdf = io.BytesIO(xmlstream.getvalue())
        rdf.readline()  # this is all ugly code, but we must skip the initial XML declaration
        for line in rdf.readlines():
            stream.write(line)
        stream.write(self.XMP_TAG_CLOSE)

    # def predicate(self, pred, obj, depth=1):
    #     # Replace actual container item predicates with <rdf:li> as per the XMP spec
    #     super().predicate(self.RDFLI if rdfhelpers.isContainerItemPredicate(pred) else pred,
    #                       obj, depth)


plugin.register("xmp", Serializer, "meow.utils.xmp", "XMPSerializer")


DC = Namespace("http://purl.org/dc/elements/1.1/")
XMP = Namespace("http://ns.adobe.com/xap/1.0/")
PDF = Namespace("http://ns.adobe.com/pdf/1.3/")
EXIF = Namespace("http://ns.adobe.com/exif/1.0/")
CRS = Namespace("http://ns.adobe.com/camera-raw-settings/1.0/")
DCT = Namespace("http://purl.org/dc/terms/")


""" 
def adjustTriple(triple, node_map, check_predicates=False):
    s, p, o = triple
    for node in node_map:
        if s == node:
            s = node_map[node]
        if check_predicates and p == node:
            p = node_map[node]
        if o == node:
            o = node_map[node]
    return s, p, o


def adjustNodes(node_map, source_graph, destination_graph=None, check_predicates=False):
    if destination_graph is None:
        destination_graph = type(source_graph)()
    for triple in source_graph:
        destination_graph.add(adjustTriple(
            triple, node_map, check_predicates=check_predicates))
    if isinstance(destination_graph, XMPMetadata):
        destination_graph.url = node_map[source_graph.url]
        destination_graph.sourceIsXMP = False
    return destination_graph


def adjustNodesInPlace(node_map, graph, check_predicates=False):
    for triple in list(graph.triples((None, None, None))):
        new_triple = adjustTriple(
            triple, node_map, check_predicates=check_predicates)
        if new_triple != triple:
            graph.add(new_triple)
            graph.remove(triple)
    if isinstance(graph, XMPMetadata):
        graph.url = node_map[graph.url]
    return graph 
"""


class iso8601:
    patterns =\
        {'iso8601': (("(?P<y>[0-9]{4})-(?P<mo>[0-9]{2})-(?P<d>[0-9]{2})"
                      "(?:T(?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2})(?:[.](?P<f>[0-9]+))?"
                      "(?P<z>[-+Z](?:(?P<oh>[0-9]{2}):(?P<om>[0-9]{2}))?)?)?$"),
                     True),
         'exif': (("(?P<y>[0-9]{4}):(?P<mo>[0-9]{2}):(?P<d>[0-9]{2})"
                   "(?:[ ](?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2}))?"),
                  False)}

    def __init__(self):
        self.re = dict()
        self.tz = dict()
        for key in self.patterns:
            (pattern, self.tz[key]) = self.patterns[key]
            self.re[key] = re.compile(pattern)

    def parse(self, string):
        for key in self.re:
            match = self.re[key].match(string)
            if match:
                (y, mo, d, h, m, s, f) = match.group(
                    "y", "mo", "d", "h", "m", "s", "f")
                if not h:
                    return date(int(y), int(mo), int(d))
                else:
                    fraction = 0
                    if f:
                        n = len(f)
                        if n > 6:
                            raise ValueError(
                                "At most microsecond precision is allowed: ." + f)
                        else:
                            fraction = int(f) * 10 ** (6 - n)
                    if self.tz[key]:
                        (z, oh, om) = match.group("z", "oh", "om")
                        return datetime(int(y), int(mo), int(d), int(h), int(m), int(s), fraction,
                                        timezone(0 if z[0] == 'Z' else oh,
                                                 0 if z[0] == 'Z' else om,
                                                 z[0] == '-'))
                    else:
                        return datetime(int(y), int(mo), int(d), int(h), int(m), int(s), fraction,
                                        timezone())
        return None


class timezone(tzinfo):
    def __init__(self, oh=0, om=0, negative=False):
        m = (int(oh) if oh else 0) * 60 + (int(om) if om else 0)
        self.offset = timedelta(minutes=(-m if negative else m))

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return None


class XMPMetadata(Graph):
    iso8601 = iso8601()

    def __init__(self, url):
        self.url = url

        super().__init__(identifier=self.url)

        self.bind("dc", DC)
        self.bind("xmp", XMP)
        self.bind("pdf", PDF)
        self.bind("exif", EXIF)
        self.bind("crs", CRS)
        self.bind("dct", DCT)

        self.paper = URIRef(self.url)

    def set(self, key, val):
        self.add((self.paper, key, val))

    def to_xml(self):

        out = io.BytesIO()

        val = self.serialize(out, format="xmp")

        out.seek(0)

        val = out.getvalue()

        return val.decode('utf-8')

    # def cbd(self, resource=None, target=None, context=None):
    #     # Does not support reified statements (yet)
    #     return rdfhelpers.cbd(self, target or Graph(), resource or self.url, context=context)
