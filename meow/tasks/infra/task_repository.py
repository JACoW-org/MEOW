import logging as lg

from meow.tasks.infra.abstract_task import AbstractTask

from meow.tasks.local.event_ab import EventAbstractBookletTask
from meow.tasks.local.event_pc import EventPapersCheckTask
from meow.tasks.local.event_dr import EventDoiReferenceTask
from meow.tasks.local.event_pp import EventPrePressTask
from meow.tasks.local.event_fp import EventFinalProceedingsTask


logger = lg.getLogger(__name__)


class TaskRepository:
    """ """

    __tasks = dict(
        event_ab=EventAbstractBookletTask,
        event_pc=EventPapersCheckTask,
        event_dr=EventDoiReferenceTask,
        event_pp=EventPrePressTask,
        event_fp=EventFinalProceedingsTask,
    )

    @classmethod
    async def get_task(cls, code: str) -> type[AbstractTask]:
        """ """

        if code in cls.__tasks:
            task = cls.__tasks[code]
            return task

        logger.error(f"Invalid Task Code {code}")

        raise RuntimeError(f"Invalid Task Code {code}")
