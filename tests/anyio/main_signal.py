import signal

from anyio import open_signal_receiver, run


async def main():
    with open_signal_receiver(signal.SIGTERM, signal.SIGHUP) as signals:
        async for signum in signals:
            if signum == signal.SIGTERM:
                print('finished!')
                return
            elif signum == signal.SIGHUP:
                print('Reloading configuration')


run(main)
