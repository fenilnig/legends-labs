from legends_labs.modules.audio_post_production.services.interfaces import IEffectsService
import numpy as np
from typing import List, Dict

try:
    from pedalboard import Pedalboard, Reverb, Compressor, HighpassFilter, LowpassFilter, Gain, Limiter, Distortion
except ImportError:
    Pedalboard = None

class PedalboardEffectsService(IEffectsService):
    def __init__(self):
        self.board = None
        if Pedalboard:
            self.board = Pedalboard([])

    def apply_eq(self, bands: List[Dict[str, float]]) -> None:
        if not self.board: return
        # Simple mapping for demonstration; a true parametric EQ would use PeakingFilter etc.
        for band in bands:
            if band.get("type") == "highpass":
                self.board.append(HighpassFilter(cutoff_frequency_hz=band.get("freq", 80)))
            elif band.get("type") == "lowpass":
                self.board.append(LowpassFilter(cutoff_frequency_hz=band.get("freq", 15000)))

    def apply_compression(self, threshold_db: float, ratio: float, attack_ms: float, release_ms: float) -> None:
        if not self.board: return
        self.board.append(Compressor(
            threshold_db=threshold_db,
            ratio=ratio,
            attack_ms=attack_ms,
            release_ms=release_ms
        ))

    def apply_reverb(self, room_size: float, damping: float, wet_level: float, dry_level: float) -> None:
        if not self.board: return
        self.board.append(Reverb(
            room_size=room_size,
            damping=damping,
            wet_level=wet_level,
            dry_level=dry_level
        ))

    def apply_limiter(self, threshold_db: float, release_ms: float) -> None:
        if not self.board: return
        self.board.append(Limiter(
            threshold_db=threshold_db,
            release_ms=release_ms
        ))
        
    def reset_chain(self):
        if self.board:
            self.board = Pedalboard([])

    def process_chain(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.board or len(audio_data) == 0:
            return audio_data
        
        try:
            # Pedalboard expects (channels, samples) shape
            if len(audio_data.shape) == 1:
                audio_data = audio_data.reshape(1, -1)
            else:
                audio_data = audio_data.T
                
            processed = self.board(audio_data, sample_rate)
            return processed.T if processed.shape[0] > 1 else processed.reshape(-1)
        except Exception as e:
            print(f"Pedalboard processing error: {e}")
            return audio_data
