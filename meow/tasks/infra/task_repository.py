import logging as lg

from meow.tasks.infra.abstract_task import AbstractTask

from meow.tasks.local.event_abstract_booklet import EventAbstractBookletTask
from meow.tasks.local.event_compress_proceedings import EventCompressProceedingsTask
from meow.tasks.local.event_doi_delete import EventDoiDeleteTask
from meow.tasks.local.event_doi_draft import EventDoiDraftTask
from meow.tasks.local.event_doi_hide import EventDoiHideTask
from meow.tasks.local.event_doi_info import EventDoiInfoTask
from meow.tasks.local.event_doi_publish import EventDoiPublishTask
from meow.tasks.local.event_papers_check import EventPapersCheckTask
from meow.tasks.local.event_pre_press_proceedings import EventPrePressProceedingsTask
from meow.tasks.local.event_final_proceedings import EventFinalProceedingsTask


logger = lg.getLogger(__name__)


class TaskRepository:
    """ """

    __tasks = dict(
        event_abstract_booklet=EventAbstractBookletTask,
        event_papers_check=EventPapersCheckTask,
        event_pre_press=EventPrePressProceedingsTask,
        event_final_proceedings=EventFinalProceedingsTask,
        event_compress_proceedings=EventCompressProceedingsTask,
        event_doi_draft=EventDoiDraftTask,
        event_doi_delete=EventDoiDeleteTask,
        event_doi_publish=EventDoiPublishTask,
        event_doi_hide=EventDoiHideTask,
        event_doi_info=EventDoiInfoTask,
    )

    @classmethod
    async def get_task(cls, code: str) -> type[AbstractTask]:
        """ """

        if code in cls.__tasks:
            task = cls.__tasks[code]
            return task

        logger.error(f"Invalid Task Code {code}")

        raise RuntimeError(f"Invalid Task Code {code}")
