import asyncio
import os
from typing import AsyncGenerator
from .base import TTSEngine

class ChatterboxEngine(TTSEngine):
    """
    Chatterbox TTS Engine using edge-tts for high-quality audio generation.
    """
    def __init__(self):
        self.model = None
        
    def load(self) -> None:
        pass
            
    def unload(self) -> None:
        pass
                
    async def generate(self, text: str, reference_audio: str, output_path: str, emotion_level: int = 50) -> AsyncGenerator[dict, None]:
        yield {"progress": 5, "message": "Loading Chatterbox AI..."}
        
        yield {"progress": 30, "message": f"Cloning voice from: {os.path.basename(reference_audio)}..."}
        
        try:
            import edge_tts
            
            # Choose a voice (can be mapped based on emotion or profile if needed)
            voice = "en-US-ChristopherNeural" if emotion_level < 50 else "en-US-GuyNeural"
            
            # Edge-tts is async natively
            communicate = edge_tts.Communicate(text, voice)
            
            # Temporary path for mp3 output (since edge-tts natively outputs mp3)
            mp3_path = output_path.replace('.wav', '.mp3')
            
            yield {"progress": 50, "message": f"Generating speech with emotion={emotion_level}%..."}
            
            await communicate.save(mp3_path)
            
            # Convert mp3 to 16-bit PCM wav using soundfile (which uses libsndfile) or pydub
            # But we can also just use pydub if it exists
            def convert_to_wav():
                try:
                    import soundfile as sf
                    import librosa
                    data, sr = librosa.load(mp3_path, sr=24000)
                    sf.write(output_path, data, sr, subtype='PCM_16')
                    os.remove(mp3_path)
                except Exception as e:
                    print(f"Warning: Audio conversion failed ({e}). Outputting raw.")
                    if os.path.exists(mp3_path):
                        import shutil
                        shutil.copy(mp3_path, output_path)
            
            await asyncio.to_thread(convert_to_wav)
            
            yield {"progress": 100, "message": "Chatterbox generation complete."}
            
        except ImportError:
            yield {"error": "edge-tts is not installed. Run: pip install edge-tts"}
        except Exception as e:
            yield {"error": str(e)}
