import json
import re
import time
from dataclasses import dataclass
from typing import Iterator, List, Optional


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


class ErrorEventParser(EventParser):
    def __init__(self) -> None:
        name = "err_line_event"
        regex_matchers = [
            r"^(?P<timestamp>.+) \| (?P<level>ERROR|CRITICAL): (?P<message>.+)$",  # Match with timestamp
            r"(?P<level>ERROR|CRITICAL): (?P<message>.+)$",  # Match if timestamp does not exist in log
        ]
        super().__init__(name, regex_matchers)

    def _parse(self, match: re.Match) -> dict:
        return match.groupdict()


class LoggedEventParser(EventParser):
    def __init__(self) -> None:
        name = "log_line_event"
        regex_matchers = [
            r"^(?P<timestamp>.+) \| \[(?P<event>.+-event)\] (?P<content>.*)",  # Match with timestamp
            r"\[(?P<event>.+-event)\] (?P<content>.*)",  # Match if timestamp does not exist in log
        ]
        super().__init__(name, regex_matchers)

    def _parse(self, match: re.Match) -> dict:
        result = match.groupdict()
        event = result["event"]
        content = result["content"]

        if event == "SMRT-event":
            return f"SMRT: {content}"

        elif event == "STP-event":
            return f"STP: {content}"

        # TODO: JSON-event does not make sense. The event name should reference the type of event, not how to parse it
        elif event == "JSON-event":
            return json.loads(content)

        else:
            return content


class LogMonitor:
    def __init__(self, log_file_path: str) -> None:
        self.log_file_path = log_file_path
        self.line_event_parsers = [
            ErrorEventParser(),
            LoggedEventParser(),
        ]

    def start_monitoring(self):
        with open(self.log_file_path, "r") as logfile:
            loglines = self._follow(logfile)
            for line in loglines:
                parsed_line = self._retrieve_line_event(line)
                if parsed_line:
                    # TODO: Send each parsed line event to the api service
                    print(parsed_line)

    def _retrieve_line_event(self, line: str) -> Optional[dict]:
        """
        Find line events and parse corresponding log line.
        Return dict of line event if found, otherwise None
        """
        for parser in self.line_event_parsers:
            if result := parser.parse_line(line):
                return result
        return None

    @staticmethod
    def _follow(file, sleep_timeout=0.1) -> Iterator[str]:
        line = ""
        while True:
            tmp_line = file.readline()
            if tmp_line:
                line += tmp_line
                if line.endswith("\n"):
                    yield line
                    line = ""
            else:
                time.sleep(sleep_timeout)


if __name__ == "__main__":
    log_monitor = LogMonitor("/workspaces/live-node-monitor/test_log.txt")
    log_monitor.start_monitoring()
