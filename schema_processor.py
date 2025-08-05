# Handle the input schema and create objects
from lxml import etree as ET


class Schema:

    def __init__(self, path):
        self.path = path
        self.schema, self.root, self.ns = self.load_xml()

    def load_xml(self):
        schema = ET.parse(self.path)
        root = schema.getroot()
        ns = {'xs': "http://www.w3.org/2001/XMLSchema",
              'xsd': "http://www.w3.org/2001/XMLSchema"}
        return schema, root, ns

    def extract_concepts(self):
        pass

    def fragment_generation(self):
        pass

    def return_fragments(self):
        pass
