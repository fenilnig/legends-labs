import os
from legends_labs.core.task_queue import BaseWorker

class EnhanceWorker(BaseWorker):
    def __init__(self, audio_path: str, strength: int, clarity_boost: bool, dereverb: bool):
        super().__init__()
        self.audio_path = audio_path
        self.strength = strength
        self.clarity_boost = clarity_boost
        self.dereverb = dereverb

    def run(self):
        self.signals.started.emit()
        self.signals.progress.emit(10, "Loading DeepFilterNet model...")
        
        try:
            from df.enhance import enhance, init_df, load_audio, save_audio
            # Initialize DeepFilterNet (downloads model to cache if first run)
            model, df_state, _ = init_df()
            
            self.signals.progress.emit(40, "Processing audio...")
            audio, _ = load_audio(self.audio_path, sr=df_state.sr())
            
            # Atten_lim specifies attenuation limit in dB
            enhanced = enhance(model, df_state, audio, atten_lim_db=100.0)
            
            self.signals.progress.emit(80, "Saving enhanced audio...")
            filename, ext = os.path.splitext(self.audio_path)
            output_path = f"{filename}_enhanced{ext}"
            save_audio(output_path, enhanced, df_state.sr())
            
            self.signals.progress.emit(100, "Enhancement complete.")
            self.signals.result.emit(output_path)
            
        except Exception as e:
            self.signals.error.emit(str(type(e).__name__), str(e))
            
        self.signals.finished.emit()
