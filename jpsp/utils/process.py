from dataclasses import dataclass
from typing import Optional
from anyio import open_process
from anyio.streams.text import TextReceiveStream

@dataclass(kw_only=True)
class ProcessResult:
    pid:int
    exit:Optional[int]
    stdout:Optional[str] = None
    stderr:Optional[str] = None

async def execute_process(args: list[str]) -> ProcessResult:
    result: ProcessResult

    async with await open_process(command=args) as process:

        await process.wait()
        
        result = ProcessResult(pid=process.pid, exit=process.returncode)

        if process.stdout:
            async for text in TextReceiveStream(process.stdout):
                result.stdout = text

        if process.stderr:
            async for text in TextReceiveStream(process.stderr):
                result.stderr = text

    return result
