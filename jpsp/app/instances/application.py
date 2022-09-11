
from typing import List
from dataclasses import dataclass, field

from starlette.websockets import WebSocket

""" """




@dataclass()
class __Instances:
    """ """

    @dataclass
    class __State:
        """ """

        running: bool = False
        
    state: __State = __State()
    
    active_connections: List[WebSocket] = field(default_factory=lambda: [])


app = __Instances()
