# NOTE: Input: XSD element object, ruleset
from rdflib import Graph

from rules_management_modules import rules_engine
from rules_management_modules import fragment_generator


def rules_parser(element, ruleset) -> Graph:
    g = Graph()
    for rule in ruleset:
        rule_match, concepts = rules_engine.rules_engine(
            element, rule)
        if rule_match:
            print(f"Successfully matched with: {rule['name']}")
            print("=================================================")
            for c in concepts:
                g_frag = fragment_generator.fragment_generator(
                    element, rule, c)
                g = g + g_frag
    return g

# NOTE: Output: RDFS fragment
