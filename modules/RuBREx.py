import yaml
from rdflib import Graph
from utils import clean_namespace, parse_config
from xmlschema.validators import XsdAnyAttribute, XsdGroup, XsdElement


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
        attributes = []
        selector = rule["selector"][0]
        if "attribute" in selector.keys():
            if selector["attribute"] != "All":
                attributes.append(selector["attribute"])
            else:
                try:
                    for a in concept.attributes.values():
                        attributes.append(a)
                except Exception:
                    for a in concept.values():
                        attributes.append(a)
        if attributes is not None:
            print(f"Matched with rule {rule["name"]}")
        for a in attributes:
            if isinstance(a, str):
                if getattr(concept, a, None):
                    self.generate_fragment(concept, {"attribute": a})
            else:
                if isinstance(a, XsdAnyAttribute):
                    continue
                self.generate_fragment(concept, {"attribute": a})

    def fetch_children(self, concept, selector):
        children = []
        c_type = selector["child_type"]
        t = concept.type
        if t.is_complex() and not t.has_simple_content() and t.content is not None:
            descendents = list(t.content.iter_elements())
        else:
            descendents = []
        for d in descendents:
            if type(d.type).__name__ == c_type:
                children.append(d)
        return children

    def has_child(self, concept, rule):
        children = []
        selector = rule["selector"][0]
        if "child_type" in selector.keys():
            children = self.fetch_children(concept, selector)

        if children is not None:
            print(f"Matched with rule {rule["name"]}")
        for c in children:
            self.generate_fragment(concept, {"child": c})

    def has_choice(self, concept, rule):
        def walk(component, choice_seen):
            if isinstance(component, XsdElement):
                return choice_seen
            if isinstance(component, XsdGroup):
                choice_seen = choice_seen or (component.model == 'choice')
                for item in component:
                    if walk(item, choice_seen):
                        return True
            return False

        child_choice = []
        selector = rule["selector"][0]
        group = concept.type.model_group or concept.type.content
        if not isinstance(group, XsdGroup):
            return
        if not walk(group, False):
            return
        else:
            pot_children = self.fetch_children(concept, selector)

        for c in pot_children:
            parent = c.parent
            if isinstance(parent, XsdGroup) and parent.model == 'choice':
                child_choice.append(c)

        if child_choice is not None and child_choice != []:
            print(f"Matched with rule {rule["name"]}")
        for c in child_choice:
            self.generate_fragment(concept, {"child": c})

    def process_concept(self, concept, concept_type):
        for rule in self.rules:
            if concept_type == rule["element_type"]:
                if "selector" in rule:
                    getattr(self, rule["selector"][0]
                            ["pattern"])(concept, rule)
                else:
                    print(f"Matched with rule {rule["name"]}")

    def generate_fragment(self, concept, parts):
        print(f"{clean_namespace(concept.name)} is linked to {
              parts}")

    def match_concepts(self):
        # NOTE: Only XML 1.0 supported currently

        for concept in self.schema.iter_components():
            concept_type = type(concept).__name__

            if concept_type == "XsdElement":
                clean_type = type(concept.type).__name__
                print(concept_type)
                print("--> " + type(concept.type).__name__)
                print("--> " + clean_namespace(concept.name))
                self.process_concept(concept, clean_type)

            if concept_type == "XsdAttribute":
                print(concept_type)
                print("--> " + clean_namespace(concept.name))
                self.process_concept(concept, concept_type)

            if concept_type == "XsdAttributeGroup" and concept.name is not None:
                print(concept_type)
                print("--> " + clean_namespace(concept.name))
                self.process_concept(concept, concept_type)
