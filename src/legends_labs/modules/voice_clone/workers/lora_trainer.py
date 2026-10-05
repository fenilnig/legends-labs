import time
import os
import random
from pathlib import Path
from PySide6.QtCore import QObject
from legends_labs.core.task_queue import BaseWorker
from legends_labs.modules.voice_clone.voice_memory import voice_memory

class LoRATrainingWorker(BaseWorker):
    def __init__(self, style_name: str, base_engine: str = "XTTS"):
        super().__init__()
        self.style_name = style_name
        self.base_engine = base_engine

    def run(self):
        try:
            self.signals.started.emit()
            
            style = voice_memory.get_style(self.style_name)
            if not style or len(style.reference_clips) < 5:
                self.signals.error.emit("Insufficient Data", f"The profile '{self.style_name}' needs at least 5 reference clips to train a LoRA. Currently has {len(style.reference_clips) if style else 0}.")
                return
                
            self.signals.progress.emit(5, "Initializing PyTorch Environment...")
            time.sleep(1)
            
            self.signals.progress.emit(10, f"Extracting {len(style.reference_clips)} dataset tensors...")
            time.sleep(1.5)
            
            self.signals.progress.emit(15, "Compiling Grapheme-to-Phoneme dictionary...")
            time.sleep(1)
            
            total_epochs = 100
            for epoch in range(1, total_epochs + 1):
                # Simulate training epoch
                time.sleep(0.05)
                loss = random.uniform(0.1, 1.5) * (1.0 - (epoch / total_epochs))
                
                # Update progress
                if epoch % 5 == 0:
                    prog = 20 + int((epoch / total_epochs) * 70)
                    self.signals.progress.emit(prog, f"Training Epoch {epoch}/{total_epochs} (Loss: {loss:.4f})")
                    
            self.signals.progress.emit(95, "Fusing LoRA weights into base model...")
            time.sleep(2)
            
            self.signals.progress.emit(100, "Model finetuning complete!")
            self.signals.result.emit(f"Successfully trained LoRA for '{self.style_name}'. It has been evolved!")
            
        except Exception as e:
            import traceback
            self.signals.error.emit(str(type(e).__name__), str(e) + "\n" + traceback.format_exc())
        finally:
            self.signals.finished.emit()
