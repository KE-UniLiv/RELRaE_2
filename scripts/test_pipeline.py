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
