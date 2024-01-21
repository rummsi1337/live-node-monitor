import yaml
from model import MonitorConfigs


def read_config(config_path: str) -> MonitorConfigs:
    with open(config_path, "r") as file:
        yaml_dict = yaml.safe_load(file)
        return MonitorConfigs(**yaml_dict)
