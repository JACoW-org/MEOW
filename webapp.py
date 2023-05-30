import meow.app.factory as factory
import logging as lg
import os

os.environ['CLIENT_TYPE'] = 'webapp'

lg.basicConfig(level=lg.INFO)

app = factory.build()

# async def app_pre():
#     import os
#     os.environ['CLIENT_TYPE'] = 'webapp'
#
#     from anyio import to_thread, to_process
#     to_thread.current_default_thread_limiter().total_tokens = 8
#     to_process.current_default_process_limiter().total_tokens = 8
#
# async def app_post():
#     from meow.app.instances.services import srs
#     await srs.redis_manager.destroy()
#
# async def main() -> None:
#     logger.debug('meow - begin')
#
#     # await app_pre()
#
#     async with create_task_group() as tg:
#         from meow.app.instances.services import srs
#         tg.start_soon(srs.webapp_manager.run)
#         # tg.start_soon(srs.socket_manager.run)
#
#     # await app_post()
#
#     logger.debug('meow - end')
#
#
# if __name__ == "__main__":
#     run(main, backend='asyncio', backend_options={'use_uvloop': True})
