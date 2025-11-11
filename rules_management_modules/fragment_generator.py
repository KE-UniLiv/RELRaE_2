# NOTE: Input: XSD concept, selected rule
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from rules_management_modules import rules_engine
from lxml.etree import QName

# TODO: Implement Constants Properly
PREFIX = 'ani'
PROV_BLOCK = "To be defined"

PREAMBLE = """
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix ani: <http://example.org/Anitology/> .
    """


def get_elem_name(concept):
    xml_concept = QName(concept.name).localname
    return xml_concept


def fragment_generator(element, rule, concept) -> Graph:
    # ANI = Namespace("http://example.org/Anitology/")

    g = Graph()

    # g.bind('ani', ANI)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('owl', OWL)

    # TODO: Collect all required info to populate emit
    prov_block = "."
    fragment = eval(rule['emit'])
    print(PREAMBLE + fragment)
    g.parse(data=(PREAMBLE + fragment), format='ttl')
    # print(fragment)

    return g

# NOTE: Output: RFDS fragment
