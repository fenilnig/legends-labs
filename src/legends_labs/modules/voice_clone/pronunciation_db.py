import sqlite3
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime

from legends_labs.core.constants import DATA_DIR
from legends_labs.modules.voice_clone.voice_memory import voice_memory

@dataclass
class PronunciationOccurrence:
    id: int
    audio_path: str
    start_time: float
    end_time: float
    confidence: float
    emotion: str
    context_sentence: str
    style_name: str

@dataclass
class PronunciationVariant:
    id: int
    phonetic: str
    ipa: str
    syllables: str
    stress: str
    occurrences: List[PronunciationOccurrence] = field(default_factory=list)

@dataclass
class PronunciationWord:
    id: int
    spelling: str
    category: str
    default_variant_id: Optional[int]
    variants: List[PronunciationVariant] = field(default_factory=list)

class PronunciationDB:
    def __init__(self):
        # We share the same database file as voice_memory
        pass

    def _get_conn(self):
        return voice_memory._get_conn()

    def init_db(self):
        with self._get_conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS pronunciation_words (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                spelling TEXT UNIQUE,
                                category TEXT,
                                default_variant_id INTEGER
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS pronunciation_variants (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                word_id INTEGER,
                                phonetic TEXT,
                                ipa TEXT,
                                syllables TEXT,
                                stress TEXT,
                                FOREIGN KEY(word_id) REFERENCES pronunciation_words(id)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS pronunciation_occurrences (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                variant_id INTEGER,
                                style_id INTEGER,
                                audio_path TEXT,
                                start_time REAL,
                                end_time REAL,
                                confidence REAL,
                                emotion TEXT,
                                context_sentence TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(variant_id) REFERENCES pronunciation_variants(id),
                                FOREIGN KEY(style_id) REFERENCES voice_styles(id)
                            )''')

    def add_word(self, spelling: str, category: str = "general") -> int:
        with self._get_conn() as conn:
            conn.execute("INSERT OR IGNORE INTO pronunciation_words (spelling, category) VALUES (?, ?)", (spelling.lower(), category))
            cur = conn.cursor()
            cur.execute("SELECT id FROM pronunciation_words WHERE spelling = ?", (spelling.lower(),))
            return cur.fetchone()[0]

    def add_variant(self, word_id: int, phonetic: str, ipa: str, syllables: str, stress: str) -> int:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM pronunciation_variants WHERE word_id = ? AND ipa = ?", (word_id, ipa))
            row = cur.fetchone()
            if row: return row[0]
            
            cur.execute("INSERT INTO pronunciation_variants (word_id, phonetic, ipa, syllables, stress) VALUES (?, ?, ?, ?, ?)",
                        (word_id, phonetic, ipa, syllables, stress))
            return cur.lastrowid

    def add_occurrence(self, variant_id: int, style_name: str, audio_path: str, start_time: float, end_time: float, confidence: float, emotion: str, context: str):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM voice_styles WHERE name = ?", (style_name,))
            style_row = cur.fetchone()
            if not style_row: return
            
            conn.execute('''INSERT INTO pronunciation_occurrences 
                            (variant_id, style_id, audio_path, start_time, end_time, confidence, emotion, context_sentence) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (variant_id, style_row[0], audio_path, start_time, end_time, confidence, emotion, context))

    def set_default_variant(self, word_spelling: str, variant_id: int):
        with self._get_conn() as conn:
            conn.execute("UPDATE pronunciation_words SET default_variant_id = ? WHERE spelling = ?", (variant_id, word_spelling.lower()))

    def get_word(self, spelling: str) -> Optional[PronunciationWord]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, spelling, category, default_variant_id FROM pronunciation_words WHERE spelling = ?", (spelling.lower(),))
            row = cur.fetchone()
            if not row: return None
            
            word_id, sp, cat, def_id = row
            word = PronunciationWord(id=word_id, spelling=sp, category=cat, default_variant_id=def_id)
            
            cur.execute("SELECT id, phonetic, ipa, syllables, stress FROM pronunciation_variants WHERE word_id = ?", (word_id,))
            variants = cur.fetchall()
            
            for v_row in variants:
                v_id, phonetic, ipa, syllables, stress = v_row
                variant = PronunciationVariant(id=v_id, phonetic=phonetic, ipa=ipa, syllables=syllables, stress=stress)
                
                cur.execute('''SELECT o.id, o.audio_path, o.start_time, o.end_time, o.confidence, o.emotion, o.context_sentence, s.name 
                               FROM pronunciation_occurrences o
                               JOIN voice_styles s ON o.style_id = s.id
                               WHERE o.variant_id = ? ORDER BY o.created_at DESC''', (v_id,))
                for o_row in cur.fetchall():
                    variant.occurrences.append(PronunciationOccurrence(
                        id=o_row[0], audio_path=o_row[1], start_time=o_row[2], end_time=o_row[3],
                        confidence=o_row[4], emotion=o_row[5], context_sentence=o_row[6], style_name=o_row[7]
                    ))
                word.variants.append(variant)
                
            return word

    def delete_word(self, spelling: str) -> bool:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM pronunciation_words WHERE spelling = ?", (spelling.lower(),))
            row = cur.fetchone()
            if not row: return False
            word_id = row[0]
            
            # Cascade delete variants and occurrences
            cur.execute("SELECT id FROM pronunciation_variants WHERE word_id = ?", (word_id,))
            for v_row in cur.fetchall():
                conn.execute("DELETE FROM pronunciation_occurrences WHERE variant_id = ?", (v_row[0],))
            
            conn.execute("DELETE FROM pronunciation_variants WHERE word_id = ?", (word_id,))
            conn.execute("DELETE FROM pronunciation_words WHERE id = ?", (word_id,))
            return True

    def get_all_words(self) -> List[str]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT spelling FROM pronunciation_words ORDER BY spelling ASC")
            return [r[0] for r in cur.fetchall()]

pronunciation_db = PronunciationDB()
