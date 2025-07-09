import logging as lg
from contextvars import ContextVar


event_id_var: ContextVar[str] = ContextVar("event_id", default="-")


class ContextFilter(lg.Filter):
    def filter(self, record):
        record.event_id = event_id_var.get()
        return True


def initLogger(level):
    """ """

    logger = lg.getLogger()
    logger.setLevel(level)

    handler = lg.StreamHandler()
    formatter = lg.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [event_id=%(event_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())  # <— qui aggiungi il filtro

    logger.addHandler(handler)
