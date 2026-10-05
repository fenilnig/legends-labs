import time
import random
from pathlib import Path
from PySide6.QtCore import QObject
from legends_labs.core.task_queue import BaseWorker
from legends_labs.modules.voice_clone.voice_memory import voice_memory

class PerformanceAnalyzerWorker(BaseWorker):
    def __init__(self, audio_path: str, style_name: str, auto_clean: bool = False, transcript: str = None):
        super().__init__()
        self.audio_path = audio_path
        self.style_name = style_name
        self.auto_clean = auto_clean
        self.transcript = transcript

    def run(self):
        try:
            self.signals.started.emit()
            
            processing_path = self.audio_path
            
            if self.auto_clean:
                self.signals.progress.emit(2, "Isolating vocals and enhancing (Background Process)...")
                import subprocess, sys, os
                
                # We spawn the cleaner script in a totally separate python process so it doesn't block the UI's GIL!
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaner_script.py")
                
                CREATE_NO_WINDOW = 0x08000000
                process = subprocess.Popen(
                    [sys.executable, script_path, processing_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=CREATE_NO_WINDOW,
                    text=True
                )
                
                # Wait for process to finish
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    self.signals.error.emit("Cleaner Failed", f"Background process crashed:\n{stderr}")
                    return
                    
                # Parse stdout for the SUCCESS tag
                for line in stdout.splitlines():
                    if line.startswith("SUCCESS:"):
                        processing_path = line.replace("SUCCESS:", "").strip()
                        break
            
            self.signals.progress.emit(10, "Extracting true Voice DNA with librosa...")
            
            from legends_labs.audio.dsp_utils import process_reference_audio_segments
            from legends_labs.audio.forced_alignment import get_word_timestamps
            from legends_labs.audio.phoneme_extractor import extract_ipa_from_audio
            from legends_labs.modules.voice_clone.pronunciation_db import pronunciation_db
            
            # Ensure tables exist
            pronunciation_db.init_db()
            
            emotions = ["neutral", "authoritative", "casual", "cinematic", "excited"]
            count = 0
            
            for metrics in process_reference_audio_segments(processing_path):
                count += 1
                self.signals.progress.emit(min(90, count * 5), f"Processing segment {count}...")
                
                # Assign a random/simulated emotion per chunk
                detected_emotion = random.choice(emotions)
                
                voice_memory.update_from_recording(
                    style_name=self.style_name,
                    audio_path=metrics["clean_path"],
                    tempo=metrics["tempo"],
                    pitch=metrics["pitch"],
                    emotion=detected_emotion,
                    transcript=self.transcript,
                    duration=metrics.get("duration", 0.0),
                    speaking_rate=metrics.get("speaking_rate", 0.0),
                    avg_volume=metrics.get("avg_volume", 0.0),
                    energy=metrics.get("energy", 0.0),
                    noise_level=metrics.get("noise_level", 0.0),
                    silence_percentage=metrics.get("silence_percentage", 0.0),
                    sample_rate=metrics.get("sample_rate", 44100.0),
                    clipping_ratio=metrics.get("clipping_ratio", 0.0)
                )
                
                # AI Pronunciation Learning System Integration
                # Extract word-level timestamps for the current short audio segment
                try:
                    words_data = get_word_timestamps(metrics["clean_path"])
                    for w in words_data:
                        spelling = w["word"]
                        start_time = w["start"]
                        end_time = w["end"]
                        prob = w["probability"]
                        
                        # Only learn if confidence is reasonably high and word is somewhat long
                        if prob > 0.6 and len(spelling) >= 2:
                            ipa = extract_ipa_from_audio(metrics["clean_path"], start_time, end_time)
                            
                            if ipa:
                                # Save to knowledge base
                                word_id = pronunciation_db.add_word(spelling)
                                variant_id = pronunciation_db.add_variant(
                                    word_id=word_id,
                                    phonetic=spelling, # Fallback, AI phonetic transcription is complex without LLM
                                    ipa=ipa,
                                    syllables="",
                                    stress=""
                                )
                                pronunciation_db.add_occurrence(
                                    variant_id=variant_id,
                                    style_name=self.style_name,
                                    audio_path=metrics["clean_path"],
                                    start_time=start_time,
                                    end_time=end_time,
                                    confidence=prob,
                                    emotion=detected_emotion,
                                    context=""
                                )
                except Exception as e:
                    print(f"Failed to extract pronunciation for segment: {e}")
                    
            self.signals.progress.emit(100, "Voice profile updated.")
            self.signals.result.emit(f"Style '{self.style_name}' evolved with {count} new clips!")
        except Exception as e:
            import traceback
            self.signals.error.emit(str(type(e).__name__), str(e) + "\n" + traceback.format_exc())
        finally:
            self.signals.finished.emit()
