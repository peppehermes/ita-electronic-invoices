from asn1crypto import cms
import CryptoInterface

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
    