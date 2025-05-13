from cryptography.hazmat.primitives.serialization import pkcs7, load_der_private_key

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