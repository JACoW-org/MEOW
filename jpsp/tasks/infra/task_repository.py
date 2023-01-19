import logging as lg

from jpsp.tasks.infra.abstract_task import AbstractTask
from jpsp.tasks.local.check_pdf import CheckPdfTask
from jpsp.tasks.local.event_ab import EventAbTask
from jpsp.tasks.local.event_pdf import EventPdfTask
from jpsp.tasks.local.event_zip import EventZipTask

# from jpsp.tasks.local.event_put import EventPutTask
# from jpsp.tasks.local.xml_download import XmlDownloadTask
# from jpsp.tasks.local.xml_exec import ExecProcessTask
# from jpsp.tasks.local.xml_merge import XmlMergeTask
# from jpsp.tasks.local.xml_split import XmlSplitTask


logger = lg.getLogger(__name__)


class TaskRepository:
    """ """

    __tasks = dict(
        event_ab=EventAbTask,
        check_pdf=CheckPdfTask,
        event_zip=EventZipTask,
        event_pdf=EventPdfTask,
        
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
