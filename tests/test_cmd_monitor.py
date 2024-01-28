import asyncio
from unittest.mock import AsyncMock

import pytest
import yaml

from components.command_monitor.monitor import CommandMonitor
from model import CmdMonitorEvent


@pytest.mark.asyncio
async def test_cmd_monitoring(tmp_path):
    file_name = "test_file.txt"
    test_file_path = tmp_path / file_name

    expected_file_content = "This is a test file."
    expected_stderr = ""
    expected_command = f"cat {file_name}"
    expected_chdir = f"{tmp_path.as_posix()}"

    test_file_path.write_text(expected_file_content)

    yaml_string = f"""
      name: "cmd event"
      command: {expected_command}
      repeat: 0.1
      chdir: "{expected_chdir}"
      targets:
        - type: elasticsearch
          config:
            index: "index"
    """

    input_dict = yaml.safe_load(yaml_string)
    cmd_event = CmdMonitorEvent(**input_dict)

    es_mock = AsyncMock()
    es_mock.index.return_value = {"success": True}

    monitor = CommandMonitor(cmd_event, es_mock)

    task = asyncio.create_task(monitor.start_monitoring())

    # Wait for two consecutive command iterations
    await asyncio.sleep(0.2)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert es_mock.index.call_count == 2
    for call in es_mock.index.call_args_list:
        es_document = call.kwargs["document"]
        assert es_document["command"] == expected_command
        assert es_document["chdir"] == expected_chdir
        assert es_document["stdout"] == expected_file_content
        assert es_document["stderr"] == expected_stderr
