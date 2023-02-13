from typing import Any

# https://www.youtube.com/watch?v=s_4ZrtQs8Do


controllers = {

}


async def build(code: str, params: Any):
    return controllers[code]
