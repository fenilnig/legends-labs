import asyncio
import numpy as np
import soundfile as sf
from typing import AsyncGenerator
from .base import TTSEngine

class MockEngine(TTSEngine):
    def load(self) -> None:
        pass
        
    def unload(self) -> None:
        pass
        
    async def generate(self, text: str, reference_audio: str, output_path: str) -> AsyncGenerator[dict, None]:
        yield {"progress": 10, "message": "Loading Mock Engine..."}
        await asyncio.sleep(0.5)
        
        yield {"progress": 50, "message": "Synthesizing test audio..."}
        await asyncio.sleep(0.5)
        
        # Generate 1 second of 440Hz sine wave (beep)
        sr = 44100
        t = np.linspace(0, 1, sr, False)
        data = np.sin(2 * np.pi * 440 * t) * 0.5
        sf.write(output_path, data, sr, subtype='PCM_16')
        
        yield {"progress": 100, "message": "Generation complete."}
