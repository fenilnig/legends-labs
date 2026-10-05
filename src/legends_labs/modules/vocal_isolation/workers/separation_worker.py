from typing import List, Dict
import sys
import re
import os
from PySide6.QtCore import Slot
import traceback
from legends_labs.core.task_queue import BaseWorker

class TqdmRedirector:
    def __init__(self, progress_signal, base_val=30, max_val=90):
        self.progress_signal = progress_signal
        self.base_val = base_val
        self.max_val = max_val
        self.original_stderr = sys.stderr
        
    def write(self, buf):
        match = re.search(r"(\d+)%\|", buf)
        if match:
            pct = int(match.group(1))
            val = self.base_val + int((pct / 100.0) * (self.max_val - self.base_val))
            self.progress_signal.emit(val, "Separating stems...")
        # Optional: uncomment to still see in console
        # self.original_stderr.write(buf)
        
    def flush(self):
        pass

class SeparationWorker(BaseWorker):
    def __init__(self, audio_path: str, model_name: str, stems: List[str], segment_size: int, output_dir: str):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name
        self.stems = stems
        self.segment_size = segment_size
        self.output_dir = output_dir

    @Slot()
    def run(self):
        old_stderr = sys.stderr
        try:
            sys.stderr = TqdmRedirector(self.signals.progress)
            self.signals.started.emit()
            self.signals.progress.emit(10, "Initializing model...")
            
            # Use audio-separator library
            try:
                import logging
                from audio_separator.separator import Separator
                separator = Separator(
                    log_level=logging.WARNING,
                    output_dir=self.output_dir,
                    use_autocast=True, # Significantly speeds up inference on modern hardware
                    demucs_params={'segment_size': 'Default', 'shifts': 0, 'overlap': 0.1, 'segments_enabled': True},
                    mdxc_params={'segment_size': 256, 'override_model_segment_size': False, 'batch_size': 1, 'overlap': 2, 'pitch_shift': 0}
                )
                
                # Setup specific model
                if self.model_name == "BS-RoFormer":
                    separator.load_model('BS-RoFormer-Viperx-1297.onnx')
                else:
                    separator.load_model('htdemucs.yaml')
                    
                # Fix m4a format issue by converting to wav first if needed
                if self.audio_path.lower().endswith(".m4a"):
                    self.signals.progress.emit(20, "Converting audio format...")
                    from pydub import AudioSegment
                    wav_path = self.audio_path.rsplit('.', 1)[0] + '.wav'
                    if not os.path.exists(wav_path):
                        audio = AudioSegment.from_file(self.audio_path, format="m4a")
                        audio.export(wav_path, format="wav")
                    self.audio_path = wav_path
                    
                self.signals.progress.emit(30, "Separating stems...")
                
                output_files = separator.separate(self.audio_path)
                
                self.signals.progress.emit(90, "Finalizing output...")
                
                result = {}
                for stem in self.stems:
                    for f in output_files:
                        if stem.lower() in f.lower():
                            full_path = os.path.abspath(os.path.join(self.output_dir, os.path.basename(f)))
                            result[stem] = full_path
                            break
                            
                self.signals.result.emit(result)
                self.signals.progress.emit(100, "Done")
                
            except ImportError:
                self.signals.error.emit("Import Error", "audio-separator library not found.")
            
        except Exception as e:
            self.signals.error.emit(str(e), traceback.format_exc())
        finally:
            sys.stderr = old_stderr
            self.signals.finished.emit()
