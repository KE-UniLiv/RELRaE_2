from lxml.etree import QName
from xmlschema.validators import XsdAnyAttribute, XsdElement, XsdGroup
import xmlschema


def find_elem(schema):
    elem_name = "Database"

    for item in schema.elements[elem_name]:
        print(item)



# Load file
path = 'test_set/fullSchema/MINiML.xsd'
xsd = xmlschema.XMLSchema(path)
find_elem(xsd)
