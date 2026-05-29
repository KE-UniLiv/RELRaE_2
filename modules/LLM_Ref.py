from typing import Literal
from pydantic import BaseModel, Field
from utils import parse_config
from random import randint


CONFIG = "config/LLM_ref_conf.txt"


class LLMRefinement:

    def __init__(self, schema, onto, prefix, namespace):
        self.log = []
        self.config = parse_config(CONFIG)
        print(self.config)
        self.errors = []
        self.schema = schema
        self.onto = onto
        self.prefix = prefix
        self.namespace = namespace
        self.set_models()

    def set_models(self):
        pass

    def get_relations(self):
        query = """
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>

        SELECT ?property ?propertyType
        WHERE {
            VALUES ?propertyType {
                rdf:Property
                owl:ObjectProperty
                owl:DatatypeProperty
                owl:AnnotationProperty
            }

            ?property rdf:type ?propertyType .
        }
        """
        qres = self.onto.query(query)
        property_list = []
        for r in qres:
            property_list.append(r.property)
        self.log.append(f"Retrieved {len(property_list)} properties")
        return property_list

    def get_relation_info(self, relation):
        query = f"""
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>

        SELECT ?subject ?predicate ?object
        WHERE {{
            {{
                BIND(<{relation}> AS ?subject)
                ?subject ?predicate ?object .
            }}
            UNION
            {{
                ?subject ?predicate <{relation}> .
                BIND(<{relation}> AS ?object)
            }}
        }}
        """
        qres = self.onto.query(query)
        rel_info = {str(relation): []}
        for r in qres:
            rel_info[str(relation)].append({str(r.predicate): str(r.object)})
        self.log.append(f"Retrieved info for relation {str(relation)}")
        return rel_info

    def get_examples(self, model_role, strat):
        if model_role == "eval":
            examples = EVAL_EXAMPLES
        else:
            examples = REF_EXAMPLES

        shots = {"zero": None,
                 "one": 0,
                 "few": 4}

        if strat == "zero":
            return

        examples_list = examples[0:shots[strat]]
        return examples_list

    def evaluate_relations(self):
        relations = self.get_relations()

        eval_m = LLM(self.config["eval_llm"],
                     EvaluatorResponse,
                     self.config["eval_repeats"])
        eval_ex = self.get_examples("eval", self.config["eval_prompt_strat"])

        ref_m = LLM(self.config["ref_llm"],
                    RefinerResponse,
                    self.config["ref_repeats"])
        ref_ex = self.get_examples("ref", self.config["ref_prompt_strat"])

        for rel in relations:
            rel_info = self.get_relation_info(rel)


class EvaluatorResponse(BaseModel):
    evaluation: Literal["Yes", "No"]
    justification: str
    confidence: float = Field(ge=0.00, le=100.00)


class RefinerResponse(BaseModel):
    relationship_label: str
    justification: str


class LLM:

    def __init__(self, settings, format, repeats):
        self.gen_seeds(repeats)
        self.model = settings[0]
        self.api_key = settings[1]
        self.params = settings[2]
        self.r_format = format

    def gen_seeds(self, n):
        self.seeds = []
        for i in range(n-1):
            self.seeds.append(randint(1, 9999))


EVAL_EXAMPLES = []

REF_EXAMPLES = []
