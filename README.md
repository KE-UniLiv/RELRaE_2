# RELRaE 2.0

Relationship Extraction, Labelling, Refinement, and Evaluation (RELRaE) is a
Python framework for generating and refining RDF ontologies from XML Schema
definitions.

## Requirements

- Python 3.12 or newer

## Installation

Install the latest published release with pip:

```console
python -m pip install relrae
```

To install a local checkout for development:

```console
python -m pip install -e .
```

## Create a project

Run the initializer inside a new project directory:

```console
relrae init
```

You can also provide the destination explicitly:

```console
relrae init path/to/project
```

This creates the following structure without overwriting existing files:

```text
relrae_components/
├── config/
│   ├── LLM_ref_conf.txt
│   ├── RuBREx_conf.txt
│   └── pipeline_conf.txt
├── output/
├── rules/
│   └── SXPF_General_1_0.yaml
└── schema/
```

Place an XML Schema file in `relrae_components/schema/`, then configure its
filename, namespace, prefix, ontology name, and pipeline modules in
`relrae_components/config/pipeline_conf.txt`.

## Python API

The main pipeline class is available from the package root:

```python
from relrae import RELRaE
```

See [`scripts/test_pipeline.py`](scripts/test_pipeline.py) for an end-to-end
pipeline example using the sample data under `examples/`.

## Project links

- [Source repository](https://github.com/KE-UniLiv/RELRaE_2)
- [Issue tracker](https://github.com/KE-UniLiv/RELRaE_2/issues)

## License

RELRaE is distributed under the [MIT License](LICENSE).
