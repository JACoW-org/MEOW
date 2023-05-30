from asyncio import Task

tasks: list[Task] = []


def add(task: Task) -> None:
    tasks.append(task)


def get() -> list[Task]:
    return tasks


async def close_all() -> None:
    for task in get():
        task.cancel()
