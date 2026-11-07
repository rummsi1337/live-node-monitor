from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr, ValidationInfo, field_validator

from components.log_monitor.logparser import LogEventParser


class TargetType(str, Enum):
    ELASTICSEARCH = "elasticsearch"


class Target(BaseModel):
    type: TargetType
    config: dict[str, str]


class LogMonitorEvent(BaseModel):
    name: str
    regexes: list[str]
    targets: list[Target]
    model_config = ConfigDict(extra="forbid")
    _parser: LogEventParser = PrivateAttr()

    def model_post_init(self, context: Any, /) -> None:
        self._parser = LogEventParser(self.name, self.regexes)
        return super().model_post_init(context)

    @property
    def parser(self):
        return self._parser


class Timestamp(BaseModel):
    regex_group_key: str
    string_format: str


class LogMonitorConfig(BaseModel):
    path: str
    timestamp: Timestamp | None = None
    events: list[LogMonitorEvent]
    model_config = ConfigDict(extra="forbid")


class CmdMonitorEvent(BaseModel):
    name: str
    command: str
    targets: list[Target]
    repeat: float | None = None
    chdir: str | None = None
    model_config = ConfigDict(extra="forbid")

    @field_validator("repeat")
    @classmethod
    def check_bigger_than_zero(cls, v: float, info: ValidationInfo) -> float:
        if isinstance(v, float):
            assert v > 0.0, f"{info.field_name} must be a positive non-zero value"
        return v

    @field_validator("chdir")
    @classmethod
    def check_dir_exists(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(v, str):
            assert Path(v).exists(), f"{info.field_name} path does not exist"
            assert Path(v).is_dir(), f"{info.field_name} path is not a directory"
        return v


class CmdMonitorConfig(BaseModel):
    events: list[CmdMonitorEvent]
    model_config = ConfigDict(extra="forbid")


class MonitorConfigs(BaseModel):
    log_configs: list[LogMonitorConfig]
    cmd_configs: list[CmdMonitorConfig]
    model_config = ConfigDict(extra="forbid")
