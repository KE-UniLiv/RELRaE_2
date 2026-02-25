from lxml.etree import QName
from xmlschema.validators import XsdAnyAttribute, XsdElement, XsdGroup
import xmlschema


def find_elem(schema):
    elem_name = "Database"

    # for item in schema.elements[elem_name]:
    #    print(item)
    return schema.elements.get(elem_name)


def elements(xsd_element):
    t = xsd_element.type
    if not t.is_complex() or t.content is None:
        return []
    return list(t.content.iter_elements())


def has_child(element):
    candidates = []

    # c_type = pattern[selector_index(pattern, 'child_type')][1]
    # r_depth = pattern[selector_index(pattern, 'relative_depth')][1]
    c_type = 'XsdComplexType'

    descendents = elements(element)
    print(descendents)
    for d in descendents:
        if type(d.type).__name__ == c_type:
            candidates.append(d)
            print(d)

    return candidates


# Load file
path = 'test_set/fullSchema/MINiML.xsd'
xsd = xmlschema.XMLSchema(path)
elem = find_elem(xsd)
has_child(elem)
