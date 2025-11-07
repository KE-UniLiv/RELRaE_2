from rules_management_modules import rules_parser
from rdflib import Graph
from pathlib import Path
import yaml
import xmlschema
import os
import inquirer
# NOTE: Input: XSD and YAML Ruleset

TESTING = True

#####################################################


def generate_graph(schema, rules) -> Graph:

    g = Graph()

    for concept in schema:
        g = g + rules_parser.rules_parser(concept, rules)

    return g


# NOTE: Output: Rules-Based Graph

#####################################################

# Testing Code

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


def test():
    schema_dir = 'test_set/fullSchema/animl-core.xsd'
    xsd = xmlschema.XMLSchema(schema_dir)
    rules = load_rules().get('rules', [])
    generate_graph(xsd, rules)


if TESTING:
    test()
