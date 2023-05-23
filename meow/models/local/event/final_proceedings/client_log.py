from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class ClientLog:
    severity: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def as_dict(self):
        return asdict(self)