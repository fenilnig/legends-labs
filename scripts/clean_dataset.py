import os
import sys
import glob
import soundfile as sf
import pyloudnorm as pyln
from pydub import AudioSegment
from pydub.silence import split_on_silence
import whisper
import warnings
import numpy as np
from tqdm import tqdm

warnings.filterwarnings("ignore")

INPUT_DIR = r"H:\legends-labs\Historical_Recordings"
OUTPUT_DIR = r"H:\legends-labs\dataset_clean"
TARGET_SR = 44100
MIN_DURATION = 1.5   # seconds
MAX_DURATION = 20.0  # seconds
TARGET_LUFS = -23.0

def load_audio(path):
    try:
        audio = AudioSegment.from_file(path)
        audio = audio.set_frame_rate(TARGET_SR).set_channels(1)
        return audio
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def normalize_loudness(samples, sr):
    meter = pyln.Meter(sr)
    try:
        loudness = meter.integrated_loudness(samples)
        normalized = pyln.normalize.loudness(samples, loudness, TARGET_LUFS)
        return normalized
    except Exception as e:
        return samples

def export_audio(chunk, out_path_base, formats):
    samples = np.array(chunk.get_array_of_samples(), dtype=np.float32) / 32768.0
    
    samples_norm = normalize_loudness(samples, TARGET_SR)
    
    wav_path = f"{out_path_base}.wav"
    sf.write(wav_path, samples_norm, TARGET_SR, subtype="PCM_16")
    
    norm_audio = AudioSegment.from_wav(wav_path)
    
    if "flac" in formats:
        norm_audio.export(f"{out_path_base}.flac", format="flac")
    if "mp3" in formats:
        norm_audio.export(f"{out_path_base}.mp3", format="mp3", bitrate="192k")
    if "m4a" in formats:
        norm_audio.export(f"{out_path_base}.m4a", format="ipod", codec="aac")
        
    return wav_path

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory not found: {INPUT_DIR}")
        return

    formats = ["flac", "mp3", "m4a"]
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "wavs"), exist_ok=True)
    for fmt in formats:
        os.makedirs(os.path.join(OUTPUT_DIR, fmt), exist_ok=True)

    print("Loading Whisper model (base)...")
    # Using 'base' model to quickly transcribe the chunks.
    # It balances good accuracy with fast inference time.
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("base", device=device)

    audio_files = glob.glob(os.path.join(INPUT_DIR, "*.*"))
    audio_files = [f for f in audio_files if f.endswith(('.m4a', '.wav', '.mp3', '.flac'))]
    
    if not audio_files:
        print(f"No audio files found in {INPUT_DIR}")
        return

    print(f"Found {len(audio_files)} files to process.")
    
    metadata_csv_path = os.path.join(OUTPUT_DIR, "metadata.csv")
    metadata_file = open(metadata_csv_path, "w", encoding="utf-8")
    
    chunk_counter = 0

    for file_path in audio_files:
        print(f"\nProcessing: {os.path.basename(file_path)}")
        audio = load_audio(file_path)
        if audio is None:
            continue
            
        print("  Splitting into chunks based on silence...")
        chunks = split_on_silence(
            audio,
            min_silence_len=500,     
            silence_thresh=audio.dBFS-14,
            keep_silence=250         
        )
        
        print(f"  Generated {len(chunks)} potential chunks.")
        
        for i, chunk in enumerate(tqdm(chunks, desc="  Transcribing and Exporting")):
            duration = len(chunk) / 1000.0
            
            if duration < MIN_DURATION or duration > MAX_DURATION:
                continue
                
            out_name = f"chunk_{chunk_counter:04d}"
            
            wav_path = os.path.join(OUTPUT_DIR, "wavs", out_name)
            out_base_paths = {}
            for fmt in formats:
                out_base_paths[fmt] = os.path.join(OUTPUT_DIR, fmt, out_name)
                
            export_audio(chunk, wav_path, formats)
            
            for fmt in formats:
                os.rename(f"{wav_path}.{fmt}", f"{out_base_paths[fmt]}.{fmt}")
                
            real_wav_path = f"{wav_path}.wav"
            
            # Use fp16 only if cuda is available
            fp16 = torch.cuda.is_available()
            result = model.transcribe(real_wav_path, fp16=fp16)
            text = result["text"].strip()
            
            if not text:
                os.remove(real_wav_path)
                for fmt in formats:
                    os.remove(f"{out_base_paths[fmt]}.{fmt}")
                continue
                
            lab_path = f"{wav_path}.lab"
            with open(lab_path, "w", encoding="utf-8") as f:
                f.write(text)
                
            metadata_file.write(f"{out_name}|{text}\n")
            
            chunk_counter += 1

    metadata_file.close()
    print(f"\nDone! Cleaned dataset with {chunk_counter} valid chunks saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
