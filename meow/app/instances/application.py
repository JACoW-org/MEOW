
from dataclasses import dataclass, field

from starlette.websockets import WebSocket

""" """




@dataclass()
class __Instances:
    """ """

    @dataclass
    class __State:
        """ """

        webapp_running: bool = False
        worker_running: bool = False
        
    state: __State = field(default_factory=__State)
    
    active_connections: dict[str, WebSocket] = field(default_factory=dict)


app = __Instances()
