from pydantic import BaseModel, ConfigDict

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
