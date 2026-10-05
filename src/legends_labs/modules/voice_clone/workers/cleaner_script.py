import sys
import os
import logging

def clean_audio(audio_path):
    # Ensure CACHE_DIR is available
    from legends_labs.core.constants import CACHE_DIR
    
    try:
        # Inject FFmpeg into PATH if it was installed via Winget while the app was running
        ffmpeg_path = r"C:\Users\fenil\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"
        if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_path
            
        # 1. Isolate vocals (DISABLED for XTTS)
        # We explicitly bypass Demucs because XTTS is highly sensitive to the phase 
        # issues and spectral artifacts introduced by vocal isolation models.
        # Cloning from pristine audio yields drastically better similarity.
        import time
        vocal_path = os.path.join(str(CACHE_DIR), f"pristine_clone_{int(time.time())}.wav")
        raw_audio_path = audio_path
            
        # 2. Advanced Preprocessing Pipeline (Phase 1)
        import librosa
        import soundfile as sf
        import numpy as np
        
        print("Loading audio with librosa...", flush=True)
        # Load the raw audio
        y, sr = librosa.load(raw_audio_path, sr=24000)
        print("Audio loaded successfully.", flush=True)
        
        # A. Clipping Repair (Cubic Spline Interpolation)
        # Detect clipped samples (usually at -1.0 or 1.0, or very close)
        threshold = 0.99
        clipped_indices = np.where(np.abs(y) >= threshold)[0]
        if len(clipped_indices) > 0:
            print("Repairing clipping...", flush=True)
            import scipy.interpolate
            # Create boolean mask of valid (non-clipped) samples
            valid_mask = np.abs(y) < threshold
            valid_indices = np.where(valid_mask)[0]
            if len(valid_indices) > 0:
                # Interpolate the clipped values based on valid neighbors
                interpolator = scipy.interpolate.CubicSpline(valid_indices, y[valid_indices])
                y[clipped_indices] = interpolator(clipped_indices)
                
        # B. Silence Trimming
        # Trim leading/trailing silence below 30db
        print("Trimming silence...", flush=True)
        y_trimmed, _ = librosa.effects.trim(y, top_db=30)
        
        # C. Loudness Normalization (ITU-R BS.1770-4 via pyloudnorm)
        print("Normalizing loudness...", flush=True)
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr) # create BS.1770 meter
            loudness = meter.integrated_loudness(y_trimmed)
            # Normalize to broadcast standard -23 LUFS
            y_norm = pyln.normalize.loudness(y_trimmed, loudness, -23.0)
        except ImportError:
            # Fallback to simple peak normalization if pyloudnorm isn't installed yet
            print("pyloudnorm not found, using peak normalization...", flush=True)
            peak = np.max(np.abs(y_trimmed))
            y_norm = y_trimmed / peak * 0.9 if peak > 0 else y_trimmed

        # Overwrite the vocal path with the cleaned version
        sf.write(vocal_path, y_norm, sr, subtype='PCM_16')
            
        # Print the final path so the parent process can read it from stdout
        print(f"SUCCESS:{vocal_path}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    clean_audio(sys.argv[1])
