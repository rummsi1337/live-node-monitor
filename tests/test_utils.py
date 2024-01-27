import os
from utils import read_config


def test_read_config():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = f"{ROOT_DIR}/fixtures/utils/test_read_config_valid.yaml"
    config = read_config(config_path)
    assert len(config.cmd_configs) == 1
    assert len(config.cmd_configs[0].events) == 2
    assert len(config.log_configs) == 1
    assert len(config.log_configs[0].events) == 2
