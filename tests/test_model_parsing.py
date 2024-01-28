import pytest
import yaml
from pydantic import ValidationError

from model import (
    CmdMonitorConfig,
    CmdMonitorEvent,
    LogMonitorConfig,
    LogMonitorEvent,
    MonitorConfigs,
    Target,
    TargetType,
)


def test_target_valid():
    yaml_string = f"""
      type: {TargetType.ELASTICSEARCH}
      config:
        index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    Target(**input_dict)


def test_target_unknown():
    yaml_string = """
      type: unknown_target
      config:
        index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        Target(**input_dict)
    assert (
        "Input should be 'elasticsearch' [type=enum, input_value='unknown_target', input_type=str]"
        in str(excinfo.value)
    )


def test_log_monitor_event_valid():
    yaml_string = """
      name: "log_event"
      regexes:
        - '.*'
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    LogMonitorEvent(**input_dict)


def test_log_monitor_event_unknown_key():
    yaml_string = """
      name: "log_event"
      regexes:
        - '.*'
      unknown_key: unknown_value
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        LogMonitorEvent(**input_dict)
    assert "unknown_key" in str(excinfo.value)


def test_log_monitor_event_missing_key():
    yaml_string = """
      name: "log_event"
      regexes:
        - '.*'
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        LogMonitorEvent(**input_dict)
    assert "targets" in str(excinfo.value)


def test_log_monitor_config_valid():
    yaml_string = """
      path: "/tmp/log.txt"
      events:
        - name: "log_event"
          regexes:
            - '.*'
          targets:
            - type: elasticsearch
              config:
                index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    LogMonitorConfig(**input_dict)


def test_log_monitor_config_unknown_key():
    yaml_string = """
      path: "/tmp/log.txt"
      unknown_key: unknown_value
      events:
        - name: "log_event"
          regexes:
            - '.*'
          targets:
            - type: elasticsearch
              config:
                index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        LogMonitorConfig(**input_dict)
    assert "unknown_key" in str(excinfo.value)


def test_log_monitor_config_missing_key():
    yaml_string = """
      events:
        - name: "log_event"
          regexes:
            - '.*'
          targets:
            - type: elasticsearch
              config:
                index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        LogMonitorConfig(**input_dict)
    assert "path" in str(excinfo.value)


def test_cmd_monitor_event_valid():
    yaml_string = """
      name: "log_event"
      command: "ls -la"
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    event = CmdMonitorEvent(**input_dict)
    assert event.name == "log_event"
    assert event.command == "ls -la"
    assert event.chdir is None
    assert event.repeat is None


def test_cmd_monitor_event_unknown_key():
    yaml_string = """
      name: "log_event"
      command: "ls -la"
      unknown_key: unknown_value
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorEvent(**input_dict)
    assert "unknown_key" in str(excinfo.value)


def test_cmd_monitor_event_missing_key():
    yaml_string = """
      name: "log_event"
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorEvent(**input_dict)
    assert "command" in str(excinfo.value)


def test_cmd_monitor_event_repeat_zero():
    yaml_string = """
      name: "zero_repeat_event"
      command: "ls -la"
      repeat: 0
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorEvent(**input_dict)
    assert "repeat must be a positive non-zero value" in str(excinfo.value)


def test_cmd_monitor_event_chdir_does_not_exist():
    yaml_string = """
      name: "zero_repeat_event"
      command: "ls -la"
      chdir: /tmp/non_existing_directory/
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorEvent(**input_dict)
    assert "chdir path does not exist" in str(excinfo.value)


def test_cmd_monitor_event_chdir_not_a_directory(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test file")
    yaml_string = f"""
      name: "zero_repeat_event"
      command: "ls -la"
      chdir: {file_path.as_posix()}
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorEvent(**input_dict)
    assert "chdir path is not a directory" in str(excinfo.value)


def test_cmd_monitor_config_valid():
    yaml_string = """
      events:
        - name: "cmd_event"
          command: "ls -la"
          targets:
            - type: elasticsearch
              config:
                index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    CmdMonitorConfig(**input_dict)


def test_cmd_monitor_config_unknown_key():
    yaml_string = """
      unknown_key: unknown_value
      events:
        - name: "cmd_event"
          command: "ls -la"
          targets:
            - type: elasticsearch
              config:
                index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorConfig(**input_dict)
    assert "unknown_key" in str(excinfo.value)


def test_cmd_monitor_config_missing_key():
    input_dict = {}
    with pytest.raises(ValidationError) as excinfo:
        CmdMonitorConfig(**input_dict)
    assert "events" in str(excinfo.value)


def test_monitor_configs_valid():
    yaml_string = """
      log_configs:
        - path: "/tmp/log.txt"
          events:
            - name: "log_event"
              regexes:
                - '.*'
              targets:
                - type: elasticsearch
                  config:
                    index: "index"
      cmd_configs:
        - events:
            - name: "cmd_event"
              command: "ls -la"
              targets:
                - type: elasticsearch
                  config:
                    index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    MonitorConfigs(**input_dict)


def test_monitor_configs_unknown_key():
    yaml_string = """
      unknown_key: unknown_value
      log_configs:
        - path: "/tmp/log.txt"
          events:
            - name: "log_event"
              regexes:
                - '.*'
              targets:
                - type: elasticsearch
                  config:
                    index: "index"
      cmd_configs:
        - events:
            - name: "cmd_event"
              command: "ls -la"
              targets:
                - type: elasticsearch
                  config:
                    index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        MonitorConfigs(**input_dict)
    assert "unknown_key" in str(excinfo.value)


def test_monitor_configs_missing_key():
    yaml_string = """
      cmd_configs:
        - events:
            - name: "cmd_event"
              command: "ls -la"
              targets:
                - type: elasticsearch
                  config:
                    index: "index"
    """
    input_dict = yaml.safe_load(yaml_string)
    with pytest.raises(ValidationError) as excinfo:
        MonitorConfigs(**input_dict)
    assert "log_configs" in str(excinfo.value)
