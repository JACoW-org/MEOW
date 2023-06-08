from dataclasses import dataclass, field, asdict

@dataclass
class BasicAuthData:
    login: str = field()
    password: str = field()

    def as_dict(self):
        return asdict(self)

