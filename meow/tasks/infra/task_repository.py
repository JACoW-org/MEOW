import logging as lg

from meow.tasks.infra.abstract_task import AbstractTask
from meow.tasks.local.check_pdf import CheckPdfTask
from meow.tasks.local.event_ab import EventAbTask
from meow.tasks.local.event_pdf import EventPdfTask
from meow.tasks.local.event_ref import EventRefTask
from meow.tasks.local.event_zip import EventZipTask

# from meow.tasks.local.event_put import EventPutTask
# from meow.tasks.local.xml_download import XmlDownloadTask
# from meow.tasks.local.xml_exec import ExecProcessTask
# from meow.tasks.local.xml_merge import XmlMergeTask
# from meow.tasks.local.xml_split import XmlSplitTask


logger = lg.getLogger(__name__)


class TaskRepository:
    """ """

    __tasks = dict(
        event_ab=EventAbTask,
        check_pdf=CheckPdfTask,
        event_zip=EventZipTask,
        event_pdf=EventPdfTask,
        event_ref=EventRefTask,
        
        # event_put=EventPutTask,
        # xml_exec=ExecProcessTask,
        # xml_download=XmlDownloadTask,
        # xml_merge=XmlMergeTask,
        # xml_split=XmlSplitTask
    )

    @classmethod
    async def get_task(cls, code: str) -> type[AbstractTask]:
        """ """

        if code in cls.__tasks:
            task = cls.__tasks[code]
            return task

        logger.error(f"Invalid Task Code {code}")

        raise RuntimeError(f"Invalid Task Code {code}")
