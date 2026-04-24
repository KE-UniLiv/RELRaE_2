import yaml
from lxml.etree import QName
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL
from utils import clean_namespace, parse_config, generate_provenance, lower_first_char, capitalise_first_char, generate_preamble, normalise_string, get_now
from xmlschema.validators import XsdAnyAttribute, XsdGroup, XsdElement, XsdAtomicBuiltin

CONFIG = "config/RuBREx_conf.txt"


class RuBREx:

    def __init__(self, schema, onto, prefix, namespace):
        self.log = []
        self.load_rules()
        self.config = parse_config(CONFIG)
        self.errors = []
        self.schema = schema
        self.onto = onto
        self.prefix = prefix
        self.namespace = namespace

    def load_rules(self):
        self.rules = None
        rulset_path = f"rules/{parse_config(CONFIG)["ruleset"]}"
        with open(rulset_path) as file:
            try:
                self.rules = yaml.safe_load(file).get("rules", [])
                self.log.append(f"{get_now()} Ruleset {
                                rulset_path} succesfully loaded")
            except Exception as exc:
                self.log.append(exc)
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
            self.log.append(f"{get_now()} Matched with rule {rule["name"]}")
        for a in attributes:
            if isinstance(a, str):
                if getattr(concept, a, None):
                    self.generate_fragment(
                        concept, {"attribute": a}, rule["emit"])
            else:
                if isinstance(a, XsdAnyAttribute):
                    continue
                self.generate_fragment(
                    concept, {"attribute": a}, rule["emit"])

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
            self.log.append(f"{get_now()} Matched with rule {rule["name"]}")
        for c in children:
            self.generate_fragment(concept, {"child": c}, rule["emit"])

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
            self.log.append(f"{get_now()} Matched with rule {rule["name"]}")
        for c in child_choice:
            self.generate_fragment(concept, {"child": c}, rule["emit"])

    def process_concept(self, concept, concept_type):
        for rule in self.rules:
            if concept_type == rule["element_type"]:
                if "selector" in rule:
                    getattr(self, rule["selector"][0]
                            ["pattern"])(concept, rule)
                else:
                    self.log.append(
                        f"{get_now()} Matched with rule {rule["name"]}")
                    self.generate_fragment(concept, {}, rule["emit"])

    def get_named_base_type(self, concept):
        t = concept
        while getattr(t, 'base_type', None) is not None:
            b = t.base_type
            if getattr(b, 'name', None):
                return b
            t = b
        return None

    def get_elem_name(self, concept):
        if concept.name:
            xml_concept = QName(concept.name).localname
        else:
            xml_concept = QName(
                self.get_named_base_type(concept).name).localname
        return capitalise_first_char(xml_concept)

    def is_built_in(self, concept):
        if isinstance(concept.base_type, XsdAtomicBuiltin):
            return self.get_elem_name(concept.base_type)
        elif isinstance(concept, XsdAtomicBuiltin):
            return self.get_elem_name(concept)
        else:
            return self.is_built_in(concept.base_type)

    def is_boolean(self, concept):
        datatype = self.is_built_in(concept.type)
        if datatype == "Boolean":
            return "is"
        else:
            return "has"

    def check_datatype(self, concept):
        rdfs_string = f"""xsd:{lower_first_char(
            self.is_built_in(concept.type))}"""
        return rdfs_string

    def generate_fragment(self, concept, parts, emit):
        self.log.append(f"{get_now()} {clean_namespace(concept.name)} is linked to {
            parts}")
        local_graph = Graph()

        prov_block = generate_provenance(
            self.prefix, "Rubrex", concept.local_name)

        graph_str = generate_preamble(self.prefix, self.namespace) + eval(emit)
        local_graph.parse(data=graph_str, format="ttl")
        self.onto = self.onto + local_graph

    def match_concepts(self):
        # NOTE: Only XML 1.0 supported currently

        for concept in self.schema.iter_components():
            concept_type = type(concept).__name__

            if concept_type == "XsdElement":
                clean_type = type(concept.type).__name__
                self.log.append(concept_type)
                self.log.append(get_now() + " --> " +
                                type(concept.type).__name__)
                self.log.append(get_now() + " --> " +
                                clean_namespace(concept.name))
                self.process_concept(concept, clean_type)

            if concept_type == "XsdAttribute":
                self.log.append(concept_type)
                self.log.append(get_now() + " --> " +
                                clean_namespace(concept.name))
                self.process_concept(concept, concept_type)

            if concept_type == "XsdAttributeGroup" and concept.name is not None:
                self.log.append(concept_type)
                self.log.append(get_now() + " --> " +
                                clean_namespace(concept.name))
                self.process_concept(concept, concept_type)
