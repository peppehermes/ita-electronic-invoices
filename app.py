from weasyprint import HTML
from asn1crypto import cms
from cryptography.hazmat.primitives.serialization import pkcs7, load_der_private_key
from lxml import etree
import requests
from io import BytesIO

XSD_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Schema_VFPR12_v1.2.3.xsd'
XSL_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Foglio_di_stile_fattura_ordinaria_ver1.2.3.xsl'
INVOICE_FILE = "data/invoice.xml.p7m"

options = [pkcs7.PKCS7Options.Text]

def get_schema():
    return requests.get(XSD_URL).content

def get_style():
    return requests.get(XSL_URL).content

def extract_xml_from_p7m(p7m_data: str) -> str:
    """
    Extract the XML content from a .p7m file using asn1crypto.
    
    Returns the raw XML as string.
    """
    # Parse CMS (Cryptographic Message Syntax)
    content_info = cms.ContentInfo.load(p7m_data)
    
    if content_info['content_type'].native != 'signed_data':
        raise ValueError("Not a PKCS7 signed data structure")

    signed_data = content_info['content']
    eci = signed_data['encap_content_info']

    if eci['content_type'].native != 'data':
        raise ValueError("No embedded data found")

    xml_bytes = eci['content'].native
    return xml_bytes

def extract_xml_from_p7m(p7m_data: bytes) -> str:
    """
    Extract the XML content from a .pm7 file using cryptography.

    Returns the raw XML as string
    """
    # Parse CMS/PKCS#
    key = load_der_private_key(p7m_data, password=None)
    cert = pkcs7.load_der_pkcs7_certificates(p7m_data)
    return pkcs7.pkcs7_decrypt_der(p7m_data, cert, key, options)

def extract_bytes_from_p7m_file(p7m_path: str) -> bytes:
    """
    Extract bytes from p7m local file

    Returns the content bytes
    """
    with open(p7m_path, "rb") as f:
        data = f.read()

    return data

def convert_xml_p7m_to_html_asn1crypto(xml_p7m_path: str) -> str:
    """
    Convert XML to HTML using XSLT.
    """
    xml = etree.fromstring(extract_xml_from_p7m(xml_p7m_path))
    xsl = etree.parse(BytesIO(get_style()))
    transform = etree.XSLT(xsl)
    html_result = transform(xml)
    return etree.tostring(html_result, pretty_print=True)

def convert_xml_p7m_to_html_cryptography(xml_p7m_path: str) -> str:
    xml_bytes = extract_bytes_from_p7m_file(xml_p7m_path)
    xml = etree.fromstring(extract_xml_from_p7m(xml_bytes))
    xsl = etree.parse(BytesIO(get_style()))
    transform = etree.XSLT(xsl)
    html_result = transform(xml)
    return etree.tostring(html_result, pretty_print=True)

html_str = convert_xml_p7m_to_html_cryptography(INVOICE_FILE)

with open("output.html", "wb") as f:
    f.write(html_str)

# Convert HTML to PDF using WeasyPrint
HTML(string=html_str).write_pdf("output.pdf")