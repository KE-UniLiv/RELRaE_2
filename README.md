<p align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="assets/Logo_Text_Black.png">
        <source media="(prefers-color-scheme: light)" srcset="assets/Logo_Text_White.png">
        <img alt="RELRaE">
    </picture>
</p>

# RELRaE 2.0

[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-31214/)

Relationship Extraction, Labelling, Refinement, and Evaluation (RELRaE) is a
Python framework for generating and refining RDF ontologies from XML Schema
definitions.

RELRaE 2.0 is a reworking on the origin [RELRaE](https://github.com/KE-UniLiv/RELRaE) framework

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

### Config File: `pipeline_conf.txt`

- `modules`: The modules being used in the pipeline.
- `schema`: The name of the schema file used. Looks in `relrae_components\schema`
  by default.
- `namespace`: The namespace of the output ontology.
- `prefix`: The abbreviation of the namespace used for readability.
- `ontology_name`: The name of the ontology file.

## RELRaE Modules

### RuBREx - Rules-Based Relationship Extraction

RuBREx is the *only* required module for a RELRaE pipeline. Additionally, it
must be the first module in the pipeline as it performs the initial translation
of the XML schema into a skeleton ontology. This is done through a specified
ruleset (expanded on later).

#### Config File : `RuBREx_conf.txt`

- `ruleset`: The file name of the ruleset you are using. By default RuBREx looks
  in `relrae_components/rules` for the ruleset you have given.

### LLM Refinement Loop

The LLM Refinement Loop module iterates through all relationships in the skeleton
ontology and attempts to generate a more suitable label for the relationship beyond
the simple label created previously. The first LLM assesses if the label is a
good fit for the relationship based on supplied context. If the label is
rejected, this is passed on to a second LLM which attempts to improve the label
before passing it back to the first model for another evaluation. If a label stays
rejected after x iterations, it is flagged for human review.

It is important to note that different models from different organisations can
be used for each LLM. Currently we aim to support the apis of Ollama, OpenAI,
and GoogleAI.

#### Config File: `LLM_ref_conf.txt`

- `domain`: The domain that the XML schema represents.
- `source`: The input file type (currently only XML schema supported)
- `refinement_loops`: Number of refinement attempts the modules has per relation.
- `eval_llm`: `model_name`,`api_key`,`{parameter: value}`
- `eval_prompt_strat`: few/one/zero - The number of examples provided to the
  eval LLM.
- `eval_repeats`: The number of times the evaluation is repeated before a consensus
  is reached.
- `eval_examples`: `[{"role":role, "content":example}]` - List of example
  responses for the eval LLM.
- `eval_messages`: `["message"]` - The prompt message for eval LLM.
- `ref_llm`: `model_name`,`api_key`,`{parameter: value}`
- `ref_prompt_strat`: few/one/zero - The number of examples provided to the
  refinement LLM.
- `ref_repeats`: The number of times the refinement is repeated before a consensus
  is reached. Currently only a value of 1 is supported.
- `ref_examples`: `[{"role":role, "content":example}]` - List of example
  responses for the refinement LLM.
- `ref_messages`: `["message"]` - The prompt message for refinement LLM.

### Human Fix

The Human Fix module, implements a human-in-the-loop solution into a RELRaE pipeline.
As a module runs, any errors identified during representation are recorded and are
then provided to the human reviewer. The user must input their data for provenance so
any changes are recorded in the schema.

For RuBREx errors, concepts in the XML schema that have not been represented are
provided to the user. The user can then chose if a concept should be represented or note.
Currently this outputs a text file along the final ontology with a list of the concepts to
represent. In future we aim to implements a system allowing the user to create and inject
the required RDF during execution.

For LLM Refinement Loop errors, the user is presented with relationships that the LLMs could
not generate suitable labels for. The user can then enter their own label for this relation
and the ontology is updated accordingly.

## Python API

The main pipeline class is available from the package root:

```python
from relrae import RELRaE
```

See [`scripts/test_pipeline.py`](scripts/test_pipeline.py) for an end-to-end
pipeline example using the sample data under `examples/`.

## Customising the RuBREx ruleset

The required first module of any RELRaE pipeline is the RuBREx module.
This module uses the ruleset specified in `RuBREx_conf.txt` to naively transform
the given XML schema. The default ruleset is simple by design to limit the
ontological commitments made by this module. It can be extended or altered by
any user wishing to achieve a richer ontology for a specific use case. Rulesets
are written in YAML following a custom format, SXPF (Simple XML Pattern Format).
Documentation on SXPF and what functionality is supported is detailed in [SXPF Docs](https://github.com/KE-UniLiv/RELRaE_2/blob/master/SXPF_Docs.md)

## Project links

- [Source repository](https://github.com/KE-UniLiv/RELRaE_2)
- [Issue tracker](https://github.com/KE-UniLiv/RELRaE_2/issues)

RELRaE is a new and growing project. We welcome any contributions to the framework,
and are grateful for your support through citations and starring the GitHub repository

## Citing RELRaE

Should you wish to use RELRaE as part of your research, you can cite RELRaE as follows

```bibtex
@misc{hannah2026relrae,
  Info to come soon
}
```

## License

RELRaE is distributed under the [MIT License](LICENSE).
