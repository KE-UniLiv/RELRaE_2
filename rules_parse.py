# NOTE: This is a test file to test the parsing of XSD files into RDFS
# Import Libraries
from dataclasses import dataclass
from typing import List, Dict, Any
import xmlschema
from xmlschema.xpath import selectors
import yaml
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, BNode, Literal
from rdflib.compare import isomorphic

from pathlib import Path
import os


@dataclass
class Component:
    kind: str
    name: str
    qname: str
    props: Dict[str, Any]
    node: Any


ns = {'xs': "http://www.w3.org/2001/XMLSchema",
      'xsd': "http://www.w3.org/2001/XMLSchema"}


def load_schema_components(xsd):
    xs = xmlschema.XMLSchema(xsd)
    comps: List[Component] = []

    # Types
    for qn, t in xs.types.items():
        kind = "complexType" if t.is_complex() else "simpleType"
        name = t.local_name
        props = {
            "abstract": getattr(t, "abstract", False),
            "base_type_qname": getattr(t.base_type, "name", None) if hasattr(t, "base_type") and t.base_type else None,
            "has_enumeration": bool(getattr(t, "enumeration", []) or getattr(getattr(t, "facets", None), "enumeration", [])),
            "enumeration_values": [e.value for e in getattr(t, "enumeration", [])] if hasattr(t, "enumeration") else [],
            # TODO: add more complex schema information collection, to facilitate more complex rules
        }
        comps.append(Component(kind, name, str(qn), props, t))

    # Elements
    for qn, e in xs.elements.items():
        t = e.type
        kind = "element"
        name = e.local_name
        props = {
            "type_qname": str(t.name) if t.name else None,
            "type_kind": "complex" if t.is_complex() else "simple",
            "min_occurs": e.min_occurs,
            "max_occurs": e.max_occurs,
            # rough domain hint
            "container_type_name": getattr(e.parent, "name", None),
            # TODO: substitution group, nillable, identity constraints, etc.
        }
        comps.append(Component(kind, name, str(qn), props, t))

    # TODO: Add other XML features (attributes, attribute groups ect.)

    return comps


def match_components(component, selector):
    if selector.get("kind") and selector.get("kind") != component.kind:
        return False
    where = selector.get('where', {})
    for k, expected in where.items():
        val = component.props.get(k)
        if isinstance(expected, List):
            if val not in expected:
                return False
        elif isinstance(expected, bool):
            if bool(val) != expected:
                return False
        else:
            if val != expected:
                return False
    return True


def fill(template, component):
    values = {
        "name": component.name,
        **{k: (','.join(v) if isinstance(v, list) else v) for k, v in component.props.items()}
    }
    s = template
    for k, v in values.items():
        s = s.replace(f"{{{k}}}", str(v) if v is not None else "")
    return s


def apply_rules(components, rules):
    out = []
    for r in rules:
        selector = r['selector']
        for c in components:
            if match_components(c, selector):
                emit = r["emit"]
                if 'class' in emit:
                    out.append(f"{fill(emit['class'], c)} a owl:Class .")
                if 'restriction' in emit:
                    domain = fill(emit["restriction"]["domain"], c)
                    property = fill(emit["restriction"]["property"], c)
                    range_ = fill(emit["restriction"]["range"], c)
                    quant = emit["restriction"].get("quantifier", "some")
                    q = "someValuesFrom" if quant == "some" else "allValuesFrom"
                    out.append(f"{domain} rdfs:subClassOf [ a owl:Restriction ; owl:onProperty {
                               property} ; owl:{q} {range_} ] . ")
                if "oneOf" in emit:
                    class_ = fill(emit["oneOf"]["class"], c)
                    values = c.propts.get("enumeration_values", [])
                    items = " ".join(f"\"{v}\"" for v in values)
                    out.append(f"{class_} owl:oneOf ( {items} ) . ")
        return "\n".join(out)


def parse_rules(xsd) -> Graph:

    # ruleset = yaml.safe_load(Path("rules/ruleset_v1.yaml").read_text())
    g = Graph()

    components = load_schema_components(xsd)

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
