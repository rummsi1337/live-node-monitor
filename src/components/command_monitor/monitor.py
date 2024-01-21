import asyncio

from elasticsearch import AsyncElasticsearch
from components.base.base_monitor import BaseMonitor

from model import CmdMonitorEvent


class CommandMonitor(BaseMonitor):
    def __init__(self, event: CmdMonitorEvent, es: AsyncElasticsearch) -> None:
        super().__init__(es)
        self.event = event

    async def start_monitoring(self):
        while True:
            await self._execute_command()
            if self.event.repeat is None:
                return
            else:
                await asyncio.sleep(self.event.repeat)

    def stop_monitoring(self) -> None:
        # TODO: stop monitoring
        pass

    async def _execute_command(self):
        command = self.event.command
        if self.event.chdir is not None:
            # TODO: make sure that the chdir exists before executing command! use Pathlib
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
        # TODO: parse and send the result of the command
        # TODO: handle errors when executing a command
        return stdout
