import os
import tempfile
import numpy as np
import soundfile as sf

# Lazy load
_recognizer = None

def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        print("Loading allosaurus phoneme recognizer...")
        from allosaurus.app import read_recognizer
        _recognizer = read_recognizer()
    return _recognizer

def extract_ipa_from_audio(audio_path: str, start_time: float, end_time: float) -> str:
    """
    Extracts the IPA pronunciation from a specific slice of the audio file.
    """
    # Load the specific slice
    # soundfile supports frames, so we convert time to frames
    info = sf.info(audio_path)
    sr = info.samplerate
    start_frame = int(start_time * sr)
    end_frame = int(end_time * sr)
    
    # Ensure bounds
    if start_frame < 0: start_frame = 0
    if end_frame > info.frames: end_frame = info.frames
    
    if start_frame >= end_frame:
        return ""
        
    y, _ = sf.read(audio_path, start=start_frame, stop=end_frame)
    
    # Allosaurus requires a file path (or a specific wav structure), so we use a temp file
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav.close()
    
    try:
        sf.write(temp_wav.name, y, sr)
        
        recognizer = _get_recognizer()
        ipa_string = recognizer.recognize(temp_wav.name, 'eng')
        
        return ipa_string
    finally:
        if os.path.exists(temp_wav.name):
            os.remove(temp_wav.name)
