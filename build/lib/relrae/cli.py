import argparse
from importlib.resources import files
from pathlib import Path
import shutil


COMPONENT_DIRECTORIES = ("config", "rules", "schema", "output")


def _copy_defaults(source, destination):
    """Copy packaged defaults without replacing user-edited files."""
    for resource in source.iterdir():
        # Finder metadata is not part of a RELRaE project, even if it happens
        # to be present in a source checkout.
        if resource.name.startswith("."):
            continue

        target = destination / resource.name
        if resource.is_dir():
            target.mkdir(exist_ok=True)
            _copy_defaults(resource, target)
        elif not target.exists():
            with resource.open("rb") as source_file, target.open("xb") as target_file:
                shutil.copyfileobj(source_file, target_file)


def initialise_project(project_root=None):
    """Create a RELRaE project beneath *project_root* (the cwd by default).

    Existing files are intentionally left untouched, making ``relrae init``
    safe to run again after configuration files have been customised.
    """
    project_root = Path.cwd() if project_root is None else Path(project_root)
    components_root = project_root / "relrae_components"

    project_root.mkdir(parents=True, exist_ok=True)
    for directory in COMPONENT_DIRECTORIES:
        (components_root / directory).mkdir(parents=True, exist_ok=True)

    packaged_defaults = files("relrae").joinpath("relrae_components")
    _copy_defaults(packaged_defaults, components_root)

    print(f"Initialised RELRaE project in {components_root}")
    return components_root


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init", help="create a RELRaE project in the current directory"
    )
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="project directory (default: current directory)",
    )

    args = parser.parse_args()

    if args.command == "init":
        initialise_project(args.directory)
