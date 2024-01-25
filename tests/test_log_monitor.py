import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiofile import async_open
import pytest
import yaml
from components.log_monitor.monitor import LogMonitor
from model import LogMonitorEvent


@pytest.mark.asyncio
async def test_log_monitoring(tmp_path):
    log_file_path = tmp_path / "log.txt"
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
    log_event = LogMonitorEvent(**input_dict)

    es_mock = AsyncMock()
    es_mock.index.return_value = {"success": True}

    monitor = LogMonitor(log_file_path, [log_event], es_mock)

    with open(log_file_path, "a") as file:
        file.write("log_line: 1\n")

    task = asyncio.create_task(monitor.start_monitoring())

    with open(log_file_path, "a") as file:
        file.write("log_line: 2\n")

    await asyncio.sleep(0.1)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert es_mock.index.call_count == 2
    assert es_mock.index.call_args_list[0].kwargs["document"]["line"] == "log_line: 1\n"
    assert es_mock.index.call_args_list[1].kwargs["document"]["line"] == "log_line: 2\n"
