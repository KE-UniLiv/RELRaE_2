# NOTE: This is a test file to test the parsing of XSD files into RDFS

# ------------- Import Libraries --------------
from pathlib import Path
from dataclasses import dataclass
from lxml import etree as ET
from typing import List, Dict, Any, Optional
from jinja2 import Environment, BaseLoader

import xmlschema

import yaml
import os
import inquirer
import math

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
    # NOTE: I don't think value is a required field
    # NOTE: Maybe **kwargs can be used to create n arrays for all children at each possible depth?


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


# --------------- Applying rules ---------------------

# --- tiny helpers the templates can call ---
def is_nan_num(x):
    try:
        return math.isnan(x)
    except:
        return True


def xsd_range(qname):
    # qname like xs:string -> return 'xsd:string'
    local = qname.split(':', 1)[1] if ':' in qname else qname
    return f"xsd:{local}"


def qname_to_iri(qname, nsmap):
    if ':' not in qname:
        return qname
    pfx, local = qname.split(':', 1)
    base = nsmap.get(pfx)
    return f"<{base}{local}>" if base else qname


def safe_range(owner, elem, value):
    # If type is missing, fall back to an owner-local IRI
    return value if value else f"ex:{owner}_{elem}_Type"


def build_env(prefixes, nsmap):
    env = Environment(loader=BaseLoader, trim_blocks=True, lstrip_blocks=True)
    env.filters['safe_range'] = lambda iri, owner, elem: safe_range(
        owner, elem, iri)
    # Make helpers visible in templates
    env.globals.update({
        'isnan': math.isnan,
        'is_nan_num': is_nan_num,
        'xsd_range': xsd_range,
        'qname_to_iri': lambda q: qname_to_iri(q, nsmap)
    })
    # Prefix preamble for TTL
    ttl_prefixes = "\n".join(
        f"@prefix {p}: <{iri}> ." for p, iri in prefixes.items()) + "\n"
    return env, ttl_prefixes

# --- core engine ---


def apply_rules(xsd_xml: str, rules_yaml: str) -> str:
    doc = ET.fromstring(xsd_xml.encode('utf-8'))
    rules = yaml.safe_load(rules_yaml)
    prefixes = rules.get('prefixes', {})
    nsmap = {'xs': 'http://www.w3.org/2001/XMLSchema#', **{k: v for k,
                                                           v in prefixes.items() if v.endswith('#') or v.endswith('/')}}  # for XPath
    env, ttl_prefixes = build_env(prefixes, nsmap)
    out = [ttl_prefixes]

    for rule in rules.get('rules', []):
        sel = rule['selector']
        nodes = doc.xpath(sel, namespaces=nsmap)
        for n in nodes:
            # Evaluate 'when' (XPath boolean), default true
            ok = True
            if 'when' in rule and rule['when']:
                ok = bool(n.xpath(rule['when'], namespaces=nsmap))
            if not ok:
                continue

            # Bind variables
            bindings = {}
            for k, xp in (rule.get('vars') or {}).items():
                val = n.xpath(xp, namespaces=nsmap)
                # coerce simple XPath result types
                if isinstance(val, list):
                    val = val[0] if val else ''
                if isinstance(val, (etree._ElementUnicodeResult, etree._ElementStringResult)):
                    val = str(val)
                bindings[k] = val

            template = env.from_string(rule['emit'])
            out.append(template.render(**bindings))

    return "\n".join(out)

# ----------------------------------------------------


def prefix_to_preamble(prefixes):
    prefix_str = """"""
    for prefix, namespace in prefixes.items():
        current_str = f"@prefix {prefix}: <{namespace}> .\n"
        prefix_str += current_str
    return prefix_str


# NOTE: This Function may be redundant
def generate_rdf(rule, component):
    # TODO: Match components to the appropriate rule
    #   -> Is this done top-down, bottom-up, or some other way to capture more complex relationships
    pass


def gen_graph(ruleset, schema):
    graph_str = apply_rules(schema, ruleset)
    g_base = Graph()
    # TODO: Implement rules parsing
    return g_base


# ------------- "Root" Function ----------------


def parse_schema(xsd) -> Graph:
    rules = load_rules()
    schema = xmlschema.XMLSchema(xsd)
    # print(schema.elements)

    generated_graph = gen_graph(rules, xsd)

    return generated_graph


# ------------ Testing --------------

dir = "test_set/fullSchema/"
test_graph = parse_schema(dir + "animl-core.xsd")
test_graph.serialize(destination=f"{dir}graph.ttl", format="turtle")


# test_xsd = "test_set/"
# responses = []
# dir = next(os.walk(test_xsd))[1]
# for x in dir:
#     generated_fragment = parse_schema(f"test_set/{x}/xsd.xsd")
#     expected_fragment = Graph()
#     expected_fragment.parse(f"test_set/{x}/rdf.ttl", format='turtle')
#     if isomorphic(generated_fragment, expected_fragment):
#         response = "Correct"
#     else:
#         response = "Incorrect"
#     response_row = [x, response]
#     responses.append(response_row)
#     generated_fragment.serialize(
#         destination=f"test_set/{x}/generated_rdf.ttl",
#         format='turtle'
#     )
# print(responses)
