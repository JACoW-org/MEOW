import asyncio
import functools
import logging

from typing import Any, Optional, TypeVar, Tuple

T = TypeVar('T')


def cancel_task(task: asyncio.Task, logger: logging.Logger, ):
    try:
        if task and isinstance(task, asyncio.Task):
            task.cancel()
        else:
            logger.error("Invalid Task")
    except Exception:  # pylint: disable=broad-except
        logger.exception("cancel_task")
    return None


def create_task(
        coro: Any,
        *,
        name: str,
        logger: logging.Logger,
        message: str,
        message_args: Tuple[Any, ...] = (),
        loop: Optional[asyncio.AbstractEventLoop] = None,
) -> 'asyncio.Task':
    """
    This helper function wraps a ``loop.create_task(coroutine())`` call and ensures there is
    an exception handler added to the resulting task. If the task raises an exception it is logged
    using the provided ``logger``, with additional context provided by ``message`` and optionally
    ``message_args``.
    """
    if not loop:
        loop = asyncio.get_running_loop()
    task = loop.create_task(name=name, coro=coro)
    task.add_done_callback(
        functools.partial(_handle_task_result, logger=logger,
                          message=message, message_args=message_args)
    )
    return task


def _handle_task_result(
        task: asyncio.Task,
        *,
        logger: logging.Logger,
        message: str,
        message_args: Tuple[Any, ...] = (),
) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    # Ad the pylint ignore: we want to handle all exceptions here so that the result of the task
    # is properly logged. There is no point re-raising the exception in this callback.
    except Exception:  # pylint: disable=broad-except
        logger.exception(message, *message_args)
