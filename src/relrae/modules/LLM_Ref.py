import json
import os
import re
import configparser
from utils import get_now
from pathlib import Path
from urllib import request
from urllib.error import URLError
from typing import Literal
from pydantic import BaseModel, Field, config
from ..utils import namespace_to_prefix
from random import randint
import numpy as np
from rdflib.namespace import RDFS
from rdflib import URIRef
import rdflib

class LLMRefinement:

    def __init__(self, schema, onto, prefix, namespace,
                 components_root="relrae_components"):
        self.log = []
        cfg = configparser.ConfigParser()
        cfg.read(Path(components_root) / "config" / "LLM_ref_conf.txt")
        self.config = cfg["MAIN"]
        self.errors = []
        self.schema = schema
        self.onto = onto
        self.prefix = prefix
        self.namespace = namespace
        self.set_models()

    # NOTE: This might not be neccessary
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
        prefixed_relation = namespace_to_prefix(
            relation, self.namespace, self.prefix)
        rel_info = {prefixed_relation: []}
        for r in qres:
            rel_info[prefixed_relation].append([
                namespace_to_prefix(r.predicate, self.namespace, self.prefix),
                namespace_to_prefix(r.object, self.namespace, self.prefix)
            ])
        self.log.append(f"Retrieved info for relation {str(relation)}")
        # print(rel_info)
        return rel_info

    def normalise_relation_label(self, label):
        label = namespace_to_prefix(label, self.namespace, self.prefix).strip()
        prefix_marker = f"{self.prefix}:"

        if ":" in label:
            prefix, label = label.split(":", 1)
            if prefix != self.prefix:
                prefix = self.prefix
        else:
            prefix = self.prefix

        words = re.findall(r"[A-Za-z0-9]+", label)
        if not words:
            raise ValueError(f"Cannot normalise empty relation label: {label}")

        camel_label = words[0].lower()
        for word in words[1:]:
            camel_label += word[:1].upper() + word[1:].lower()

        return f"{prefix_marker}{camel_label}"

    def get_examples(self, model_role, strat):
        if model_role == "eval":
            examples = self.config["eval_examples"]
        else:
            examples = self.config["ref_examples"]

        # print(examples)
        shots = {"zero": None,
                 "one": 0,
                 "few": 4}

        if strat == "zero":
            return []

        examples_list = examples[0:shots[strat]]
        return examples_list

    def average_eval(self, responses):
        evals = []
        confs = []
        for r in responses:
            if r["evaluation"] == "Yes":
                evals.append(1)
            else:
                evals.append(0)
            confs.append(r["confidence"])
        mean_evals = round((sum(evals)/len(evals)), 0)
        if int(mean_evals) == 1:
            eval = "Yes"
        else:
            eval = "No"
        avg_eval = {
            "evaluation": eval,
            "confidence": round(sum(confs)/len(confs), 3),
            "variance": round(float(np.var(evals)), 3)
        }
        return avg_eval

    def evaluation_loop(self, relation, evaluator, refiner, info):
        accepted = False
        rejected_labels = []
        loops = 0
        active_label = relation

        while not accepted and loops < int(self.config["refinement_loops"]):
            loops += 1
            eval_model = evaluator[0]
            eval_prompt = eval_model.build_eval_prompt(
                namespace_to_prefix(active_label, self.namespace, self.prefix),
                self.config["domain"],
                self.config["source"],
                info,
                rejected_labels,
                self.config["eval_messages"],
                evaluator[1])
            # print(eval_prompt)
            full_eval = eval_model.run_prompt(eval_prompt)
            if full_eval[0] == "Error":
                self.log.append("Error: LLM could not generate valid response")
            else:
                avg_eval = self.average_eval(full_eval[0])
                print(active_label)
                print("\n=======================\n")
                print(avg_eval)
                print("\n=======================\n")
                print(full_eval[1])

                self.log.append(full_eval[1])
                if avg_eval["evaluation"] == "Yes":
                    self.log.append("Label accepted")
                    break

                self.log.append("Label rejected")
            rejected_labels.append(namespace_to_prefix(
                active_label, self.namespace, self.prefix))
            print("\n ==== Rejected -> Refining ==== \n")
            ref_model = refiner[0]
            ref_prompt = ref_model.build_ref_prompt(
                namespace_to_prefix(active_label, self.namespace, self.prefix),
                self.config["domain"],
                self.config["source"],
                info,
                rejected_labels,
                self.config["ref_messages"],
                refiner[1])
            full_ref = ref_model.run_prompt(ref_prompt)
            ref = full_ref[0][0]
            print(ref)
            print(rejected_labels)
            print("\n=======================\n")
            print(full_ref[1])
            print("\n=======================\n")
            self.log.append(full_ref[1])
            active_label = self.normalise_relation_label(
                ref["relationship_label"])

        if accepted:
            self.replace_relation(relation, active_label)
            return ["refined", rejected_labels]
        else:
            return ["unrefined", rejected_labels]

    def evaluate_relations(self):
        relations = self.get_relations()

        eval_m = LLM(self.config["eval_llm"],
                     EvaluatorResponse,
                     self.config["eval_repeats"],
                     self.namespace,
                     self.prefix)
        eval_ex = self.get_examples("eval", self.config["eval_prompt_strat"])

        ref_m = LLM(self.config["ref_llm"],
                    RefinerResponse,
                    self.config["ref_repeats"],
                    self.namespace,
                    self.prefix)
        ref_ex = self.get_examples("ref", self.config["ref_prompt_strat"])

        for rel in relations:
            rel_info = self.get_relation_info(rel)
            response = self.evaluation_loop(rel, [eval_m, eval_ex], [
                                            ref_m, ref_ex], rel_info)
            if response[0] == "unrefined":
                self.errors.append([rel, rel_info, response[1]])

    def replace_relation(self, original, new):
        query = f"""
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>

        SELECT ?s ?p ?o WHERE{{
            ?s ?p ?o
            FITLER(
                ?s = <{self.namespace}{original}> ||
                ?p = <{self.namespace}{original}> ||
                ?o = <{self.namespace}{original}>
            )
        }}
        """
        qres = self.onto.query(query)

        for r in qres:

            if r.p == str(RDFS.label):
                n_sub = URIRef(f"{self.namespace}{new}")
                n_obj = rdflib.Literal(new)
                self.onto.remove((r.s, r.p, r.o))
                self.onto.add((n_sub, r.p, n_obj))
            elif r.s == f"{self.namespace}{original}":
                n_sub = URIRef(f"{self.namespace}{new}")
                self.onto.remove((r.s, r.p, r.o))
                self.onto.add((n_sub, r.p, r.o))
            elif r.p == f"{self.namespace}{original}":
                n_pred = URIRef(f"{self.namespace}{new}")
                self.onto.remove((r.s, r.p, r.o))
                self.onto.add((r.s, n_pred, r.o))
            elif r.o == f"{self.namespace}{original}":
                n_obj = URIRef(f"{self.namespace}{new}")
                self.onto.remove((r.s, r.p, r.o))
                self.onto.add((r.s, r.p, n_obj))

        s = URIRef(f"{self.namespace}{new}")
        p = URIRef(f"{self.namespace}editedBy")
        o = URIRef(f"{self.config["eval_llm"]} @ {get_now()}")
        self.onto.add([s, p, o])
        self.log.append(f"Relationship {original} updated to {new}.")

