from typing import Iterator, Optional
import asyncio
from aiofile import async_open
import glob
from components.log_monitor.utils import read_config
from components.log_monitor.model import LogMonitorEvent
from components.log_monitor.logparser import LogEventParser


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


def run_log_monitor(config_path: str):
    configs = read_config(config_path)
    log_monitors = []
    for config in configs.log_configs:
        for path in glob.glob(config.path):
            log_monitors.append(LogMonitor(path, config.events))
    asyncio.run(start_monitors(log_monitors))
