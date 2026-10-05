import os
from typing import List, Dict
from faster_whisper import WhisperModel

# Lazy loading of model to save memory until needed
_whisper_model = None

def _get_model():
    global _whisper_model
    if _whisper_model is None:
        print("Loading faster-whisper model for ASR and Forced Alignment...")
        # Use 'base.en' for English-only with good accuracy and fast speed
        # If CUDA is available, faster-whisper uses it automatically if configured, otherwise CPU
        try:
            _whisper_model = WhisperModel("base.en", device="cuda", compute_type="float16")
        except Exception:
            # Fallback to CPU if CUDA fails
            print("Falling back to CPU for Whisper.")
            _whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return _whisper_model

def get_word_timestamps(audio_path: str) -> List[Dict[str, any]]:
    """
    Transcribes the audio file and returns a list of words with their exact start and end timestamps.
    Returns:
        List of dicts: {"word": str, "start": float, "end": float, "probability": float}
    """
    model = _get_model()
    
    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language="en"
    )
    
    words_data = []
    for segment in segments:
        for word in segment.words:
            # Clean up the word text (whisper often includes leading/trailing spaces or punctuation)
            clean_word = word.word.strip().lower()
            # Strip basic punctuation
            for p in ".,!?;:\"'()[]{}":
                clean_word = clean_word.replace(p, "")
                
            if clean_word:
                words_data.append({
                    "word": clean_word,
                    "start": word.start,
                    "end": word.end,
                    "probability": word.probability
                })
                
    return words_data
