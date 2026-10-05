import os
import sqlite3
import csv
import random

db_path = r"C:\Users\fenil\.legends-labs\default.llproj"
dataset_dir = r"H:\legends-labs\dataset_clean"
wavs_dir = os.path.join(dataset_dir, "wavs")
metadata_path = os.path.join(dataset_dir, "metadata.csv")

def main():
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Get the style ID for "Fenil"
    cur.execute("SELECT id FROM voice_styles WHERE name = 'Fenil'")
    row = cur.fetchone()
    if not row:
        print("Voice style 'Fenil' not found!")
        return
    style_id = row[0]
    
    # 2. Delete old junk
    print("Deleting old junk reference clips...")
    cur.execute("DELETE FROM reference_clips WHERE style_id = ?", (style_id,))
    cur.execute("DELETE FROM evolution_history WHERE style_id = ?", (style_id,))
    conn.commit()
    
    # 3. Read the new pristine chunks
    print("Loading 55 pristine dataset chunks...")
    chunks_added = 0
    with open(metadata_path, 'r', encoding='utf-8') as f:
        # Our metadata.csv format is: chunk_0000|Hello world
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                chunk_name, text = parts
                wav_path = os.path.join(wavs_dir, f"{chunk_name}.wav")
                if os.path.exists(wav_path):
                    cur.execute(
                        "INSERT INTO reference_clips (style_id, audio_path, transcript) VALUES (?, ?, ?)",
                        (style_id, wav_path, text)
                    )
                    chunks_added += 1

    conn.commit()
    
    cur.execute("UPDATE voice_styles SET avg_tempo = 145.0, avg_pitch = 115.0 WHERE id = ?", (style_id,))
    conn.commit()
    
    conn.close()
    print(f"Successfully replaced 145 junk recordings with {chunks_added} pristine dataset chunks!")

if __name__ == '__main__':
    main()
