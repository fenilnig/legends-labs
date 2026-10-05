import librosa
import numpy as np
import soundfile as sf
import os
import time
from pathlib import Path
from legends_labs.core.constants import DATA_DIR

from pydub import AudioSegment
from pydub.silence import split_on_silence

def process_reference_audio_segments(audio_path: str):
    """
    Analyzes a reference audio clip, splitting it into natural speaking segments.
    Yields a dict containing:
    - clean_path: Path to the short audio segment
    - pitch: Median fundamental frequency (Hz)
    - tempo: Estimated speaking tempo (BPM)
    """
    clean_dir = DATA_DIR / "clean_references"
    clean_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load the audio with pydub (handles memory far better for large files)
    audio = AudioSegment.from_file(audio_path)
    if audio.channels > 1:
        audio = audio.set_channels(1)
        
    # 2. Split on silence to find natural sentences
    chunks = split_on_silence(
        audio, 
        min_silence_len=700,
        silence_thresh=audio.dBFS - 14,
        keep_silence=250
    )
    
    if not chunks:
        chunks = [audio]
        
    original_name = Path(audio_path).stem
    
    for i, chunk in enumerate(chunks):
        # Skip chunks that are too short - 5 seconds minimum for quality cloning
        # Fish Audio recommends 5-15s segments for optimal voice capture
        if len(chunk) < 5000:
            continue
            
        # Limit chunk to max 15 seconds to prevent librosa.pyin memory exhaustion
        if len(chunk) > 15000:
            chunk = chunk[:15000]
            
        clean_filename = f"{original_name}_seg{i}_{int(time.time()*1000)}.wav"
        clean_path = str(clean_dir / clean_filename)
        chunk.export(clean_path, format="wav")
        
        y, sr = librosa.load(clean_path, sr=None)
        
        f0, _, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C6'),
            sr=sr
        )
        
        valid_f0 = f0[~np.isnan(f0)]
        avg_pitch = float(np.median(valid_f0)) if len(valid_f0) > 0 else 120.0
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        avg_tempo = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        
        duration = float(len(y) / sr)
        rms_energy = np.sqrt(np.mean(y**2))
        avg_volume = float(20 * np.log10(rms_energy + 1e-9))
        energy = float(rms_energy)
        
        # Estimate noise level & silence percentage
        frame_len = int(sr * 0.1) # 100ms frames
        if frame_len > 0 and len(y) >= frame_len:
            frames = [y[i:i+frame_len] for i in range(0, len(y), frame_len)]
            frame_rms = [np.sqrt(np.mean(f**2)) for f in frames]
            frame_db = [20 * np.log10(r + 1e-9) for r in frame_rms]
            sorted_db = sorted(frame_db)
            # Noise level is the average of the quietest 10% frames
            noise_level = float(np.mean(sorted_db[:max(1, len(sorted_db)//10)]))
            # Silence is percentage of frames below -40 dBFS
            silence_percentage = float(sum(1 for db in frame_db if db < -40.0) / max(1, len(frame_db)) * 100.0)
        else:
            noise_level = -60.0
            silence_percentage = 0.0
            
        # Estimate speaking rate using onset envelope peaks (syllables per second)
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
            speaking_rate = float(len(peaks) / max(0.1, duration))
        except Exception:
            speaking_rate = float(avg_tempo / 60.0 * 2.0) # Fallback based on beat tempo
            
        # Estimate clipping ratio (fraction of samples exceeding/matching 0.99 amplitude)
        clipping_ratio = float(np.sum(np.abs(y) >= 0.99) / len(y)) if len(y) > 0 else 0.0
        
        yield {
            "clean_path": clean_path,
            "pitch": avg_pitch,
            "tempo": avg_tempo,
            "duration": duration,
            "speaking_rate": speaking_rate,
            "avg_volume": avg_volume,
            "energy": energy,
            "noise_level": noise_level,
            "silence_percentage": silence_percentage,
            "sample_rate": float(sr),
            "clipping_ratio": clipping_ratio
        }

def apply_pitch_shift(audio_data: np.ndarray, sr: int, n_steps: float) -> np.ndarray:
    """
    Shifts the pitch of the audio by n_steps (semitones).
    """
    return librosa.effects.pitch_shift(audio_data, sr=sr, n_steps=n_steps)

def apply_gain(audio_data: np.ndarray, gain_db: float) -> np.ndarray:
    """
    Applies gain in decibels to the audio array.
    """
    # gain_db = 20 * log10(amplitude_ratio) -> amplitude_ratio = 10 ** (gain_db / 20)
    ratio = 10.0 ** (gain_db / 20.0)
    return audio_data * ratio
