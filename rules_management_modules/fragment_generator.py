# NOTE: Input: XSD concept, selected rule
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from rules_management_modules import rules_engine
from lxml.etree import QName
from xmlschema.validators import XsdAtomicBuiltin, XsdAtomicRestriction

# TODO: Implement Constants Properly
PREFIX = 'ani'

PROV_BLOCK = "."

PREAMBLE = """
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix ani: <http://example.org/Anitology/> .
    """


def capitalise_first_char(label):
    first_char = label[0]
    back_label = label[1:]
    processed_label = first_char.upper() + back_label
    return processed_label


def lower_first_char(label):
    first_char = label[0]
    back_label = label[1:]
    if back_label[0] != back_label[0].upper():
        processed_label = first_char.lower() + back_label
    else:
        processed_label = label
    return processed_label


def get_named_base_type(concept_type):
    t = concept_type
    while getattr(t, 'base_type', None) is not None:
        b = t.base_type
        if getattr(b, 'name', None):
            return b
        t = b
    return None


def get_elem_name(concept):
    if concept.name:
        xml_concept = QName(concept.name).localname
    else:
        xml_concept = QName(get_named_base_type(concept).name).localname
    return capitalise_first_char(xml_concept)


def is_built_in(concept):
    # print(concept.base_type)
    if isinstance(concept.base_type, XsdAtomicBuiltin):
        return get_elem_name(concept.base_type)
    elif isinstance(concept, XsdAtomicBuiltin):
        return get_elem_name(concept)
    else:
        return is_built_in(concept.base_type)


def check_datatype(concept):
    rdfs_string = f"""xsd:{lower_first_char(is_built_in(concept.type))}"""
    return rdfs_string


def generate_preamble():
    preamble = PREAMBLE
    more_namespaces = True
    # Define name space
    while more_namespaces:
        namespace = input('Enter a namespace URL (Leave blank to skip): ')
        if namespace == '':
            more_namespaces = False
            continue
        prefix = input('Enter a prefix for this namespace: ')
        pref_line = f"""
            @prefix {prefix}: <{namespace}> .
        """
        preamble = PREAMBLE + pref_line

    return preamble


def fragment_generator(element, rule, concept, preamble) -> Graph:

    g = Graph()

    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('owl', OWL)

    # TODO: Collect all required info to populate emit
    prov_block = "."
    fragment = eval(rule['emit'])
    print(preamble + fragment)
    g.parse(data=(preamble + fragment), format='ttl')
    # print(fragment)

    return g

# NOTE: Output: RFDS fragment
