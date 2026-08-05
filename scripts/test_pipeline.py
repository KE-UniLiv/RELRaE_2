# NOTE: DEPRECATED
"""
RELRaE Framework
Relationship Extraction, Labelling, Refinement, and Evaluation

Usage quick-guide:
 - Set up correct config files in config/
 - Instantiate a RELRaE object
 - Call modules as methods of the object

This file is an entry point to use framework from a static pipeline config file
 -> Defined in config/pipeline_conf.txt

Modules can be called manually as methods with individual config files
 -> config/RuBREx_conf.txt
 -> config/LLM_Refinement_conf.txt
 -> config/Human_conf.txt
"""

import configparser
from relrae.RELRaE import RELRaE


def run_pipeline(pipeline, modules):
    if modules[0] != "RuBREx":
        print("WARNING!!! RuBREx is required as the 1st module, running your pipeline without this may lead to unseen errors")
    for m in modules:
        print(f"Running {m} ...")
        getattr(pipeline, m)()


def main():
    cfg = configparser.ConfigParser()
    cfg.read("config/pipeline_conf.txt")
    modules = cfg["MAIN"]["modules"]
    schema = cfg["MAIN"]["schema"]
    namespace = cfg["MAIN"]["namespace"]
    prefix = cfg["MAIN"]["prefix"]
    ontology_name = cfg["MAIN"]["ontology_name"]
    pipeline = RELRaE(ontology_name, schema, namespace, prefix, cfg["MAIN"])
    run_pipeline(pipeline, modules)
    pipeline.serialise()


if __name__ == "__main__":
    main()
