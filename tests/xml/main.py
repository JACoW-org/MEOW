
from anyio import to_process


xml_val: str = '''\
    <user>
        <first>mario</first>
        <last>rossi</last>
    </user>
'''

xslt_val: str = '''\
    <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:template match="/">
            <user_full><xsl:value-of select="$sel" /></user_full>
        </xsl:template>
    </xsl:stylesheet>
'''


def _main() -> str:

    from lxml.etree import XML, XSLT, fromstring, tostring

    xslt_root = XML(xslt_val, parser=None)
    xslt_tran = XSLT(xslt_root)

    doc = fromstring(xml_val, parser=None)
    result_tree = xslt_tran(doc, sel="/user/last/text()")

    return tostring(result_tree)


async def main() -> None:

    result_tree = await to_process.run_sync(_main)

    print(result_tree)
