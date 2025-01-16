import yaml, json


# Load the config file
def get_config():
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    return config


# Load all the guidelines
def get_guidelines():
    with open("guidelines.json", "r") as f:
        guidelines = json.load(f)
    return guidelines
