from dataclasses import dataclass
from anyio import open_file, run, Path

# from tests.pikepdf.main_report import main
# from tests.hugo.generate import main


@dataclass
class Mission:
    year: int
    name: str


@dataclass
class Astronaut:
    firstname: str
    lastname: str
    missions: list[Mission]
    
astro = Astronaut('Mark', 'Watney', missions=[
    Mission(1973, 'Apollo 18'),
    Mission(2012, 'STS-136'),
    Mission(2035, 'Ares 3')])


async def main():
    
    lock_file = Path('/tmp/lock')
    
    lock_file.touch
    
    async with await open_file('/tmp/lock') as f:
        
        async for line in f:
            print(line, end='')
            

if __name__ == '__main__':
    print(astro)
    run(main)
