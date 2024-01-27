import asyncio

from elasticsearch import AsyncElasticsearch
from components.base.base_monitor import BaseMonitor

from model import CmdMonitorEvent


class CommandMonitor(BaseMonitor):
    def __init__(self, event: CmdMonitorEvent, es: AsyncElasticsearch) -> None:
        super().__init__(es)
        self.event = event

    async def start_monitoring(self) -> None:
        while True:
            await self._execute_command()
            if self.event.repeat is None:
                return
            else:
                await asyncio.sleep(self.event.repeat)

    def stop_monitoring(self) -> None:
        # TODO: stop monitoring
        pass

    async def _execute_command(self) -> None:
        command = self.event.command
        if self.event.chdir is not None:
            command = f"cd {self.event.chdir} && {self.event.command}"

        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        print(f"[{command!r} exited with {proc.returncode}]")
        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

        data = self.event.model_dump(exclude={"targets"})
        data.update(
            {"stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}
        )
        await self._save_data(data, self.event.targets)
        return
