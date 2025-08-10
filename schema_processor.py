# Handle the input schema and create objects
from lxml import etree as ET


# Define element classes

class AttributeGroup():

    def __init__(self, name, attributes, **kwargs):
        self.name = name
        self.attributes = attributes

        for k, v in kwargs.items():
            setattr(self, k, v)


class ComplexTypeElement():

    def __init__(self, name, description, children, attributes, definition, **kwargs):
        self.name = name
        self.description = description
        self.children = children
        self.attributes = attributes
        self.definition = definition

        for k, v in kwargs.items():
            setattr(self, k, v)


class SimpleTypeElement():

    def __init__(self, name, description, restriction, **kwargs):
        self.name = name
        self.description = description
        self.restriction = restriction

        for k, v in kwargs.items():
            setattr(self, k, v)


class Attribute():

    def __init__(self, name, description, type_, use, **kwargs):
        self.name = name
        self.description = description
        self.type_ = type_
        self.use = use

        for k, v in kwargs.items():
            setattr(self, k, v)


class ExternallyDefinedElement():

    def __init__(self, name, description, type_, **kwargs):
        self.name = name
        self.description = description
        self.type_ = type_

        for k, v in kwargs.items():
            setattr(self, k, v)


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
