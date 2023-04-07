
from abc import ABC, abstractmethod

import io

from anyio import Path
from anyio import run_process
from anyio.streams.file import FileReadStream

class AbstractFinalProceedingsPlugin(ABC):
    
    @abstractmethod
    async def prepare(self):
        pass
    
    @abstractmethod
    async def render_home(self):
        pass

    @abstractmethod
    async def render_session(self):
        pass
    
    @abstractmethod
    async def render_classification(self):
        pass
    
    @abstractmethod
    async def render_author(self):
        pass
    
    @abstractmethod
    async def render_institute(self):
        pass
    
    @abstractmethod
    async def render_doi_per_institute(self):
        pass
    
    @abstractmethod
    async def render_keyword(self):
        pass    
    
    @abstractmethod
    async def finalize(self):
        pass
    
    @abstractmethod
    async def generate(self) -> None:
        pass
    
    @abstractmethod
    async def compress(self) -> io.BytesIO:
        pass
    
    @abstractmethod
    async def clean(self) -> None:
        pass
    
    @abstractmethod
    async def ssg_cmd(self) -> Path:
        pass
    
    async def zip_cmd(self) -> Path:
        return await Path('bin', '7zzs').absolute()
    
    async def get_zip(self, file: Path) -> io.BytesIO:       

        b = io.BytesIO()

        async with await FileReadStream.from_path(file) as s:
            async for c in s:
                b.write(c)

        b.seek(0)

        return b
