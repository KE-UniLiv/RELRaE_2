# NOTE: This is a test file to test the parsing of XSD files into RDFS

# Import Libraries
import rdflib
from rdflib import Graph
from rdflib.compare import isomorphic

from jinja2 import Environment, BaseLoader
import yaml
from pathlib import Path
from lxml import etree as ET
import os


env = Environment(loader=BaseLoader, autoescape=False)


def turtle_string(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def evaluate_xpath(node, expression):
    if not expression:
        return None
    resource = node.xpath(expression, namespaces=ns)
    if isinstance(resource, list):
        return resource[0] if resource else ""
    return str(resource)


env.filters["turtle_string"] = turtle_string
ns = {'xs': "http://www.w3.org/2001/XMLSchema",
      'xsd': "http://www.w3.org/2001/XMLSchema"}


# XSD to RDF translation
def parse_rules(xsd) -> Graph:

    schema = ET.parse(xsd)
    ruleset = yaml.safe_load(Path("rules/ruleset_v1.yaml").read_text())
    g = Graph()
    for pfx, iri in ruleset.get("prefixes", {}).items():
        g.bind(pfx, rdflib.Namespace(iri))

    for rule in ruleset["rules"]:
        template = env.from_string(rule["emit"])
        matches = schema.xpath(rule["selector"], namespaces=ns)

        for m in matches:
            context = {}
            for k, expression in rule.get("vars", {}).items():
                context[k] = evaluate_xpath(m, expression)
            items = m.xpath(rule.get("for_each"), namespaces=ns) if rule.get(
                "for_each") else [None]
            for item in items:
                item_context = dict(context)
                if item is not None:
                    for k, expression in rule.get("vars_per_item", {}).items():
                        item_context[k] = evaluate_xpath(item, expression)
                turtle = template.render(**item_context)
                g.parse(data=turtle, format=turtle)

    return g


# Load test set of XSD fragments and compare the generated RDF against an expected output
test_xsd = "test_set/"
responses = []
dir = next(os.walk(test_xsd))[1]
for x in dir:
    generated_fragment = parse_rules(f"test_set/{x}/xsd.xsd")
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
print(response_row)
