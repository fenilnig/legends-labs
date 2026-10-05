import asyncio
import torch
from typing import AsyncGenerator
from .base import TTSEngine

class XTTSEngine(TTSEngine):
    def __init__(self):
        self.tts = None
        
    def load(self) -> None:
        if self.tts is not None:
            return
            
        try:
            import os
            os.environ["COQUI_TOS_AGREED"] = "1"
            from TTS.api import TTS
        except Exception as e:
            raise RuntimeError(f"Missing XTTS dependencies: {e}")
            
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
    def unload(self) -> None:
        if self.tts:
            del self.tts
            self.tts = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
    async def generate(self, text: str, reference_audio: str, output_path: str) -> AsyncGenerator[dict, None]:
        yield {"progress": 10, "message": "Analyzing semantic prompt..."}
        
        from legends_labs.core.prompt_parser import PromptParser
        metadata, clean_text = PromptParser.parse_script(text)
        params = PromptParser.map_to_xtts_params(metadata)
        
        yield {"progress": 20, "message": "Loading XTTS model..."}
        
        await asyncio.to_thread(self.load)
        
        yield {"progress": 40, "message": "Synthesizing AI voice..."}
        
        def _run_tts():
            # Pass speed and emotion natively to XTTS if supported
            tts_kwargs = {
                "text": clean_text,
                "speaker_wav": reference_audio,
                "language": "en",
                "file_path": output_path,
                "speed": params["speed"]
            }
            if params["emotion"]:
                tts_kwargs["emotion"] = params["emotion"]
                
            print(f"[DEBUG XTTS] Model: XTTS v2 | speaker_wav: {reference_audio}")
            self.tts.tts_to_file(**tts_kwargs)
            
        await asyncio.to_thread(_run_tts)
        
        # Apply post-processing DSP if needed
        if params["pitch_shift"] != 0.0 or params["volume_db"] != 0.0:
            yield {"progress": 85, "message": "Applying acoustic DSP transformations..."}
            
            def _apply_dsp():
                import soundfile as sf
                from legends_labs.audio.dsp_utils import apply_pitch_shift, apply_gain
                
                audio, sr = sf.read(output_path)
                if params["pitch_shift"] != 0.0:
                    audio = apply_pitch_shift(audio, sr, params["pitch_shift"])
                if params["volume_db"] != 0.0:
                    audio = apply_gain(audio, params["volume_db"])
                    
                sf.write(output_path, audio, sr)
                
            await asyncio.to_thread(_apply_dsp)
        
        yield {"progress": 100, "message": "Generation complete."}
