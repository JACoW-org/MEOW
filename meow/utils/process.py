from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import Optional
from anyio import open_process, run_process
from anyio.streams.text import TextReceiveStream
import logging as lg

logger = lg.getLogger(__name__)


@dataclass(kw_only=True)
class ProcessResult:
    pid: int
    exit: Optional[int]
    stdout: Optional[str] = None
    stderr: Optional[str] = None


async def execute_process(args: list[str], cwd: str | None = None) -> ProcessResult:
    result: ProcessResult

    async with await open_process(command=args, cwd=cwd) as process:

        await process.wait()

        result = ProcessResult(pid=process.pid, exit=process.returncode)

        if process.stdout:
            async for text in TextReceiveStream(process.stdout):
                result.stdout = text

        if process.stderr:
            async for text in TextReceiveStream(process.stderr):
                result.stderr = text

    return result


async def run_cmd(cmd: list[str], cwd: str | None = None):

    try:
        print(" ".join(cmd))

        result = await run_process(cmd, cwd=cwd, start_new_session=True)

        print(result.returncode)
        print(result.stdout.decode())
        print(result.stderr.decode())

    except CalledProcessError as err:
        logger.error(err, exc_info=True)
