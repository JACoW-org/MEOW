import logging

from jpsp.tasks.infra.abstract_task import AbstractTask
from jpsp.tasks.local.xml_download import XmlDownloadTask
from jpsp.tasks.local.xml_exec import ExecProcessTask
from jpsp.tasks.local.xml_merge import XmlMergeTask
from jpsp.tasks.local.xml_split import XmlSplitTask

# from jpsp.tasks.repo.xml_merge import XmlMergeTask
# from jpsp.tasks.repo.xml_split import XmlSplitTask

logger = logging.getLogger(__name__)


class TaskRepository:
    """ """

    __tasks = dict(
        xml_download=XmlDownloadTask,
        exec_process=ExecProcessTask,
        exec_merge=XmlMergeTask,
        exec_split=XmlSplitTask
    )

    @classmethod
    async def get_task(cls, code: str) -> type[AbstractTask]:
        """ """

        if code in cls.__tasks:
            task = cls.__tasks[code]
            return task

        logger.error(f"Invalid Task Code {code}")

        raise RuntimeError(f"Invalid Task Code {code}")
