import abc
from typing import AsyncGenerator

class TTSEngine(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None:
        """Load the model into memory/VRAM."""
        pass
        
    @abc.abstractmethod
    def unload(self) -> None:
        """Unload the model and free VRAM."""
        pass
        
    @abc.abstractmethod
    async def generate(self, text: str, reference_audio: str, output_path: str, **kwargs) -> AsyncGenerator[dict, None]:
        """
        Generate audio and yield progress events.
        Yields dicts like: {"progress": int, "message": str}
        """
        pass
