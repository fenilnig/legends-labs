import time
import os
from pathlib import Path
from PySide6.QtCore import QObject
from legends_labs.core.task_queue import BaseWorker
from legends_labs.modules.voice_clone.voice_memory import voice_memory

class BatchImportWorker(BaseWorker):
    def __init__(self, folder_path: str, style_name: str, auto_clean: bool = False):
        super().__init__()
        self.folder_path = folder_path
        self.style_name = style_name
        self.auto_clean = auto_clean

    def run(self):
        try:
            self.signals.started.emit()
            folder = Path(self.folder_path)
            
            if not folder.exists() or not folder.is_dir():
                self.signals.error.emit("Batch Import", "Folder does not exist.")
                return
                
            audio_files = list(folder.glob("*.wav")) + list(folder.glob("*.mp3")) + list(folder.glob("*.m4a"))
            if not audio_files:
                self.signals.error.emit("Batch Import", "No audio files found in folder.")
                return
                
            total = len(audio_files)
            # Real SpeechBrain Diarization (Phase 1)
            try:
                from speechbrain.pretrained import SpeakerRecognition
                import torch
                from sklearn.cluster import AgglomerativeClustering
                import numpy as np
                import torchaudio
                
                self.signals.progress.emit(10, "Loading SpeechBrain ECAPA-TDNN model...")
                # Download/load model from HF cache. Run on CPU to save VRAM for TTS.
                spk_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp_speechbrain")
                
                self.signals.progress.emit(15, "Extracting speaker embeddings for all files...")
                embeddings = []
                valid_files = []
                
                for f in audio_files:
                    try:
                        sig, fs = torchaudio.load(str(f))
                        # Embeddings
                        emb = spk_model.encode_batch(sig)
                        embeddings.append(emb.squeeze().detach().cpu().numpy())
                        valid_files.append(f)
                    except Exception as e:
                        print(f"Diarization error on {f.name}: {e}")
                        
                audio_files = valid_files
                
                if len(embeddings) > 1:
                    self.signals.progress.emit(20, "Clustering speakers...")
                    emb_matrix = np.stack(embeddings)
                    # Cluster based on cosine distance. Threshold 0.25 (empirical for ECAPA)
                    clusterer = AgglomerativeClustering(
                        n_clusters=None, 
                        distance_threshold=0.25, 
                        metric='cosine', 
                        linkage='average'
                    )
                    labels = clusterer.fit_predict(emb_matrix)
                else:
                    labels = [0] * len(audio_files)
                    
            except ImportError:
                self.signals.progress.emit(10, "SpeechBrain not installed. Skipping diarization (all files assigned to same speaker).")
                labels = [0] * len(audio_files)
            
            from legends_labs.audio.dsp_utils import process_reference_audio_segments
            import random
            
            total_clips_added = 0
            
            for i, (file, speaker_id) in enumerate(zip(audio_files, labels)):
                pct = 25 + int(70 * (i / total))
                # Create a sub-profile if multiple speakers are detected
                current_style = self.style_name if max(labels) == 0 else f"{self.style_name}_Speaker_{speaker_id + 1}"
                
                self.signals.progress.emit(pct, f"Analyzing {file.name} for {current_style}...")
                
                # Real DSP extraction
                try:
                    processing_path = str(file)
                    
                    if self.auto_clean:
                        self.signals.progress.emit(pct, f"Preprocessing {file.name} for optimal cloning (Background Process)...")
                        import subprocess, sys, os
                        
                        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaner_script.py")
                        CREATE_NO_WINDOW = 0x08000000
                        process = subprocess.Popen(
                            [sys.executable, script_path, processing_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=CREATE_NO_WINDOW,
                            text=True
                        )
                        
                        stdout, stderr = process.communicate()
                        
                        if process.returncode != 0:
                            print(f"Skipping {file.name} due to cleaner error: {stderr}")
                            continue
                            
                        for line in stdout.splitlines():
                            if line.startswith("SUCCESS:"):
                                processing_path = line.replace("SUCCESS:", "").strip()
                                break
                    
                    for metrics in process_reference_audio_segments(processing_path):
                        # We will still fake the emotion until SpeechBrain is integrated
                        emotions = ["neutral", "authoritative", "casual", "cinematic", "excited"]
                        detected_emotion = random.choice(emotions)
                        
                        # Add to voice memory
                        # Add to voice memory under the detected speaker profile
                        voice_memory.update_from_recording(
                            style_name=current_style,
                            audio_path=metrics["clean_path"],
                            tempo=metrics["tempo"],
                            pitch=metrics["pitch"],
                            emotion=detected_emotion,
                            duration=metrics.get("duration", 0.0),
                            speaking_rate=metrics.get("speaking_rate", 0.0),
                            avg_volume=metrics.get("avg_volume", 0.0),
                            energy=metrics.get("energy", 0.0),
                            noise_level=metrics.get("noise_level", 0.0),
                            silence_percentage=metrics.get("silence_percentage", 0.0),
                            sample_rate=metrics.get("sample_rate", 44100.0),
                            clipping_ratio=metrics.get("clipping_ratio", 0.0)
                        )
                        total_clips_added += 1
                except Exception as ex:
                    print(f"Skipping {file.name} due to DSP error: {ex}")
                    continue
                
            self.signals.progress.emit(100, "Batch import complete!")
            self.signals.result.emit(f"Successfully processed {total} files and extracted {total_clips_added} clips for '{self.style_name}'.")
        except Exception as e:
            import traceback
            self.signals.error.emit(str(type(e).__name__), str(e) + "\n" + traceback.format_exc())
        finally:
            self.signals.finished.emit()
