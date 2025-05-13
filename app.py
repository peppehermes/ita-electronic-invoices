from service.crypto_interface import CryptoService

XSD_URL = 'https://www.fatturapa.gov.it/export/documenti/fatturapa/v1.4/Schema_VFPR12_v1.2.3.xsd'
INVOICE_FILE_PATH = "data/invoice.xml.p7m"
OUTPUT_PATH = "output.pdf"

def get_schema():
    return requests.get(XSD_URL).content

converter = CryptoService()

data = converter.load_bytes(INVOICE_FILE_PATH)
xml = converter.extract_xml_from_p7m(data)
html = converter.convert_xml_to_html(xml)

# Export
converter.save_html_to_file(html)
converter.save_html_as_pdf(html)