from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

class ClientLogSeverity(Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

@dataclass
class ClientLog:
    severity: ClientLogSeverity
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def as_dict(self):
        log_dict = asdict(self)
        log_dict['severity'] = self.severity.value
        return log_dict