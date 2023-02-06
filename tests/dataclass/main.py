from dataclasses import dataclass

from pprint import pprint

@dataclass
class Mission:
    year: int
    name: str


@dataclass
class Astronaut:
    firstname: str
    lastname: str
    missions: list[Mission]


async def main():

    astro = Astronaut('Mark', 'Watney', missions=[
        Mission(1973, 'Apollo 18'),
        Mission(2012, 'STS-136'),
        Mission(2035, 'Ares 3')])

    pprint(astro)
