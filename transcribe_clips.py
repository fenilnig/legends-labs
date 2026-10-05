import os
import sys
import sqlite3
from pathlib import Path
from faster_whisper import WhisperModel

def main():
    db_path = Path.home() / ".legends-labs" / "default.llproj"
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return

    print("Loading faster-whisper model...")
    model = WhisperModel("small", device="cuda" if "cuda" in sys.argv else "cpu", compute_type="float16" if "cuda" in sys.argv else "int8")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT audio_path FROM reference_clips WHERE transcript IS NULL OR transcript = ''")
    rows = cur.fetchall()
    
    if not rows:
        print("No clips missing transcripts.")
        return
        
    print(f"Found {len(rows)} clips missing transcripts. Starting transcription...")
    
    for row in rows:
        audio_path = row[0]
        if not os.path.exists(audio_path):
            print(f"File not found: {audio_path}")
            continue
            
        print(f"Transcribing: {os.path.basename(audio_path)}")
        segments, info = model.transcribe(audio_path, beam_size=5)
        transcript = " ".join([segment.text for segment in segments]).strip()
        
        print(f"  -> {transcript}")
        
        cur.execute("UPDATE reference_clips SET transcript = ? WHERE audio_path = ?", (transcript, audio_path))
        conn.commit()

    conn.close()
    print("Done! Transcripts updated.")

if __name__ == "__main__":
    main()
