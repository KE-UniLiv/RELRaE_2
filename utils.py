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
