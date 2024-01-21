from elasticsearch import AsyncElasticsearch
from model import Target, TargetType


class BaseMonitor:
    def __init__(self, es: AsyncElasticsearch) -> None:
        self.es = es

    async def start_monitoring(self) -> None:
        raise NotImplementedError()

    def stop_monitoring(self) -> None:
        raise NotImplementedError()

    async def _save_data(self, data: dict, targets: list[Target]):
        for target in targets:
            if target.name == TargetType.ELASTICSEARCH:
                response = await self._save_data_es(data, target.config)
                print(response)

    async def _save_data_es(self, data: dict, config: dict):
        # TODO: sending documents individually or sending them in bulk?
        # Can the mechanism be rebuilt to use https://elasticsearch-py.readthedocs.io/en/v8.12.0/async.html#bulk-and-streaming-bulk
        return await self.es.index(index=config["index"], document=data)
