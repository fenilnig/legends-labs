import os
from PySide6.QtCore import QObject
from legends_labs.core.task_queue import BaseWorker
from legends_labs.modules.audio_editor import effects

class EditorWorker(BaseWorker):
    def __init__(self, operation: str, audio_path: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.audio_path = audio_path
        self.kwargs = kwargs

    def run(self):
        self.signals.started.emit()
        self.signals.progress.emit(10, f"Starting {self.operation}...")
        
        # Output to a temporary or updated file
        filename, ext = os.path.splitext(self.audio_path)
        output_path = f"{filename}_edited{ext}"
        
        try:
            if self.operation == "normalize":
                self.signals.progress.emit(50, "Normalizing audio...")
                effects.apply_normalize(self.audio_path, output_path, target_dbfs=self.kwargs.get("target_dbfs", -3.0))
            
            elif self.operation == "trim":
                self.signals.progress.emit(50, "Trimming audio...")
                effects.apply_trim(self.audio_path, output_path, self.kwargs.get("start_ms", 0), self.kwargs.get("end_ms", 0))
                
            elif self.operation == "fade":
                self.signals.progress.emit(50, "Applying fade...")
                effects.apply_fade(self.audio_path, output_path, self.kwargs.get("fade_in_ms", 0), self.kwargs.get("fade_out_ms", 0))
                
            elif self.operation == "compression":
                self.signals.progress.emit(50, "Compressing dynamic range...")
                effects.apply_compression(self.audio_path, output_path, self.kwargs.get("threshold", -20.0), self.kwargs.get("ratio", 4.0))
                
            else:
                self.signals.error.emit("Editor Error", f"Unknown operation: {self.operation}")
                self.signals.finished.emit()
                return

            self.signals.progress.emit(100, f"Successfully applied {self.operation}.")
            self.signals.result.emit(output_path)
            
        except Exception as e:
            self.signals.error.emit("Editor Error", str(e))
            
        self.signals.finished.emit()
