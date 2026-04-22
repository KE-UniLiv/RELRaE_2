import yaml
from utils import parse_config


class RuBREx:

    def __init__(self, schema, onto):
        self.rules = self.load_rules()
        self.errors = []
        self.schema = schema
        self.onto = onto

    def load_rules(self):
        CONFIG = "config/RuBREx_conf.txt"
        rulset_path = f"rules/{parse_config(CONFIG)["ruleset"]}"
        self.rules = None
        with open(rulset_path) as file:
            try:
                self.rules = yaml.safe_load(file)
                print(f"Ruleset {rulset_path} succesfully loaded")
            except Exception as exc:
                print(exc)
        if self.rules is not None:
            return self.rules
        else:
            raise Exception

    def match_concepts(self):
        pass
