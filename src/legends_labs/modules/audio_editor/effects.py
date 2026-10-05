import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

def apply_normalize(audio_path: str, output_path: str, target_dbfs: float = -3.0):
    """Normalize audio to a target dBFS."""
    audio = AudioSegment.from_file(audio_path)
    normalized = normalize(audio)
    
    # Adjust to target if needed (pydub's normalize brings peak to 0dBFS by default)
    change_in_dbfs = target_dbfs - normalized.max_dBFS
    normalized = normalized.apply_gain(change_in_dbfs)
    
    normalized.export(output_path, format="wav")
    return output_path

def apply_trim(audio_path: str, output_path: str, start_ms: int, end_ms: int):
    """Trim audio to a specific start and end time (in milliseconds)."""
    audio = AudioSegment.from_file(audio_path)
    trimmed = audio[start_ms:end_ms]
    trimmed.export(output_path, format="wav")
    return output_path

def apply_fade(audio_path: str, output_path: str, fade_in_ms: int = 0, fade_out_ms: int = 0):
    """Apply fade in and/or fade out."""
    audio = AudioSegment.from_file(audio_path)
    if fade_in_ms > 0:
        audio = audio.fade_in(fade_in_ms)
    if fade_out_ms > 0:
        audio = audio.fade_out(fade_out_ms)
    audio.export(output_path, format="wav")
    return output_path

def apply_compression(audio_path: str, output_path: str, threshold: float = -20.0, ratio: float = 4.0):
    """Apply dynamic range compression."""
    audio = AudioSegment.from_file(audio_path)
    compressed = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
    compressed.export(output_path, format="wav")
    return output_path
