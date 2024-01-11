import glob
import json
import re
from typing import Iterator, Optional
from typing_extensions import Annotated
from pydantic import AfterValidator, BaseModel, ConfigDict
import yaml
import asyncio
from aiofile import async_open


class EventParser:
    def __init__(self, name: str, regex_matchers: list) -> None:
        self.name = name
        self.regex_matchers = regex_matchers

    def parse_line(self, line: str) -> Optional[dict]:
        for pattern in self.regex_matchers:
            match = re.search(pattern, line)
            if match:
                print(f"New event found: {self.name}")
                return self._parse(match)
        return None

    def _parse(self, match: re.Match) -> dict:
        raise NotImplementedError("abstract base class")


class LogEventParser(EventParser):
    def __init__(self, name: str, regex_matchers: list) -> None:
        super().__init__(name, regex_matchers)

    def _parse_json_group(self, json_string: str) -> dict:
        return json.loads(json_string)

    def _parse(self, match: re.Match) -> dict:
        """Parse lines using events defined in log_monitor_config.
        Each parsed event contains the matched line, pattern and all named groups.
        Some special named groups trigger further parsing inside the matched group.
        In addition to the named group, also the contents of the parsed groups are returned.
        Special named groups:
          - json: Parses the content of the named group as json.

        Args:
            match (re.Match): the matched object.

        Returns:
            dict: A dict containing the matched line, pattern and all named groups inlcuding parsed special groups.
        """
        named_groups = match.groupdict()

        if json_str := named_groups.get("json"):
            named_groups.update(self._parse_json_group(json_str))
            named_groups.pop("json", None)

        named_groups.update({"line": match.string, "pattern": match.re.pattern})

        return named_groups


class LogMonitorEvent(BaseModel):
    name: str
    regexes: list[str]
    model_config = ConfigDict(extra="forbid")


class LogMonitorConfig(BaseModel):
    path: str
    events: list[LogMonitorEvent]
    model_config = ConfigDict(extra="forbid")


class LogMonitorConfigs(BaseModel):
    log_configs: list[LogMonitorConfig]
    model_config = ConfigDict(extra="forbid")


def read_config() -> LogMonitorConfigs:
    with open(
        "/workspaces/live-node-monitor/src/components/log_monitor_config.yaml", "r"
    ) as file:
        yaml_dict = yaml.safe_load(file)
        return LogMonitorConfigs(**yaml_dict)


class LogMonitor:
    def __init__(self, log_file_path: str, log_events: list[LogMonitorEvent]) -> None:
        self.log_file_path = log_file_path
        self.event_parsers = []
        for event in log_events:
            self.event_parsers.append(LogEventParser(event.name, event.regexes))

    async def start_monitoring(self):
        async with async_open(self.log_file_path, "r") as logfile:
            loglines = self._follow(logfile)
            async for line in loglines:
                parsed_line = self._retrieve_line_event(line)
                if parsed_line:
                    # TODO: Send each parsed line event to the api service
                    print(parsed_line)

    def _retrieve_line_event(self, line: str) -> Optional[dict]:
        """
        Find line events and parse corresponding log line.
        Return dict of line event if found, otherwise None
        """
        for parser in self.event_parsers:
            if result := parser.parse_line(line):
                return result
        return None

    @staticmethod
    async def _follow(file, sleep_timeout=0.1) -> Iterator[str]:
        line = ""
        while True:
            tmp_line = await file.readline()
            if tmp_line:
                line += tmp_line
                if line.endswith("\n"):
                    yield line
                    line = ""
            else:
                await asyncio.sleep(sleep_timeout)


async def start_monitors(log_monitors: list[LogMonitor]):
    tasks = []
    for monitor in log_monitors:
        tasks.append(asyncio.create_task(monitor.start_monitoring()))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    configs = read_config()
    log_monitors = []
    for config in configs.log_configs:
        for path in glob.glob(config.path):
            log_monitors.append(LogMonitor(path, config.events))
    asyncio.run(start_monitors(log_monitors))
