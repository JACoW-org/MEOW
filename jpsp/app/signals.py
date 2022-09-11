import signal

from anyio import open_signal_receiver

from jpsp.models.infra.locks import RedisLockList
from jpsp.utils.http import HttpClientSessions


async def create_signal_handler():
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM, signal.SIGHUP) as signals:
        async for signum in signals:
            if signum == signal.SIGTERM:
                print('>>>> Terminated!')
            elif signum == signal.SIGHUP:
                print('Reloading configuration')
            elif signum == signal.SIGINT:
                print('>>>>> Ctrl+C pressed!')

            await HttpClientSessions.close_client_sessions()
            await RedisLockList.release_all_locks()

            return
