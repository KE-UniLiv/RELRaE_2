from rdflib import Graph
import xmlschema


from modules.RuBREx import RuBREx
from modules.LLM_Ref import LLM_Refinement
from modules.human_fix import human_fix


class RELRaE:

    def __init__(self, schema):
        self.schema = xmlschema.XMLSchema(open(f"schema/{schema}"))
        self.onto = Graph()
        self.errors = []

    def RuBREx(self):
        # TODO:
        m_rubrex = RuBREx(self.schema, self.onto)
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
