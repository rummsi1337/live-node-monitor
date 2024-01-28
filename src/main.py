import asyncio
import glob
import logging
import os

import click
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


def setup_logging(level: str):
    format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    logging.basicConfig(format=format, level=logging.DEBUG)


@click.command()
@click.option("--config", prompt=True, help="Path to the config.yaml")
@click.option("--verbose", "-v", is_flag=True, help="Print debug output")
def main(config: str, verbose: bool):
    setup_logging(logging.DEBUG if verbose else logging.INFO)
    # # TODO: use proper logging framework
    # # TODO: get config vars from argparse, env or file
    es_host = os.getenv("ES_HOST")
    # TODO: How to do basic auth using netrc? does this work out-of-the-box?
    es_username = os.getenv("ES_USERNAME")
    es_password = os.getenv("ES_PASSWORD")
    es = AsyncElasticsearch(
        es_host, basic_auth=(es_username, es_password), verify_certs=False
    )
    run_monitors(config, es)


if __name__ == "__main__":
    main()
