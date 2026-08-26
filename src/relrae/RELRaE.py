from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import xmlschema
from pathlib import Path


from .modules.RuBREx import RuBREx
from .modules.LLM_Ref import LLMRefinement
from .modules.human_fix import HumanFix
from .utils import get_now


class RELRaE:

    def __init__(self, onto_name, schema, namespace, prefix, config,
                 components_root="relrae_components", output_root="output"):
        self.components_root = Path(components_root)
        self.output_root = Path(output_root)
        schema_path = self.components_root / "schema" / schema
        self.schema = xmlschema.XMLSchema(schema_path)
        self.namespace = Namespace(namespace)
        self.prefix = prefix
        self.onto_name = onto_name
        self.onto = Graph()
        self.errors = []
        self.config = config
        self.configs = [{"Pipeline": config}]
        self.logs = {}

        self.onto.bind('rdf', RDF)
        self.onto.bind('rdfs', RDFS)
        self.onto.bind('owl', OWL)
        self.onto.bind(self.prefix, self.namespace)

    def RuBREx(self):
        m_rubrex = RuBREx(
            self.schema, self.onto, self.prefix, self.namespace,
            self.components_root,
        )
        m_rubrex.match_concepts()
        m_rubrex.schema_coverage()

        self.configs.append({"RuBREx": m_rubrex.config})
        self.logs["RuBREx"] = m_rubrex.log
        # NOTE: Consider the module complete
        self.onto = self.onto + m_rubrex.onto
        self.errors.append(m_rubrex.errors)

    def LLM_Refinement_Loop(self):
        m_LLM_ref = LLMRefinement(
            self.schema, self.onto, self.prefix, self.namespace,
            self.components_root)
        m_LLM_ref.evaluate_relations()
        self.errors.append(m_LLM_ref.errors)

    def human_fix(self):
        # TODO:
        m_human_fix = HumanFix(
            self.schema, self.onto, self.prefix, self.namespace,
            self.components_root, self.errors, self.config["modules"]
        )
        m_human_fix.set_user_info()
        m_human_fix.fix_errors()

    def write_logs(self, path):
        for key, values in self.logs.items():
            with (path / f"{key}.txt").open("w", encoding="utf-8") as f:
                for line in values:
                    f.write(line + "\n")

    def write_metadata(self, path):
        with (path / "metadata.txt").open("w", encoding="utf-8") as f:
            for config in self.configs:
                for section, values in config.items():
                    f.write(f"{section}\n\n")
                    for key, value in values.items():
                        f.write(f"{key}: {value}\n")
                f.write("\n\n")

    def serialise(self):
        timestamp = get_now().replace(":", "-")
        main_path = self.output_root / f"{self.onto_name}{timestamp}"
        log_path = main_path / "logs"
        log_path.mkdir(parents=True)
        self.write_logs(log_path)
        self.write_metadata(main_path)
        self.onto.serialize(
            destination=main_path / f"{self.onto_name}.ttl",
            format="ttl",
        )
