
from jpsp.app.instances.databases import dbs
from jpsp.utils.serialization import json_encode


class TaskResponse:
    """ """

    def __init__(self):
        pass

    async def send(self, event: str, body: dict) -> None:
        """ """

        message = json_encode(
            dict(event=event, body=body)
        )

        await dbs.redis_client.publish("jpsp:feed", message)

    async def close(self) -> None:
        """ """

        pass
