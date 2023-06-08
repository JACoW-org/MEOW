
from abc import ABC, abstractmethod

import io

from anyio import Path

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
    async def ssg_cmd(self) -> Path:
        pass


