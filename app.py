from weasyprint import HTML
from asn1crypto import cms
from lxml import etree
import requests
from io import BytesIO

XSD_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Schema_VFPR12_v1.2.3.xsd'
XSL_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Foglio_di_stile_fattura_ordinaria_ver1.2.3.xsl'
INVOICE_FILE = "data/invoice.xml.p7m"


def extract_xml_from_p7m(p7m_path: str) -> str:
    """
    Extract the XML content from a .p7m file using asn1crypto (no subprocess).
    
    Returns the raw XML as string.
    """
    with open(p7m_path, "rb") as f:
        data = f.read()

    # Parse CMS (Cryptographic Message Syntax)
    content_info = cms.ContentInfo.load(data)
    
    if content_info['content_type'].native != 'signed_data':
        raise ValueError("Not a PKCS7 signed data structure")

    signed_data = content_info['content']
    eci = signed_data['encap_content_info']

    if eci['content_type'].native != 'data':
        raise ValueError("No embedded data found")

    xml_bytes = eci['content'].native
    return xml_bytes

def get_schema():
    return requests.get(XSD_URL).content

def get_style():
    return requests.get(XSL_URL).content

def convert_xml_p7m_to_html(xml_p7m_path: str) -> str:
    """
    Convert XML to HTML using XSLT.
    """
    xml = etree.fromstring(extract_xml_from_p7m(xml_p7m_path))
    xsl = etree.parse(BytesIO(get_style()))
    transform = etree.XSLT(xsl)
    html_result = transform(xml)
    return etree.tostring(html_result, pretty_print=True)

html_str = convert_xml_p7m_to_html(INVOICE_FILE)

with open("output.html", "wb") as f:
    f.write(html_str)

# Convert HTML to PDF using WeasyPrint
HTML(string=html_str).write_pdf("output.pdf")