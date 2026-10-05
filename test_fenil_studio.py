import sqlite3
import os
from pathlib import Path
from faster_whisper import WhisperModel

def main():
    print('Loading model...')
    model = WhisperModel('small', device='cpu', compute_type='int8')
    conn = sqlite3.connect(os.path.expanduser('~/.legends-labs/default.llproj'))
    cur = conn.cursor()
    cur.execute("SELECT r.audio_path FROM voice_styles s JOIN reference_clips r ON s.id = r.style_id WHERE s.name = 'Fenil Studio'")
    for row in cur.fetchall():
        audio = row[0]
        if os.path.exists(audio):
            segments, _ = model.transcribe(audio)
            transcript = ' '.join([s.text for s in segments])
            print(f'{os.path.basename(audio)} -> {transcript}')
            
if __name__ == '__main__':
    main()
