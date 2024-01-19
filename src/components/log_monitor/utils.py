import yaml
from components.log_monitor.model import LogMonitorConfigs

def read_config(config_path: str) -> LogMonitorConfigs:
    with open(config_path, "r") as file:
        yaml_dict = yaml.safe_load(file)
        return LogMonitorConfigs(**yaml_dict)
