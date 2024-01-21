import asyncio
import glob
import os
from elasticsearch import AsyncElasticsearch
from components.base.base_monitor import BaseMonitor
from components.command_monitor.monitor import CommandMonitor
from components.log_monitor.monitor import LogMonitor
from utils import read_config


async def start_monitors(monitors: list[BaseMonitor]):
    tasks = []
    for monitor in monitors:
        tasks.append(asyncio.create_task(monitor.start_monitoring()))

    await asyncio.gather(*tasks)


def run_monitors(config_path: str, es: AsyncElasticsearch):
    configs = read_config(config_path)
    monitors = []

    for config in configs.log_configs:
        for path in glob.glob(config.path):
            monitors.append(LogMonitor(path, config.events, es))

    for config in configs.cmd_configs:
        for event in config.events:
            monitors.append(CommandMonitor(event, es))
    asyncio.run(start_monitors(monitors))


if __name__ == "__main__":
    # TODO: use proper logging framework
    # TODO: get config vars from argparse, env or file
    config_path = "/workspaces/live-node-monitor/config.yaml"
    es_host = os.getenv("ES_HOST")
    # TODO: How to do basic auth using netrc? does this work out-of-the-box?
    es_username = os.getenv("ES_USERNAME")
    es_password = os.getenv("ES_PASSWORD")
    es = AsyncElasticsearch(
        es_host, basic_auth=(es_username, es_password), verify_certs=False
    )
    run_monitors(config_path, es)
