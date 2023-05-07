
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.services.local.event.event_pdf_utils import read_report
from meow.services.local.event.event_pdf_utils import extract_event_pdf_files, is_to_download

from meow.services.local.event.final_proceedings.collecting_contributions_and_files import collecting_contributions_and_files
from meow.services.local.event.final_proceedings.collecting_sessions_and_attachments import collecting_sessions_and_attachments
from meow.services.local.event.final_proceedings.read_papers_report import read_papers_report
from meow.services.local.event.final_proceedings.validate_proceedings_data import validate_proceedings_data
from meow.services.local.event.final_proceedings.create_final_proceedings import create_final_proceedings
from meow.services.local.event.final_proceedings.download_contributions_papers import download_contributions_papers


from meow.utils.http import download_file

logger = lg.getLogger(__name__)


async def event_pdf_check(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:
            async for r in _event_pdf_check(event, cookies, settings, lock):
                yield r

    except LockError as e:
        logger.error(e, exc_info=True)
        raise e
    except BaseException as e:
        logger.error(e, exc_info=True)
        raise e


def acquire_lock(key: str) -> RedisLock:
    """ Create event lock """

    return RedisLock(
        redis=dbs.redis_client,
        name=conf.REDIS_EVENT_LOCK_KEY(key),
        timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
        sleep=0.5,
        blocking=True,
        blocking_timeout=conf.REDIS_LOCK_BLOCKING_TIMEOUT_SECONDS,
        thread_local=True,
    )


async def extend_lock(lock: RedisLock) -> RedisLock:
    """ Reset lock timeout (conf.REDIS_LOCK_TIMEOUT_SECONDS) """

    await lock.reacquire()
    return lock


async def _event_pdf_check(event: dict, cookies: dict, settings: dict, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_final_proceedings - create_final_proceedings')

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_sessions_and_attachments',
        text="Collecting sessions and attachments"
    ))

    [sessions, attachments] = await collecting_sessions_and_attachments(event, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_contributions_and_files',
        text="Collecting contributions and files"
    ))

    [contributions] = await collecting_contributions_and_files(event, sessions, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='adapting_final_proceedings',
        text="Adapting final proceedings"
    ))

    final_proceedings = await create_final_proceedings(event, sessions, contributions, attachments, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))

    final_proceedings = await download_contributions_papers(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='read_papers_report',
        text='Read Papers Report'
    ))

    final_proceedings = await read_papers_report(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='validate_contributions_papers',
        text='Validate Contributions Papers'
    ))
    
    def callback(c: ContributionData) -> bool:
        return c.is_qa_approved or c.is_qa_pending

    [metadata, errors] = await validate_proceedings_data(final_proceedings, cookies, settings, callback)

    yield dict(type='result', value=dict(
        metadata=metadata,
        errors=errors
    ))


async def __event_pdf_check(event: dict, cookies: dict, settings: dict, lock: RedisLock):
    """ """

    # logger.debug(f'event_pdf_check - count: {len(contributions)} - cookies: {cookies}')

    event_id = event.get('id', 'event')

    pdf_cache_dir: Path = Path('var', 'run', f"{event_id}_pdf")
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    files = await extract_event_pdf_files(event)

    total_files: int = len(files)
    checked_files: int = 0

    logger.info(f'event_pdf_check - files: {len(files)}')

    send_stream, receive_stream = create_memory_object_stream()

    capacity_limiter = CapacityLimiter(4)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files):
                tg.start_soon(pdf_check_task, capacity_limiter, total_files, current_index,
                              current_file, cookies, pdf_cache_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for report in receive_stream:
                    checked_files = checked_files + 1

                    # print('receive_reports_stream::report-->',
                    #       checked_files, total_files, report)

                    yield dict(
                        type='progress',
                        value=report
                    )

                    await extend_lock(lock)

                    if checked_files >= total_files:
                        receive_stream.close()

                        yield dict(
                            type='result',
                            value=None
                        )

        except ClosedResourceError:
            pass


async def pdf_check_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: dict,
                         cookies: dict, pdf_cache_dir: Path, res: MemoryObjectSendStream):
    """ """

    async with capacity_limiter:
        report = await internal_pdf_check_task(current_file, cookies, pdf_cache_dir)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "report": report
        })


async def internal_pdf_check_task(current_file: dict, cookies: dict, pdf_cache_dir: Path):
    """ """

    pdf_md5 = current_file.get('md5sum', '')
    pdf_name = current_file.get('filename', '')
    http_sess = cookies.get('indico_session_http', '')
    pdf_url = current_file.get('external_download_url', '')

    pdf_file = Path(pdf_cache_dir, pdf_name)

    logger.debug(f"{pdf_md5} {pdf_name}")

    if await is_to_download(pdf_file, pdf_md5):
        cookies = dict(indico_session_http=http_sess)
        await download_file(url=pdf_url, file=pdf_file, cookies=cookies)

    # EXTERNAL PROCESS
    return await read_report(str(await pdf_file.absolute()))
