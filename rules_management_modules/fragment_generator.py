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


def get_elem_name(concept):
    xml_concept = QName(concept.name).localname
    return xml_concept


def check_datatype(concept):
    print(concept.type.base_type)
    if isinstance(concept.type.base_type, XsdAtomicBuiltin):
        rdfs_string = f"xsd:{get_elem_name(concept.type.base_type)}"
        return rdfs_string
    elif isinstance(concept.type.base_type, XsdAtomicRestriction):
        # TODO: Add an option to deal with undefined (or nested custom) datatypes (e.g. SVG and EmbeddedXMLType)
        rdfs_string = f"""{PREFIX}:{get_elem_name(concept.type.base_type)} ;
            {PROV_BLOCK}

            {PREFIX}:{get_elem_name(concept.type.base_type)} a rdfs:Datatype ;
                rdfs:label '{get_elem_name(concept.type.base_type)}'@en ;
                rdfs:subClassOf xsd:{get_elem_name(concept.type.base_type.base_type)}"""
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
