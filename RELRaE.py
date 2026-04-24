from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import xmlschema


from modules.RuBREx import RuBREx
from modules.LLM_Ref import LLM_Refinement
from modules.human_fix import human_fix


class RELRaE:

    def __init__(self, schema, namespace, prefix):
        self.schema = xmlschema.XMLSchema(open(f"schema/{schema}"))
        self.namespace = Namespace(namespace)
        self.prefix = prefix
        self.onto = Graph()
        self.errors = []

        self.onto.bind('rdf', RDF)
        self.onto.bind('rdfs', RDFS)
        self.onto.bind('owl', OWL)
        self.onto.bind(self.prefix, self.namespace)

    def RuBREx(self):
        # TODO:
        m_rubrex = RuBREx(self.schema, self.onto, self.prefix, self.namespace)
        m_rubrex.match_concepts()

        # NOTE: Consider the module complete
        self.onto = self.onto + m_rubrex.onto
        self.errors.append(m_rubrex.errors)

    def LLM_Refinement_Loop(self):
        # TODO:
        LLM_Refinement()

    def human_fix(self):
        # TODO:
        human_fix()
