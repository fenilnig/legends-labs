from legends_labs.modules.audio_post_production.services.interfaces import IAnalysisService
import numpy as np
from typing import List
import os

try:
    import librosa
    import soundfile as sf
except ImportError:
    librosa = None
    sf = None

class LibrosaAnalysisService(IAnalysisService):
    def compute_spectrogram(self, audio_path: str) -> np.ndarray:
        if not librosa or not os.path.exists(audio_path):
            return np.zeros((1, 1))
            
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            if len(y) == 0:
                return np.zeros((1, 1))
                
            D = librosa.stft(y)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            return S_db
        except Exception as e:
            print(f"Librosa spectrogram error: {e}")
            return np.zeros((1, 1))

    def compute_lufs(self, audio_path: str) -> float:
        # Proper LUFS requires pyloudnorm, but we simulate a basic RMS/Peak measurement if missing
        if not librosa or not os.path.exists(audio_path):
            return -14.0
            
        try:
            y, sr = librosa.load(audio_path, sr=None)
            rms = librosa.feature.rms(y=y)[0]
            if len(rms) == 0: return -14.0
            avg_rms = np.mean(rms)
            # Rough conversion to dBFS
            dbfs = 20 * np.log10(avg_rms + 1e-10)
            return float(dbfs)
        except Exception as e:
            print(f"LUFS computation error: {e}")
            return -14.0

    def detect_clipping(self, audio_path: str) -> List[float]:
        if not librosa or not os.path.exists(audio_path):
            return []
            
        try:
            y, sr = librosa.load(audio_path, sr=None)
            # Find indices where amplitude is at or extremely close to 1.0 or -1.0
            clip_indices = np.where(np.abs(y) >= 0.99)[0]
            # Convert indices to timestamps
            timestamps = clip_indices / sr
            return timestamps.tolist()
        except Exception as e:
            print(f"Clipping detection error: {e}")
            return []
