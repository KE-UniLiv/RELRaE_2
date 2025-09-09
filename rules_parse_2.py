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


@dataclass
class Component:
    node: Any
    kind: str
    qname: str
    name: str
    attributes: Dict[str, Any]
    depth: int
    # value: Any
    # NOTE: I don't think value is a required field


NS = {'xs': "http://www.w3.org/2001/XMLSchema",
      'xsd': "http://www.w3.org/2001/XMLSchema"}


# =============== Parsing Functions ================


def get_depth(element):
    return len(list(element.iterancestors()))


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
    tree = ET.parse(xsd, parser=ET.XMLParser(remove_comments=True))
    root = tree.getroot()

    for concept in tree.iter():
        if not concept.get("name"):
            continue

        attributes = dict(concept.attrib)
        attributes.pop("name", None)

        current_component = Component(
            node=concept,
            kind=concept.tag,
            qname=ET.QName(concept).localname,
            name=concept.get("name"),
            attributes=attributes,
            depth={get_depth(concept)}
        )

        print(f"Generated object for concept: {current_component.name}")
        components.append(current_component)

    return components


# --------------- Applying rules ---------------------


def condense_definitions(components):

    for comp in components:
        if "type" in comp.attributes:
            for c in components:
                if c.name == comp.attributes["type"]:
                    c.name = comp.name
                    components.pop(components.index(comp))

        # NOTE: I am not 100% sure this will work properly (Expect errors)
        else:
            children = list(comp.node)
            for c in children:
                if ET.QName(c).localname == "complexType":
                    comp.kind = c.tag
                    comp.qname = ET.QName(c).localname
    return components


# NOTE: This Function may be redundant
def generate_rdf(rule, component):
    # TODO: Match components to the appropriate rule
    #   -> Is this done top-down, bottom-up, or some other way to capture more complex      relationships
    pass


def apply_rules(ruleset, components):
    g_base = Graph()

    for prefix, namespace in ruleset["prefixes"].items():
        g_base.bind(prefix, Namespace(namespace))

    # TODO: Merge RDF into the base graph

    # NOTE: I think there will be a need to redesign the ruleset's matching component
    for comp in components:
        for rule in ruleset["rules"]:
            if comp.qname == rule["selector"]["qname"]:
                # Populate emit
                g = Graph()

                for prefix, namespace in ruleset["prefixes"].items():
                    g.bind(prefix, Namespace(namespace))

                # TODO: Fix parsing

                name = comp.name
                g.parse(eval(rule["emit"]))
                print(f"Matched with rule: {rule["name"]}")

                g_base += g

    return g_base


# ------------- "Root" Function ----------------


def parse_schema(xsd) -> Graph:
    rules = load_rules()
    components = load_components(xsd)
    components = condense_definitions(components)

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
