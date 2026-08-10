import argparse
from importlib.resources import files
from pathlib import Path
import shutil


def initialise_project():
    # Install RELRaE to current directory
    # Create relrae_components
    # create config, rules, schema, and output within relrae_components
    #
    # Insert base ruleset to rules
    # Insert base configs to config
    pass

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")

    args = parser.parse_args()

    if args.command == "init":
        initialise_project()
