# NOTE: This is a test file to test the parsing of XSD files into RDFS

# Import Libraries
import rdflib
import jinja2
import yaml
from pathlib import Path
from lxml import etree as ET


# XSD to RDF translation
def parse_rules(xsd):
    ruleset = yaml.safe_load(Path("rules/ruleset_v1.yaml").read_txt())


# Load test set of XSD fragments and compare the generated RDF against an expected output
test_xsd = "test_set/"
responses = []
for x in test_xsd:
    generated_fragment = parse_rules(x + "xsd.xsd")
    expected_fragment = x + "rdf.ttl"
    if generated_fragment == expected_fragment:
        response = "Expected"
    else:
        response = "Incorrect"
    response_row = [x, response]
    responses.append(response_row)
