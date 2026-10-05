import re
import os
import sys
from legends_labs.modules.voice_clone.pronunciation_db import pronunciation_db

class PronunciationManager:
    def __init__(self):
        self.nlp = None

    def _load_nlp(self):
        if self.nlp is None:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"Failed to load spaCy model: {e}")
                self.nlp = "failed"

    def apply_rules(self, text: str) -> str:
        self._load_nlp()
        
        # Phase 3: Text Normalization Pipeline
        text = self._normalize_currency(text)
        text = self._normalize_acronyms(text)
        
        # Pull all learned words from the database
        words = pronunciation_db.get_all_words()
        
        if not words:
            # Fallback to the hardcoded defaults if DB is empty
            defaults = {
                "varun mayya": "Vuh-ROON my-YAH",
                "varuynmaya": "Vuh-ROON my-YAH",
                "chatgpt": "Chat Gee Pee Tee"
            }
            for w, p in defaults.items():
                pattern = re.compile(r'\b' + re.escape(w) + r'\b', re.IGNORECASE)
                text = pattern.sub(p, text)
            return text

        if self.nlp != "failed" and self.nlp is not None:
            # Context-aware replacement using spaCy POS tagging
            doc = self.nlp(text)
            new_text = text
            # We process backwards so string replacements don't mess up indices
            for token in reversed(doc):
                lower_text = token.text.lower()
                if lower_text in words:
                    word_obj = pronunciation_db.get_word(lower_text)
                    if word_obj and word_obj.default_variant_id:
                        for variant in word_obj.variants:
                            if variant.id == word_obj.default_variant_id:
                                # Replace the exact token string with the phonetic spelling
                                replacement = variant.phonetic or variant.ipa
                                if replacement:
                                    start, end = token.idx, token.idx + len(token.text)
                                    new_text = new_text[:start] + replacement + new_text[end:]
                                break
            return new_text
        else:
            # Simple regex replacement if NLP fails
            for w in words:
                word_obj = pronunciation_db.get_word(w)
                if word_obj and word_obj.default_variant_id:
                    for variant in word_obj.variants:
                        if variant.id == word_obj.default_variant_id:
                            replacement = variant.phonetic or variant.ipa
                            if replacement:
                                pattern = re.compile(r'\b' + re.escape(w) + r'\b', re.IGNORECASE)
                                text = pattern.sub(replacement, text)
                            break
            return text

    def _normalize_currency(self, text: str) -> str:
        """Expands basic currency symbols to words."""
        # $50.50 -> 50 dollars and 50 cents
        text = re.sub(r'\$(\d+)\.(\d{2})', r'\1 dollars and \2 cents', text)
        text = re.sub(r'\$(\d+)', r'\1 dollars', text)
        text = re.sub(r'€(\d+)\.(\d{2})', r'\1 euros and \2 cents', text)
        text = re.sub(r'€(\d+)', r'\1 euros', text)
        text = re.sub(r'£(\d+)\.(\d{2})', r'\1 pounds and \2 pence', text)
        text = re.sub(r'£(\d+)', r'\1 pounds', text)
        text = re.sub(r'₹(\d+)', r'\1 rupees', text)
        return text

    def _normalize_acronyms(self, text: str) -> str:
        """Smart acronym normalizer. Spaces out true acronyms for spelling but protects standard words."""
        acronyms_to_spell = {
            "FBI", "CIA", "NSA", "HTML", "URL", "PDF", "API", "SDK", "UI", "UX", 
            "VRAM", "TTS", "STT", "LLM", "UAC", "ML", "AI", "WAV", "PCM", "MP3", 
            "JSON", "XML", "GPU", "CPU", "RAM", "ROM", "OS", "PC", "VS", "MSVC",
            "UAC", "USA", "UK", "UN", "EU", "IP", "DNS", "HTTP", "HTTPS", "FTP"
        }
        spoken_acronyms = {"NASA", "NATO", "LASER", "SCUBA", "RADAR", "UNESCO", "UNICEF", "OPEC", "PIN", "AWOL", "ISRO"}
        
        def replace_acronym(match):
            word = match.group(0)
            if word in spoken_acronyms:
                return word
            if word in acronyms_to_spell:
                return " ".join(list(word))
            
            # Heuristic: Uppercase words with no vowels are always spelled acronyms (e.g., "PNG", "TXT", "DRM")
            has_vowels = any(c in "AEIOU" for c in word)
            if not has_vowels and len(word) >= 2:
                return " ".join(list(word))
                
            return word
            
        return re.sub(r'\b[A-Z]{2,}\b', replace_acronym, text)

pronunciation_manager = PronunciationManager()
