import os
import sqlite3
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List
import datetime

from legends_labs.core.constants import DATA_DIR

@dataclass
class VoiceStyle:
    name: str
    reference_clips: List[str] = field(default_factory=list)
    avg_tempo: float = 140.0
    avg_pitch: float = 120.0
    emotion_profile: Dict[str, float] = field(default_factory=lambda: {"neutral": 1.0})

class StyleDict(dict):
    """A dictionary-like wrapper that proxies style requests back to VoiceMemory SQLite backend."""
    def __init__(self, voice_memory):
        super().__init__()
        self.vm = voice_memory

    def get(self, key, default=None):
        return self.vm.get_style(key) or default

    def keys(self):
        return self.vm.get_all_style_names()
        
    def __contains__(self, key):
        return self.vm.get_style(key) is not None

class VoiceMemory:
    def __init__(self):
        self.db_path = DATA_DIR / "default.llproj" # Default project file
        self.old_json_path = DATA_DIR / "voice_memory.json"
        
        self.styles = StyleDict(self)
        self.load_project(self.db_path)

    def load_project(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Only attempt migration if loading the default
        if self.db_path.name == "default.llproj":
            self._migrate_from_json()
            
        # Create defaults if empty
        if not self.get_all_style_names():
            self.add_style("Fenil", tempo=130, pitch=110)

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS voice_styles (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE,
                                avg_tempo REAL,
                                avg_pitch REAL
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS reference_clips (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                style_id INTEGER,
                                audio_path TEXT,
                                transcript TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(style_id) REFERENCES voice_styles(id)
                            )''')
            try:
                conn.execute("ALTER TABLE reference_clips ADD COLUMN transcript TEXT")
            except sqlite3.OperationalError:
                pass
                
            for col in ["duration", "speaking_rate", "avg_pitch", "avg_volume", "energy", "noise_level", "silence_percentage", "sample_rate", "clipping_ratio"]:
                try:
                    conn.execute(f"ALTER TABLE reference_clips ADD COLUMN {col} REAL")
                except sqlite3.OperationalError:
                    pass
            conn.execute('''CREATE TABLE IF NOT EXISTS emotion_profiles (
                                style_id INTEGER,
                                emotion TEXT,
                                score REAL,
                                FOREIGN KEY(style_id) REFERENCES voice_styles(id),
                                UNIQUE(style_id, emotion)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS evolution_history (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                style_id INTEGER,
                                previous_tempo REAL,
                                previous_pitch REAL,
                                added_audio_path TEXT,
                                added_emotion TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(style_id) REFERENCES voice_styles(id)
                            )''')

    def _migrate_from_json(self):
        if not self.old_json_path.exists():
            return
            
        try:
            with open(self.old_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for k, v in data.items():
                self.add_style(k, tempo=v.get("avg_tempo", 140.0), pitch=v.get("avg_pitch", 120.0))
                
                with self._get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM voice_styles WHERE name = ?", (k,))
                    row = cur.fetchone()
                    if not row: continue
                    style_id = row[0]
                    
                    for clip in v.get("reference_clips", []):
                        cur.execute("INSERT INTO reference_clips (style_id, audio_path) VALUES (?, ?)", (style_id, clip))
                        
                    for em, score in v.get("emotion_profile", {}).items():
                        cur.execute("INSERT OR REPLACE INTO emotion_profiles (style_id, emotion, score) VALUES (?, ?, ?)", (style_id, em, score))
                        
            shutil.move(self.old_json_path, str(self.old_json_path) + ".bak")
            print("Successfully migrated VoiceMemory from JSON to SQLite!")
        except Exception as e:
            print(f"Failed to migrate JSON to SQLite: {e}")

    def add_style(self, name: str, tempo: float = 140.0, pitch: float = 120.0):
        with self._get_conn() as conn:
            conn.execute("INSERT OR IGNORE INTO voice_styles (name, avg_tempo, avg_pitch) VALUES (?, ?, ?)", (name, tempo, pitch))
            
    def get_style(self, name: str) -> VoiceStyle:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, avg_tempo, avg_pitch FROM voice_styles WHERE name = ?", (name,))
            row = cur.fetchone()
            if not row: return None
            
            style_id, tempo, pitch = row
            
            cur.execute("SELECT audio_path FROM reference_clips WHERE style_id = ? ORDER BY created_at ASC", (style_id,))
            clips = [r[0] for r in cur.fetchall()]
            
            cur.execute("SELECT emotion, score FROM emotion_profiles WHERE style_id = ?", (style_id,))
            emotions = {r[0]: r[1] for r in cur.fetchall()}
            if not emotions: emotions = {"neutral": 1.0}
            
            return VoiceStyle(name=name, reference_clips=clips, avg_tempo=tempo, avg_pitch=pitch, emotion_profile=emotions)

    def find_cached_audio(self, name: str, text: str) -> str:
        """Phase 2 Intelligent Reuse: Search for an exact phrase in VoiceMemory."""
        if not text: return None
        text_clean = "".join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM voice_styles WHERE name = ?", (name,))
            row = cur.fetchone()
            if not row: return None
            style_id = row[0]
            
            cur.execute("SELECT audio_path, transcript FROM reference_clips WHERE style_id = ? AND transcript IS NOT NULL ORDER BY created_at DESC", (style_id,))
            for r in cur.fetchall():
                path, trans = r
                t_clean = "".join(c for c in trans.lower() if c.isalnum() or c.isspace()).strip()
                if t_clean == text_clean:
                    return path
        return None

    def get_all_style_names(self) -> List[str]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM voice_styles ORDER BY name ASC")
            return [r[0] for r in cur.fetchall()]

    def get_clips_with_emotions(self, name: str) -> List[Dict[str, str]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM voice_styles WHERE name = ?", (name,))
            row = cur.fetchone()
            if not row: return []
            style_id = row[0]
            
            cur.execute('''
                SELECT r.audio_path, COALESCE(MAX(e.added_emotion), 'neutral'),
                       r.duration, r.speaking_rate, r.avg_pitch, r.avg_volume, r.energy, r.noise_level, r.silence_percentage,
                       r.sample_rate, r.clipping_ratio, r.transcript
                FROM reference_clips r
                LEFT JOIN evolution_history e ON r.audio_path = e.added_audio_path AND r.style_id = e.style_id
                WHERE r.style_id = ?
                GROUP BY r.audio_path, r.created_at
                ORDER BY r.created_at ASC
            ''', (style_id,))
            
            results = []
            for r in cur.fetchall():
                path = r[0]
                emotion = r[1]
                duration = r[2]
                speaking_rate = r[3]
                avg_pitch = r[4]
                avg_volume = r[5]
                energy = r[6]
                noise_level = r[7]
                silence_percentage = r[8]
                sample_rate = r[9]
                clipping_ratio = r[10]
                transcript = r[11] or ""
                
                # Auto-backfill legacy clips (if metadata is empty but clip file exists)
                if (duration is None or duration <= 0.0) and os.path.exists(path):
                    try:
                        from legends_labs.audio.dsp_utils import process_reference_audio_segments
                        metrics_gen = process_reference_audio_segments(path)
                        metrics = next(metrics_gen)
                        
                        duration = metrics.get("duration", 0.0)
                        speaking_rate = metrics.get("speaking_rate", 0.0)
                        avg_pitch = metrics.get("pitch", 0.0)
                        avg_volume = metrics.get("avg_volume", 0.0)
                        energy = metrics.get("energy", 0.0)
                        noise_level = metrics.get("noise_level", -60.0)
                        silence_percentage = metrics.get("silence_percentage", 0.0)
                        sample_rate = metrics.get("sample_rate", 44100.0)
                        clipping_ratio = metrics.get("clipping_ratio", 0.0)
                        
                        # Update DB
                        conn.execute("""
                            UPDATE reference_clips 
                            SET duration = ?, speaking_rate = ?, avg_pitch = ?, avg_volume = ?, energy = ?, noise_level = ?, silence_percentage = ?, sample_rate = ?, clipping_ratio = ?
                            WHERE audio_path = ?
                        """, (duration, speaking_rate, avg_pitch, avg_volume, energy, noise_level, silence_percentage, sample_rate, clipping_ratio, path))
                    except Exception as e:
                        print("Error backfilling legacy clip:", e)
                
                results.append({
                    "path": path,
                    "emotion": emotion,
                    "duration": duration if duration is not None else 0.0,
                    "speaking_rate": speaking_rate if speaking_rate is not None else 0.0,
                    "avg_pitch": avg_pitch if avg_pitch is not None else 0.0,
                    "avg_volume": avg_volume if avg_volume is not None else 0.0,
                    "energy": energy if energy is not None else 0.0,
                    "noise_level": noise_level if noise_level is not None else 0.0,
                    "silence_percentage": silence_percentage if silence_percentage is not None else 0.0,
                    "sample_rate": sample_rate if sample_rate is not None else 44100.0,
                    "clipping_ratio": clipping_ratio if clipping_ratio is not None else 0.0,
                    "transcript": transcript
                })
            return results

    def update_from_recording(self, style_name: str, audio_path: str, tempo: float, pitch: float, emotion: str, transcript: str = None, duration: float = 0.0, speaking_rate: float = 0.0, avg_volume: float = 0.0, energy: float = 0.0, noise_level: float = 0.0, silence_percentage: float = 0.0, sample_rate: float = 44100.0, clipping_ratio: float = 0.0):
        style = self.get_style(style_name)
        if not style:
            self.add_style(style_name)
            style = self.get_style(style_name)
            
        N = len(style.reference_clips) + 1
        new_tempo = ((style.avg_tempo * (N - 1)) + tempo) / N
        new_pitch = ((style.avg_pitch * (N - 1)) + pitch) / N
        
        new_emotion_score = style.emotion_profile.get(emotion, 0.0) + 1.0
        
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM voice_styles WHERE name = ?", (style_name,))
            style_id = cur.fetchone()[0]
            
            # Snapshot for Undo
            conn.execute("INSERT INTO evolution_history (style_id, previous_tempo, previous_pitch, added_audio_path, added_emotion) VALUES (?, ?, ?, ?, ?)", 
                         (style_id, style.avg_tempo, style.avg_pitch, audio_path, emotion))
            
            conn.execute("UPDATE voice_styles SET avg_tempo = ?, avg_pitch = ? WHERE id = ?", (new_tempo, new_pitch, style_id))
            conn.execute("INSERT INTO reference_clips (style_id, audio_path, transcript, duration, speaking_rate, avg_pitch, avg_volume, energy, noise_level, silence_percentage, sample_rate, clipping_ratio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                         (style_id, audio_path, transcript, duration, speaking_rate, pitch, avg_volume, energy, noise_level, silence_percentage, sample_rate, clipping_ratio))
            conn.execute("INSERT OR REPLACE INTO emotion_profiles (style_id, emotion, score) VALUES (?, ?, ?)", (style_id, emotion, new_emotion_score))

    def undo_last_evolution(self, style_name: str) -> bool:
        """Undoes the last clip added to the style. Returns True if successful."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM voice_styles WHERE name = ?", (style_name,))
            row = cur.fetchone()
            if not row: return False
            style_id = row[0]
            
            # Get latest history
            cur.execute("SELECT id, previous_tempo, previous_pitch, added_audio_path, added_emotion FROM evolution_history WHERE style_id = ? ORDER BY created_at DESC LIMIT 1", (style_id,))
            history_row = cur.fetchone()
            if not history_row: return False
            
            h_id, prev_tempo, prev_pitch, added_audio, added_emotion = history_row
            
            # Restore previous metrics
            conn.execute("UPDATE voice_styles SET avg_tempo = ?, avg_pitch = ? WHERE id = ?", (prev_tempo, prev_pitch, style_id))
            
            # Remove the added clip
            conn.execute("DELETE FROM reference_clips WHERE style_id = ? AND audio_path = ?", (style_id, added_audio))
            
            # Decrement emotion score
            cur.execute("SELECT score FROM emotion_profiles WHERE style_id = ? AND emotion = ?", (style_id, added_emotion))
            em_row = cur.fetchone()
            if em_row:
                new_score = em_row[0] - 1.0
                if new_score <= 0:
                    conn.execute("DELETE FROM emotion_profiles WHERE style_id = ? AND emotion = ?", (style_id, added_emotion))
                else:
                    conn.execute("UPDATE emotion_profiles SET score = ? WHERE style_id = ? AND emotion = ?", (new_score, style_id, added_emotion))
                    
            # Delete history entry
            conn.execute("DELETE FROM evolution_history WHERE id = ?", (h_id,))
            return True

    def get_clip_transcript(self, audio_path: str) -> str:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT transcript FROM reference_clips WHERE audio_path = ?", (audio_path,))
            row = cur.fetchone()
            return row[0] if row and row[0] else ""

    def update_clip_transcript(self, audio_path: str, transcript: str) -> bool:
        """Updates the transcript of an existing reference clip."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE reference_clips SET transcript = ? WHERE audio_path = ?", (transcript, audio_path))
            return cur.rowcount > 0


voice_memory = VoiceMemory()
