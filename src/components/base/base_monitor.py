class BaseMonitor:
    def __init__(self) -> None:
        pass

    async def start_monitoring(self) -> None:
        raise NotImplementedError()

    def stop_monitoring(self) -> None:
        raise NotImplementedError()