class EvaluatorResponse(BaseModel):
    evaluation: Literal["Yes", "No"]
    justification: str
    confidence: float = Field(ge=0.00, le=100.00)


class RefinerResponse(BaseModel):
    relationship_label: str
    justification: str


class LLM:

    def __init__(self, settings, format, repeats, ns, pr):
        self.repeats = repeats
        self.model = settings[0]
        self.api_key = settings[1]
        self.params = settings[2]
        self.provider = self.get_provider(settings)
        self.r_format = format
        self.onto_ns = ns
        self.onto_pr = pr

    def gen_seeds(self, n):
        seeds = []
        for i in range(int(n)):
            seeds.append(randint(1, 9999))
        return seeds

    def get_provider(self, settings):
        if len(settings) > 3:
            return str(settings[3]).lower()
        if isinstance(self.params, dict) and self.params.get("provider"):
            return str(self.params["provider"]).lower()
        if str(self.api_key).lower() in ("", "none", "ollama"):
            return "ollama"
        if str(self.model).lower().startswith(("gpt", "o1", "o3", "o4")):
            return "openai"
        if str(self.model).lower().startswith(("gemini", "models/gemini")):
            return "google"
        return "ollama"

    def build_messages(self, prompt, examples, active):
        message_list = [{"role": "system", "content": prompt}]
        for example in examples:
            for e in example:
                message_list.append(e)
        message_list.append(active)
        return message_list

    def process_context(self, context):
        context_list = []
        reject_relations = [
            "http://www.w3.org/2000/01/rdf-schema#label",
            f"{self.onto_pr}:generatedBy",
            f"{self.onto_pr}:hasXSDSource"
        ]
        for l in context.keys():
            for r in context[l]:
                if r[0] in reject_relations:
                    continue
                triple = [l, r[0], r[1]]
                context_list.append(triple)
        print(context_list)
        return context_list

    def build_eval_prompt(self, relation, domain, source, info, rejected_label, prompt, examples):
        active = {"role": "user", "content": f"relation: {relation}, context: {
            self.process_context(info)}, domain: {domain}, source: {source}, rejected labels: {rejected_label}"}

        messages = self.build_messages(prompt[0], examples, active)
        return messages

    def build_ref_prompt(self, relation, domain, source, info, rejected_label, prompt, examples):
        active = {"role": "user", "content": f"relation: {relation}, context: {
            self.process_context(info)}, domain: {domain}, source: {source}, rejected_labels: {rejected_label}"}

        messages = self.build_messages(prompt[0], examples, active)
        return messages

    def run_prompt(self, messages):
        results = []
        logs = []
        seeds = []
        seed = 0

        while seed < int(self.repeats):
            retrys = 10
            valid = False
            while not valid and retrys > 0:
                c_seed = randint(1, 9999)
                try:
                    raw_response = self.call_provider(messages, c_seed)
                    parsed_response = self.parse_response(raw_response)
                    results.append(parsed_response)
                    logs.append({
                        "provider": self.provider,
                        "model": self.model,
                        "seed": c_seed,
                        "response": parsed_response,
                    })
                    valid = True
                    seeds.append(c_seed)
                    seed += 1
                    retrys -= 1
                except Exception as exc:
                    logs.append({
                        "provider": self.provider,
                        "model": self.model,
                        "seed": c_seed,
                        "error": str(exc),
                    })
                    retrys -= 1

        if not results:
            results = "Error"

        return [results, logs]

    def call_provider(self, messages, seed):
        if self.provider == "ollama":
            return self.call_ollama(messages, seed)
        if self.provider == "openai":
            return self.call_openai(messages, seed)
        if self.provider in ("google", "googleai", "gemini"):
            return self.call_google(messages, seed)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def get_params(self, seed, provider=None):
        params = {}
        if isinstance(self.params, dict):
            params.update(self.params)
        params.pop("provider", None)
        params["seed"] = seed
        if provider == "openai":
            supported = {
                "temperature",
                "top_p",
                "max_tokens",
                "max_completion_tokens",
                "presence_penalty",
                "frequency_penalty",
                "seed",
                "stop",
            }
            params = {
                key: value for key, value in params.items()
                if key in supported
            }
        return params

    def get_api_key(self, env_var):
        if str(self.api_key).lower() not in ("", "none"):
            return self.api_key
        return os.environ.get(env_var)

    def parse_response(self, raw_response):
        if isinstance(raw_response, self.r_format):
            return raw_response.model_dump()
        if isinstance(raw_response, dict):
            return self.r_format.model_validate(raw_response).model_dump()
        return self.r_format.model_validate_json(raw_response).model_dump()

    def messages_to_text(self, messages):
        prompt_parts = []
        for message in messages:
            prompt_parts.append(f"{message['role']}: {message['content']}")
        return "\n\n".join(prompt_parts)

    def call_ollama(self, messages, seed):
        params = self.get_params(seed, "ollama")
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": self.r_format.model_json_schema(),
            "options": params,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            "http://localhost:11434/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama at localhost:11434") from exc

        return body["message"]["content"]

    def call_openai(self, messages, seed):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "Install the openai package to use OpenAI models") from exc

        api_key = self.get_api_key("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key missing")

        params = self.get_params(seed, "openai")
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=self.r_format,
            **params,
        )
        return completion.choices[0].message.parsed

    def call_google(self, messages, seed):
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "Install the google-genai package to use Google AI models"
            ) from exc

        api_key = self.get_api_key("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google AI API key missing")

        params = self.get_params(seed, "google")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=self.messages_to_text(messages),
            config={
                **params,
                "response_format": {
                    "text": {
                        "mime_type": "application/json",
                        "schema": self.r_format.model_json_schema(),
                    }
                },
            },
        )
        return response.text
