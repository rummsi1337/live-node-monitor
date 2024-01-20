from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, PrivateAttr

from components.log_monitor.logparser import LogEventParser


class TargetType(str, Enum):
    ELASTICSEARCH = "elasticsearch"


class Target(BaseModel):
    name: TargetType
    config: dict[str, str]


class LogMonitorEvent(BaseModel):
    name: str
    regexes: list[str]
    targets: list[Target]
    model_config = ConfigDict(extra="forbid")
    _parser: LogEventParser = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._parser = LogEventParser(self.name, self.regexes)
        return super().model_post_init(__context)

    @property
    def parser(self):
        return self._parser


class LogMonitorConfig(BaseModel):
    path: str
    events: list[LogMonitorEvent]
    model_config = ConfigDict(extra="forbid")


class LogMonitorConfigs(BaseModel):
    log_configs: list[LogMonitorConfig]
    model_config = ConfigDict(extra="forbid")
