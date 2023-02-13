from uvicorn.workers import UvicornWorker


class AppUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio", "http": "h11", "lifespan": "on"}
