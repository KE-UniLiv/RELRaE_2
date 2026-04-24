from datetime import datetime
import pytz


def parse_config(path):
    config = {}

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)

            if "," in value:
                value = [v.strip() for v in value.split(",")]

            config[key.strip()] = value

    return config


def clean_namespace(label):
    clean_label = label.split('}')[-1]
    return clean_label


def generate_provenance(prefix, tool, source):
    prov_block = f"""
        {prefix}:generatedBy {prefix}:{tool} ;
        {prefix}:hasXSDSource '{source}'@en ;
        {prefix}:createdAt '{datetime.now(pytz.utc).isoformat()}'^^xsd:dateTimeStamp ;
        {prefix}:lastEditied '{datetime.now(pytz.utc).isoformat()}'^^xsd:dateTimeStamp .
    """
    return prov_block


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
