import os
from elasticsearch import AsyncElasticsearch
from components.log_monitor.monitor import run_log_monitor


if __name__ == "__main__":
    # TODO: use proper logging framework
    # TODO: get config vars from argparse, env or file
    config_path = "/workspaces/live-node-monitor/log_monitor_config.yaml"
    es_host = os.getenv("ES_HOST")
    # TODO: How to do basic auth using netrc? does this work out-of-the-box?
    es_username = os.getenv("ES_USERNAME")
    es_password = os.getenv("ES_PASSWORD")
    es = AsyncElasticsearch(
        es_host, basic_auth=(es_username, es_password), verify_certs=False
    )
    run_log_monitor(config_path, es)
