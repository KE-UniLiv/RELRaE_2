from datetime import datetime, timezone
import ast
import re


def split_top_level(value):
    parts = []
    current = []
    depth = 0
    quote = None

    for char in value:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            current.append(char)
            quote = char
        elif char in "[{(":
            current.append(char)
            depth += 1
        elif char in "]})":
            current.append(char)
            depth -= 1
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    parts.append("".join(current).strip())
    return parts


def parse_config_value(value):
    value = value.strip()

    if "," in value:
        parts = split_top_level(value)
        if len(parts) > 1:
            return [parse_config_value(part) for part in parts]

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def parse_config(path):
    config = {}

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)

            config[key.strip()] = parse_config_value(value)

    return config


def clean_namespace(label):
    clean_label = label.split('}')[-1]
    return clean_label


def namespace_to_prefix(value, namespace, prefix):
    namespace = str(namespace)
    value = str(value)

    if value.startswith(namespace):
        return f"{prefix}:{value[len(namespace):]}"
    return value


def prefix_to_namespace(value, namespace, prefix):
    namespace = str(namespace)
    value = str(value)
    prefix_marker = f"{prefix}:"

    if value.startswith(prefix_marker):
        return f"{namespace}{value[len(prefix_marker):]}"
    return value


def generate_provenance(prefix, tool, source):
    prov_block = f"""
        {prefix}:generatedBy '{tool}'@en ;
        {prefix}:hasXSDSource '{source}'@en .
    """
    # FIX: sort out temporal tracking
    #   {prefix}:createdAt '{get_now()}'^^xsd:dateTimeStamp ;
    #   {prefix}:lastEditied '{get_now()}'^^xsd:dateTimeStamp .
    # """
    return prov_block


def generate_preamble(prefix, namespace):
    preamble = f"""
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix xs: <http://www.w3.org/2001/XMLSchema/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix {prefix}: <{str(namespace)}> .

    """
    return preamble


def lower_first_char(label):
    first_char = label[0]
    back_label = label[1:]
    if back_label[0] != back_label[0].upper():
        processed_label = first_char.lower() + back_label
    else:
        processed_label = label
    return processed_label


def capitalise_first_char(label):
    first_char = label[0]
    back_label = label[1:]
    processed_label = first_char.upper() + back_label
    return processed_label


def normalise_string(string):
    norm_str = string.replace("\\", "\\\\").replace(
        "\n", "\\n").replace("'", '"')
    return norm_str


def normalise_label(label):
    label = re.sub(r'(?<!^)(?=[A-Z])', ' ', label)
    label = re.sub(r'[_\-]+', ' ', label)
    label = label.lower()
    label = re.sub(r'\s+', ' ', label).strip()
    return label


def get_now():
    return datetime.now(timezone.utc).isoformat()
