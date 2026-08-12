import configparser
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPOSITORY_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from relrae.RELRaE import RELRaE


def run_pipeline(pipeline, modules):
    if modules[0] != "RuBREx":
        print("WARNING!!! RuBREx is required as the 1st module, running your pipeline without this may lead to unseen errors")
    for m in modules:
        print(f"Running {m} ...")
        getattr(pipeline, m)()


def main():
    project_root = REPOSITORY_ROOT / "examples" / "animl"
    components_root = project_root / "relrae_components"
    cfg = configparser.ConfigParser()
    config_path = components_root / "config" / "pipeline_conf.txt"
    if not cfg.read(config_path):
        raise FileNotFoundError(f"Pipeline configuration not found: {config_path}")

    modules = [
        module.strip()
        for module in cfg["MAIN"]["modules"].split(",")
        if module.strip()
    ]
    schema = cfg["MAIN"]["schema"]
    namespace = cfg["MAIN"]["namespace"]
    prefix = cfg["MAIN"]["prefix"]
    ontology_name = cfg["MAIN"]["ontology_name"]
    pipeline = RELRaE(
        ontology_name,
        schema,
        namespace,
        prefix,
        cfg["MAIN"],
        components_root=components_root,
        output_root=components_root / "output",
    )
    run_pipeline(pipeline, modules)
    pipeline.serialise()


if __name__ == "__main__":
    main()
