class CryptoInterface:
    def load_data_source(self, path: str) -> str:
        """ Load in the file for extracting data"""
        pass

    def extract_xml_from_p7m(self, data: bytes) -> str:
        """Extract XML data from P7M bytes"""
        pass