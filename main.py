# Entry to RELRaE
import argparse

from schema_processor import Schema


def run(args):
    schema = args.schema

    # Process schema
    current_schema = Schema(schema)
    current_schema.extract_concepts()
    current_schema.fragment_generation()
    fragments_list = current_schema.return_fragments()

    # Refine fragments

    # Create Graph


def main():
    parser = argparse.ArgumentParser(
        prog='RELRaE 2',
        description='A LLM-enhanced framework for translating an XML schema into an RDFS ontology'
    )
    parser.add_argument(
        '-s',
        type=str,
        help="The path of the input XML schema",
        dest='schema',
        required=True
    )

    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
