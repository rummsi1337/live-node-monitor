import json
import re
from typing import Optional


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
