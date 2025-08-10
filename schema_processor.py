# Handle the input schema and create objects
from lxml import etree as ET


# Define element classes
# TODO: Add cardinality support

class AttributeGroup():

    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes


class ComplexTypeElement():

    def __init__(self, name, description, children, attributes, definition):
        self.name = name
        self.description = description
        self.children = children
        self.attributes = attributes
        self.definition = definition


class SimpleTypeElement():

    def __init__(self, name, description, restriction):
        self.name = name
        self.description = description
        self.restriction = restriction


class Attribute():

    def __init__(self, name, description, type_, use):
        self.name = name
        self.description = description
        self.type_ = type_
        self.use = use


class ExternallyDefinedElement():

    def __init__(self, name, description, type_):
        self.name = name
        self.description = description
        self.type_ = type_


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
        self.schema_concepts = {}

    def fragment_generation(self):
        pass

    def return_fragments(self):
        pass
