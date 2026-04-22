from rdflib import Graph
import xmlschema


from modules.RuBREx import RuBREx
from modules.LLM_Ref import LLM_Refinement
from modules.human_fix import human_fix


class RELRaE:

    def __init__(self, schema):
        self.schema = xmlschema.XMLSchema(open(schema))
        self.onto = Graph()

    def RuBREx(self):
        # TODO:
        RuBREx()

    def LLM_Refinement_Loop(self):
        # TODO:
        LLM_Refinement()

    def human_fix(self):
        # TODO:
        human_fix()
