from legends_labs.modules.audio_post_production.services.interfaces import IAudioService
import numpy as np
import os
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

class PydubAudioService(IAudioService):
    def __init__(self):
        self.audio: AudioSegment = None
        self.current_path: str = ""

    def load_audio(self, file_path: str) -> bool:
        if not AudioSegment or not os.path.exists(file_path):
            return False
        try:
            self.audio = AudioSegment.from_file(file_path)
            self.current_path = file_path
            return True
        except Exception as e:
            print(f"Pydub loading error: {e}")
            return False

    def save_audio(self, output_path: str, format: str = "wav") -> bool:
        if not self.audio:
            return False
        try:
            self.audio.export(output_path, format=format)
            return True
        except Exception as e:
            print(f"Pydub saving error: {e}")
            return False

    def trim(self, start_ms: float, end_ms: float) -> None:
        if self.audio:
            self.audio = self.audio[start_ms:end_ms]

    def apply_fade(self, fade_in_ms: float, fade_out_ms: float) -> None:
        if self.audio:
            if fade_in_ms > 0:
                self.audio = self.audio.fade_in(int(fade_in_ms))
            if fade_out_ms > 0:
                self.audio = self.audio.fade_out(int(fade_out_ms))

    def get_waveform_data(self, max_points: int = 1000) -> np.ndarray:
        if not self.audio:
            return np.zeros(max_points)
        
        # Extract raw audio data
        samples = np.array(self.audio.get_array_of_samples())
        
        # If stereo, just take one channel for visualization
        if self.audio.channels == 2:
            samples = samples[::2]
            
        if len(samples) == 0:
            return np.zeros(max_points)
            
        # Downsample for visualization
        if len(samples) > max_points:
            chunk_size = len(samples) // max_points
            samples = samples[:chunk_size * max_points].reshape(-1, chunk_size).mean(axis=1)
            
        return samples
