import re
from typing import Dict, Tuple

class PromptParser:
    """
    Parses bracketed semantic tags from a script.
    Example: 
    [Emotion: Neutral | Pace: Fast | Pitch: High]
    Hello world!
    
    Returns:
    (
        {"Emotion": "Neutral", "Pace": "Fast", "Pitch": "High"},
        "Hello world!"
    )
    """
    @staticmethod
    def parse_script(script: str) -> Tuple[Dict[str, str], str]:
        # Regex to find anything in brackets at the beginning or anywhere in the text
        # We look for blocks like [Key: Value | Key: Value]
        metadata = {}
        clean_text = script
        
        # Find all bracketed blocks
        bracket_pattern = r'\[(.*?)\]'
        matches = re.finditer(bracket_pattern, script)
        
        for match in matches:
            block = match.group(1)
            
            # Check if this block actually looks like metadata (contains Key: Value)
            if ":" in block:
                # Split by pipe or comma
                pairs = re.split(r'\||,', block)
                
                is_valid_metadata = False
                for pair in pairs:
                    if ":" in pair:
                        is_valid_metadata = True
                        key, val = pair.split(":", 1)
                        metadata[key.strip().lower()] = val.strip().lower()
                
                if is_valid_metadata:
                    # Remove this specific block from the text so it isn't spoken
                    clean_text = clean_text.replace(match.group(0), "")
                    
        # Clean up any leftover whitespace or newlines from removing the brackets
        clean_text = clean_text.strip()
        
        return metadata, clean_text

    @staticmethod
    def map_to_xtts_params(metadata: Dict[str, str]) -> Dict[str, float]:
        """
        Maps parsed semantic tags to physical generation or DSP parameters.
        Returns a dictionary with numeric multipliers/settings.
        """
        params = {
            "speed": 1.0,
            "pitch_shift": 0.0,
            "volume_db": 0.0,
            "emotion": None
        }
        
        # Parse Pace -> speed
        pace = metadata.get("pace", "normal")
        if pace in ["very fast", "fastest"]: params["speed"] = 1.3
        elif pace == "fast": params["speed"] = 1.15
        elif pace == "slow": params["speed"] = 0.85
        elif pace in ["very slow", "slowest"]: params["speed"] = 0.7
        
        # Parse Pitch -> pitch_shift (semitones)
        pitch = metadata.get("pitch", "baseline")
        if pitch == "high": params["pitch_shift"] = 2.0
        elif pitch == "very high": params["pitch_shift"] = 4.0
        elif pitch == "low": params["pitch_shift"] = -2.0
        elif pitch == "very low": params["pitch_shift"] = -4.0
        
        # Parse Volume/Energy -> volume_db
        vol = metadata.get("volume", metadata.get("energy", "medium"))
        if vol == "high": params["volume_db"] = 3.0
        elif vol == "very high": params["volume_db"] = 6.0
        elif vol == "low": params["volume_db"] = -3.0
        elif vol == "very low": params["volume_db"] = -6.0
        
        # Pass emotion string if it exists
        if "emotion" in metadata:
            params["emotion"] = metadata["emotion"].capitalize()
            
        return params
