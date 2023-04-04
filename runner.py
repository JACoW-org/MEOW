import json
import sys
import io

from anyio import run
from anyio import open_process, run_process
from anyio.streams.text import TextReceiveStream
from anyio import create_task_group, run, CapacityLimiter
from anyio import create_task_group, create_memory_object_stream, run

INPUT = {"method": "report", "params": {"input": "var/run/18_pdf/MOBI3.pdf"}}


def split_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i+chunk_size]
        
        
async def main_stdin() -> None:

    args = ["venv/bin/python3", "command.py", "-"]

    chunk_size = int(100000 / 8) + 1 
    all_inputs = [INPUT for i in range(100000)]
    
    limiter = CapacityLimiter(8)

    async with create_task_group() as tg:

        async def task(inputs, limiter):
            async with limiter:
                stdin = io.BytesIO()

                for input in inputs:
                    stdin.write(f"{json.dumps(input)}\n".encode('utf-8'))

                res = await run_process(command=args, input=stdin.getvalue())
                # print(res.stdout.decode())

        for chunk in split_list(all_inputs, chunk_size):
            tg.start_soon(task, chunk, limiter)


async def main_loop() -> None:

    args = ["venv/bin/python3", "command.py", "-"]

    limiter = CapacityLimiter(8)

    async with create_task_group() as tg:

        for i in range(1000):

            async def task(limiter):
                async with limiter:
                    stdin = io.StringIO(f"{json.dumps(INPUT)}\n").getvalue()
                    res = await run_process(command=args, input=stdin.encode('utf-8'))
                    # print(res.stdout.decode())

            tg.start_soon(task, limiter)


if __name__ == "__main__":
    run(main_stdin)
