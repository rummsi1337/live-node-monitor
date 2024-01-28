import asyncio
import logging
from typing import Iterator, Optional

from aiofile import async_open
from elasticsearch import AsyncElasticsearch

from components.base.base_monitor import BaseMonitor
from model import LogMonitorEvent

logger = logging.getLogger(__name__)


class LogMonitor(BaseMonitor):
    def __init__(
        self,
        log_file_path: str,
        log_events: list[LogMonitorEvent],
        es: AsyncElasticsearch,
    ) -> None:
        super().__init__(es)
        self.log_file_path = log_file_path
        self.events = log_events

    async def start_monitoring(self):
        async with async_open(self.log_file_path, "r") as logfile:
            loglines = self._follow(logfile)
            # TODO: multi log-line parsing could be done by
            # storing the last x lines in the log and moving on via sliding window
            async for line in loglines:
                try:
                    await self._retrieve_line_event(line)
                except Exception:
                    # TODO: proper exception handling. Make sure the parser can continue but properly logs the errors.
                    logger.exception(f"Exception while parsing log line: {line}.")

    def stop_monitoring(self) -> None:
        # TODO: stop monitoring
        pass

    async def _retrieve_line_event(self, line: str) -> Optional[dict]:
        """
        Find line events and parse corresponding log line.
        Return dict of line event if found, otherwise None
        """
        for event in self.events:
            if result := event.parser.parse_line(line):
                logger.info(result)
                # TODO: also store timestamp of log, if found in log.
                # Should be there anyways, but how to parse? timestamp format as option?
                await self._save_data(result, event.targets)
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
