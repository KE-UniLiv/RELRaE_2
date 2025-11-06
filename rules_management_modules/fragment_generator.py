# NOTE: Input: XSD concept, selected rule
from rdflib import Graph
from rules_management_modules import rules_engine


def fragment_generator(element, rule) -> Graph:
    g = Graph()

    selector = rules_engine.selector_translation(rule)
    # TODO: Collect all required info to populate emit

    return g

# NOTE: Output: RFDS fragment
