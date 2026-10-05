from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class IAudioService(ABC):
    """Interface for basic audio editing operations (trim, split, merge, fade)."""
    @abstractmethod
    def load_audio(self, file_path: str) -> bool:
        pass
        
    @abstractmethod
    def save_audio(self, output_path: str, format: str = "wav") -> bool:
        pass
        
    @abstractmethod
    def trim(self, start_ms: float, end_ms: float) -> None:
        pass
        
    @abstractmethod
    def apply_fade(self, fade_in_ms: float, fade_out_ms: float) -> None:
        pass
        
    @abstractmethod
    def get_waveform_data(self, max_points: int = 1000) -> np.ndarray:
        pass

class IEffectsService(ABC):
    """Interface for applying professional real-time effects (EQ, Compression, Reverb, etc.)."""
    @abstractmethod
    def apply_eq(self, bands: List[Dict[str, float]]) -> None:
        pass
        
    @abstractmethod
    def apply_compression(self, threshold_db: float, ratio: float, attack_ms: float, release_ms: float) -> None:
        pass
        
    @abstractmethod
    def apply_reverb(self, room_size: float, damping: float, wet_level: float, dry_level: float) -> None:
        pass
        
    @abstractmethod
    def apply_limiter(self, threshold_db: float, release_ms: float) -> None:
        pass
        
    @abstractmethod
    def process_chain(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Processes the audio through the entire configured effects chain."""
        pass

class IAnalysisService(ABC):
    """Interface for audio analysis (Spectrogram, FFT, Loudness)."""
    @abstractmethod
    def compute_spectrogram(self, audio_path: str) -> np.ndarray:
        pass
        
    @abstractmethod
    def compute_lufs(self, audio_path: str) -> float:
        pass
        
    @abstractmethod
    def detect_clipping(self, audio_path: str) -> List[float]:
        """Returns a list of timestamps where clipping occurs."""
        pass

class IVocalIsolationService(ABC):
    """Interface for AI stem separation."""
    @abstractmethod
    def separate_stems(self, audio_path: str, stems: List[str], model: str, output_dir: str) -> Dict[str, str]:
        """Returns a dictionary mapping stem name to saved file path."""
        pass

class ICleanupService(ABC):
    """Interface for AI noise reduction and cleanup."""
    @abstractmethod
    def reduce_background_noise(self, audio_path: str, intensity: float, output_path: str) -> str:
        pass
        
    @abstractmethod
    def remove_clicks_pops(self, audio_path: str, output_path: str) -> str:
        pass
