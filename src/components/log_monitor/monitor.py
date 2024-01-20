from typing import Iterator, Optional
import asyncio
from aiofile import async_open
import glob

from elasticsearch import AsyncElasticsearch
from components.log_monitor.utils import read_config
from components.log_monitor.model import LogMonitorEvent, Target, TargetType


class LogMonitor:
    def __init__(
        self,
        log_file_path: str,
        log_events: list[LogMonitorEvent],
        es: AsyncElasticsearch,
    ) -> None:
        self.log_file_path = log_file_path
        self.events = log_events
        self.es = es

    async def start_monitoring(self):
        async with async_open(self.log_file_path, "r") as logfile:
            loglines = self._follow(logfile)
            async for line in loglines:
                try:
                    parsed_line = await self._retrieve_line_event(line)
                    if parsed_line:
                        print(parsed_line)
                except Exception as e:
                    # TODO: proper exception handling. Make sure the parser can continue but properly logs the errors.
                    print(e)

    async def _retrieve_line_event(self, line: str) -> Optional[dict]:
        """
        Find line events and parse corresponding log line.
        Return dict of line event if found, otherwise None
        """
        for event in self.events:
            if result := event.parser.parse_line(line):
                await self._save_data(result, event.targets)
                return result
        return None

    async def _save_data(self, data: dict, targets: list[Target]):
        for target in targets:
            if target.name == TargetType.ELASTICSEARCH:
                response = await self._save_data_es(data, target.config)
                print(response)

    async def _save_data_es(self, data: dict, config: dict):
        # TODO: sending documents individually or sending them in bulk?
        # Can the mechanism be rebuilt to use https://elasticsearch-py.readthedocs.io/en/v8.12.0/async.html#bulk-and-streaming-bulk
        return await self.es.index(index=config["index"], document=data)

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


def run_log_monitor(config_path: str, es: AsyncElasticsearch):
    configs = read_config(config_path)
    log_monitors = []
    for config in configs.log_configs:
        for path in glob.glob(config.path):
            log_monitors.append(LogMonitor(path, config.events, es))
    asyncio.run(start_monitors(log_monitors))
