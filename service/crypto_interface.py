from weasyprint import HTML
from lxml import etree
import requests
from io import BytesIO
from cryptography.hazmat.primitives.serialization import pkcs7, load_der_private_key
from asn1crypto import cms

class CryptoInterface:
    XSL_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Foglio_di_stile_fattura_ordinaria_ver1.2.3.xsl'

    def _get_style():
        return requests.get(XSL_URL).content

    def load_bytes(self, path: str) -> bytes:
        """
        Load in the file for extracting data.
        Extract bytes from p7m local file.

        Returns the content bytes
        """
        with open(path, "rb") as f:
            data = f.read()

        return data

    def convert_xml_to_html(self, xml: str) -> str:
        """
        Convert XML to HTML using XSLT.

        Return HTML string
        """
        xml = etree.fromstring(xml)
        xsl = etree.parse(BytesIO(_get_style()))
        transform = etree.XSLT(xsl)
        html_result = transform(xml)
        return etree.tostring(html_result, pretty_print=True)

    def save_html_to_file(self, output_path: str, html: str):
        """
        Save HTML string to filesystem.
        """
        with open(output_path, "wb") as f:
            f.write(html)

    def save_html_as_pdf(self, output_path: str, html: str):
        """
        Save HTML string to filesystem as PDF.
        """
        HTML(string=html).write_pdf(output_path)

    def extract_xml_from_p7m(self, data: bytes) -> str:
        """Extract XML data from P7M bytes."""
        pass


class CryptoService(CryptoInterface):
    options = [pkcs7.PKCS7Options.Text]

    def extract_xml_from_p7m(self, data: bytes) -> str:
        """
        Extract the XML content from a .pm7 file using cryptography.

        Returns the raw XML as string
        """
        # Parse CMS/PKCS#
        key = load_der_private_key(p7m_data, password=None)
        cert = pkcs7.load_der_pkcs7_certificates(p7m_data)
        return pkcs7.pkcs7_decrypt_der(p7m_data, cert, key, options)


class Asn1CryptoService(CryptoInterface):
    def extract_xml_from_p7m(self, data: bytes) -> str:
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