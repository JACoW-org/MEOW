from dataclasses import dataclass
from subprocess import CalledProcessError, CompletedProcess
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


async def run_cmd(command: list[str]) -> CompletedProcess[bytes] | None:

    result: CompletedProcess[bytes] | None = None

    try:

        # logger.info(" ".join(cmd))

        result = await run_process(command=command, check=True, start_new_session=True)

        # print(result.returncode)
        # print(result.stdout.decode())
        # print(result.stderr.decode())
        
        return result

    except CalledProcessError as err:
        
        if err:
            print(" ".join(command))
            print(err.returncode)
            print(err.stdout.decode())
            print(err.stderr.decode())
        
        logger.error(err, exc_info=True)
