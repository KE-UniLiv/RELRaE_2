from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import xmlschema
import os


from modules.RuBREx import RuBREx
from modules.LLM_Ref import LLM_Refinement
from modules.human_fix import human_fix
from utils import get_now


class RELRaE:

    def __init__(self, onto_name, schema, namespace, prefix, config):
        self.schema = xmlschema.XMLSchema(open(f"schema/{schema}"))
        self.namespace = Namespace(namespace)
        self.prefix = prefix
        self.onto_name = onto_name
        self.onto = Graph()
        self.errors = []
        self.configs = [{"Pipeline": config}]
        self.logs = {}

        self.onto.bind('rdf', RDF)
        self.onto.bind('rdfs', RDFS)
        self.onto.bind('owl', OWL)
        self.onto.bind(self.prefix, self.namespace)

    def RuBREx(self):
        m_rubrex = RuBREx(self.schema, self.onto, self.prefix, self.namespace)
        m_rubrex.match_concepts()

        self.configs.append({"RuBREx": m_rubrex.config})
        self.logs["RuBREx"] = m_rubrex.log
        # NOTE: Consider the module complete
        self.onto = self.onto + m_rubrex.onto
        self.errors.append(m_rubrex.errors)

    def LLM_Refinement_Loop(self):
        # TODO:
        LLM_Refinement()

    def human_fix(self):
        # TODO:
        human_fix()

    def write_logs(self, path):
        for key, values in self.logs.items():
            with open(f"{path}{key}.txt", "w", encoding="utf-8") as f:
                for line in values:
                    f.write(line + "\n")

    def write_metadata(self, path):
        with open(f"{path}metadata.txt", "w", encoding="utf-8") as f:
            for config in self.configs:
                for section, values in config.items():
                    f.write(f"{section}\n\n")
                    for key, value in values.items():
                        f.write(f"{key}: {value}\n")
                f.write("\n\n")

    def serialise(self):
        main_path = f"output/{self.onto_name}{get_now()}/"
        log_path = main_path + "/logs/"
        os.makedirs(log_path)
        self.write_logs(log_path)
        self.write_metadata(main_path)
        self.onto.serialize(destination=f"{main_path}{
                            self.onto_name}.ttl", format="ttl")
