import yaml
from rdflib import Graph
from utils import clean_namespace, parse_config


class RuBREx:

    def __init__(self, schema, onto):
        self.load_config()
        self.errors = []
        self.schema = schema
        self.onto = onto

    def load_config(self):
        CONFIG = "config/RuBREx_conf.txt"
        self.rules = None
        rulset_path = f"rules/{parse_config(CONFIG)["ruleset"]}"
        with open(rulset_path) as file:
            try:
                self.rules = yaml.safe_load(file).get("rules", [])
                print(f"Ruleset {rulset_path} succesfully loaded")
            except Exception as exc:
                print(exc)
        if self.rules is None:
            raise Exception

    def has_attribute(self, concept, rule):
        self.generate_fragment(concept)

    def has_child(self, concept, rule):
        self.generate_fragment(concept)

    def has_choice(self, concept, rule):
        self.generate_fragment(concept)

    def process_element(self, concept):
        concept_type = type(concept.type).__name__
        for rule in self.rules:
            if concept_type == rule["element_type"]:
                if "selector" in rule:
                    getattr(self, rule["selector"][0]
                            ["pattern"])(concept, rule)
                    print(f"Matched with rule {rule["name"]}")
                    self.generate_fragment(concept)
                else:
                    print(f"Matched with rule {rule["name"]}")
                    self.generate_fragment(concept)

    def process_attribute(self, concept):
        pass

    def process_attribute_group(self, concept):
        pass

    # FIX: Determine what arguments are required
    # Likely kwargs
    def generate_fragment(self, concept):
        pass

    def match_concepts(self):
        # NOTE: Only XML 1.0 supported currently

        for concept in self.schema.iter_components():
            concept_type = type(concept).__name__

            if concept_type == "XsdElement":
                print(concept_type)
                print("--> " + type(concept.type).__name__)
                print("--> " + clean_namespace(concept.name))
                self.process_element(concept)

            if concept_type == "XsdAttribute":
                print(concept_type)
                print("--> " + clean_namespace(concept.name))
                self.process_attribute(concept)

            if concept_type == "XsdAttributeGroup" and concept.name is not None:
                print(concept_type)
                print("--> " + clean_namespace(concept.name))
                self.process_attribute_group(concept)
