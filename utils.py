def parse_config(path):
    config = {}

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # skip empty lines or comments
            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)

            # handle comma-separated values as lists
            if "," in value:
                value = [v.strip() for v in value.split(",")]

            config[key.strip()] = value

    return config
