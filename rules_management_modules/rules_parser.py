# NOTE: Input: XSD element object, ruleset
from rdflib import Graph

from rules_management_modules import rules_engine
from rules_management_modules import fragment_generator


def rules_parser(element, ruleset) -> Graph:
    g = Graph()
    for rule in ruleset:
        rule_match = rules_engine.rules_engine(element, ruleset[rule])
        if rule_match:
            print(f"Successfully matched with: {rule['name']}")
            print("=================================================")
            g = fragment_generator.fragment_generator(element, rule)
    return g

# NOTE: Output: RDFS fragment
