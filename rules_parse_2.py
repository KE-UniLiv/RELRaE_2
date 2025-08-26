# NOTE: This is a test file to test the parsing of XSD files into RDFS

# ------------- Import Libraries --------------
from pathlib import Path
from dataclasses import dataclass
from lxml import etree as ET
from typing import List, Dict, Any, Optional

import yaml
import os
import inquirer

from rdflib import Graph, Namespace
from rdflib.compare import isomorphic


# -------------- Definitions ---------------

# TODO: If needed, expand the Component class to cover elements
@dataclass
class Component:
    kind: str
    name: str
    qname: str
    props: Dict[str, Any]
    node: Any


NS = {'xs': "http://www.w3.org/2001/XMLSchema",
      'xsd': "http://www.w3.org/2001/XMLSchema"}


# =============== Parsing Functions ================


# --------------- Loading Functions -----------------


def load_rules():
    rulesets = [f for f in os.listdir(
        "rules/") if os.path.isfile(os.path.join("rules/", f))]

    question = [
        inquirer.List(
            'ruleset',
            message="What ruleset to use?",
            choices=rulesets
        ),
    ]

    selected_path = inquirer.prompt(question)['ruleset']

    rules = yaml.safe_load(Path(f"rules/{selected_path}").read_text())
    return rules


def load_components(xsd):
    components = []
    tree = ET.parse(xsd)
    root = tree.getroot()

    for concept in tree.iter():
        print(concept)
        # TODO: for each element, instantiate a component object

    return components


# --------------- Applying rules ---------------------


def generate_rdf(rule, component):
    # TODO: Match components to the appropriate rule
    #   -> Is this done top-down, bottom-up, or some other way to capture more complex      relationships
    pass


def apply_rules(ruleset, components):
    g_base = Graph()
    # TODO: Generate RDF for the component
    # TODO: Merge RDF into the base graph
    return g_base


# ------------- "Root" Function ----------------


def parse_schema(xsd) -> Graph:
    rules = load_rules()
    components = load_components(xsd)

    generated_graph = apply_rules(rules, components)
    return generated_graph


# ------------ Testing --------------


test_xsd = "test_set/"
responses = []
dir = next(os.walk(test_xsd))[1]
for x in dir:
    generated_fragment = parse_schema(f"test_set/{x}/xsd.xsd")
    expected_fragment = Graph()
    expected_fragment.parse(f"test_set/{x}/rdf.ttl", format='turtle')
    if isomorphic(generated_fragment, expected_fragment):
        response = "Correct"
    else:
        response = "Incorrect"
    response_row = [x, response]
    responses.append(response_row)
    generated_fragment.serialize(
        destination=f"test_set/{x}/generated_rdf.ttl",
        format='turtle'
    )
print(responses)
