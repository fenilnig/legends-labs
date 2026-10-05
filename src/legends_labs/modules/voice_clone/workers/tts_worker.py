import time
from PySide6.QtCore import QObject
from legends_labs.core.task_queue import BaseWorker

_dict_cache = {}
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "where",
    "why", "how", "what", "who", "whom", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "their", "our", "its", "am", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over",
    "after", "some", "any", "no", "not", "can", "will", "would", "should", "could"
}
CORE_TRIGGERS = {
    "fast", "slow", "high", "low", "loud", "quiet", "deep", "bass", "whisper", "scream", "yell", "softly", "quickly"
}

class TTSWorker(BaseWorker):
    def __init__(self, script: str, engine: str, voice_profile: str, emotion_level: int, selected_reference_clip: str = None):
        super().__init__()
        self.script = script
        self.engine = engine
        self.voice_profile = voice_profile
        self.emotion_level = emotion_level
        self.selected_reference_clip = selected_reference_clip

    def run(self):
        import asyncio
        asyncio.run(self.run_async())
        
    async def run_async(self):
        try:
            self.signals.started.emit()
            self.signals.progress.emit(10, f"Preparing request for {self.engine}...")
            
            # Resolve the voice profile
            profile_name = self.voice_profile.replace("Fenil - ", "").strip()
            from legends_labs.modules.voice_clone.voice_memory import voice_memory
            
            clips_with_emotions = voice_memory.get_clips_with_emotions(profile_name)
            if not clips_with_emotions:
                self.signals.error.emit("No Reference Audio", f"The profile '{profile_name}' has no reference recordings. Please drop a recording into the Evolution panel first!")
                return
                
            # Voice Consistency Score: Prefer longer duration and lower noise
            def clip_score(c):
                dur = c.get("duration") or 0.0
                if dur <= 0.0:
                    return -10000.0
                noise = c.get("noise_level") or -60.0
                return (dur * 1.0) - (noise * 2.0)
                
            clips_with_emotions_sorted = sorted(clips_with_emotions, key=clip_score, reverse=True)
            default_clip = clips_with_emotions_sorted[0]["path"] if clips_with_emotions_sorted else clips_with_emotions[-1]["path"]
            available_emotions = list(set(c["emotion"] for c in clips_with_emotions))
            
            clips_by_emotion = {}
            for c in clips_with_emotions_sorted:
                if c["emotion"] not in clips_by_emotion:
                    clips_by_emotion[c["emotion"]] = []
                clips_by_emotion[c["emotion"]].append(c["path"])
                
            # Manual Override
            if self.selected_reference_clip and os.path.exists(self.selected_reference_clip):
                default_clip = self.selected_reference_clip
                for em in available_emotions + ["neutral"]:
                    clips_by_emotion[em] = [self.selected_reference_clip]
                
            # 1. Parse Script
            import re
            
            def map_emotion(tag: str, avail: list) -> str:
                tag = tag.lower()
                emotion_map = {
                    "soft": "casual", "reflective": "casual", "quiet": "neutral", "thoughtful": "neutral",
                    "smile": "casual", "laugh": "excited", "angry": "authoritative", "yell": "excited",
                    "dramatic": "cinematic", "epic": "cinematic", "serious": "authoritative", "fast": "excited"
                }
                for keyword, target in emotion_map.items():
                    if keyword in tag and target in avail:
                        return target
                for em in avail:
                    if em in tag:
                        return em
                return None

            def get_synonyms(word: str) -> list:
                global _dict_cache
                word = word.lower().strip()
                if not word or word in STOP_WORDS or word in CORE_TRIGGERS:
                    return []
                if word in _dict_cache:
                    return _dict_cache[word]
                
                import urllib.request
                import json
                try:
                    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=1.5) as response:
                        data = json.loads(response.read().decode())
                        syns = []
                        for meaning in data[0].get('meanings', []):
                            for definition in meaning.get('definitions', []):
                                syns.extend(definition.get('synonyms', []))
                            syns.extend(meaning.get('synonyms', []))
                        syns = list(set(s.lower() for s in syns))
                        _dict_cache[word] = syns
                        return syns
                except Exception:
                    _dict_cache[word] = []
                return []

            def infer_sentiment_emotion(text: str, current_em: str, avail: list) -> str:
                if current_em != "neutral":
                    return current_em
                
                text_lower = text.lower()
                semantic_map = {
                    "excited": [
                        r"\bwow\b", r"\bawesome\b", r"\bincredible\b", r"\bhappy\b", r"\bgreat\b", 
                        r"\bamazing\b", r"\bwonderful\b", r"\bcool\b", r"\bhurray\b", r"\byay\b", 
                        r"\blove\b", r"\bthrilled\b", r"\bdelighted\b", r"\blaugh\b", r"\bexcited\b",
                        r"\bfantastic\b", r"\bfabulous\b", r"\bsuperb\b", r"\bbrilliant\b", r"\bterrific\b",
                        r"\boutstanding\b", r"\bhooray\b", r"\bomg\b", r"\byippee\b", r"\bwahoo\b",
                        r"\beureka\b", r"\bsweet\b", r"\bperfect\b", r"\bstunning\b", r"\bspectacular\b",
                        r"\bmagical\b", r"\bjoyful\b", r"\bhype\b", r"\bhyped\b", r"\bpumped\b",
                        r"\bstoked\b", r"\bthrilling\b", r"\becstatic\b", r"\belated\b", r"\boverjoyed\b",
                        r"\bgleeful\b", r"\bcheer\b", r"\bcheering\b", r"\bcelebrate\b", r"\btriumph\b",
                        r"\bvictory\b", r"\bglorious\b", r"\bmagnificent\b", r"\bphenomenal\b",
                        r"\bunbelievable\b", r"\binsane\b", r"\bcrazy\b", r"\bwild\b", r"\bunreal\b",
                        r"\brad\b", r"\bsplendid\b", r"\bdelight\b", r"\bstellar\b", r"\bchampion\b",
                        r"\bwoohoo\b", r"\bhoorah\b", r"\bpeachy\b", r"\bsensational\b", r"\bmarvelous\b"
                    ],
                    "authoritative": [
                        r"\bmust\b", r"\bserious\b", r"\bcritical\b", r"\burgent\b", r"\bwarning\b", 
                        r"\bdemanded\b", r"\bhate\b", r"\bangry\b", r"\bfurious\b", r"\bstop\b", 
                        r"\bnever\b", r"\brules\b", r"\bcommand\b", r"\border\b", r"\bauthority\b"
                    ],
                    "cinematic": [
                        r"\bepic\b", r"\blegendary\b", r"\bdestiny\b", r"\bfate\b", r"\bforever\b", 
                        r"\bdarkness\b", r"\bshadow\b", r"\bworld\b", r"\buniverse\b", r"\bjourney\b", 
                        r"\badventure\b", r"\bdramatic\b", r"\bhistory\b"
                    ],
                    "casual": [
                        r"\bmaybe\b", r"\bguess\b", r"\bwell\b", r"\bprobably\b", r"\bcasual\b", 
                        r"\bwhatever\b", r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bsoftly\b", 
                        r"\bgentle\b", r"\bnice\b"
                    ]
                }
                
                # 1. Local direct matches
                for target_em in ["cinematic", "excited", "authoritative", "casual"]:
                    if target_em in avail:
                        for pattern in semantic_map[target_em]:
                            if re.search(pattern, text_lower):
                                return target_em
                                
                # 2. Synonym expansion lookup via Google Dictionary
                words = re.findall(r"\b[a-zA-Z']+\b", text_lower)
                candidate_words = [w for w in words if w not in STOP_WORDS]
                
                for word in candidate_words[:3]:
                    syns = get_synonyms(word)
                    for syn in syns:
                        for target_em in ["cinematic", "excited", "authoritative", "casual"]:
                            if target_em in avail:
                                for pattern in semantic_map[target_em]:
                                    if re.search(pattern, syn):
                                        return target_em
                                        
                return current_em

            def infer_physical_prosody(text: str) -> dict:
                text_lower = text.lower()
                phys_map = {
                    "fast": [
                        r"\bfast\b", r"\bquick\b", r"\bquickly\b", r"\brapid\b", r"\brapidly\b", 
                        r"\bhurry\b", r"\bhurriedly\b", r"\bswiftly\b", r"\bfastest\b", r"\bspeedy\b", r"\brush\b"
                    ],
                    "slow": [
                        r"\bslow\b", r"\bslowly\b", r"\bsluggish\b", r"\bdragging\b", r"\bcrawling\b", 
                        r"\bdelayed\b", r"\bponderous\b", r"\bleisurely\b", r"\bgradually\b"
                    ],
                    "high": [
                        r"\bhigh\b", r"\bsqueaky\b", r"\bchildish\b", r"\bscreeching\b", r"\bsharp\b", 
                        r"\bshrill\b", r"\bcute\b", r"\btiny\b", r"\bhigh-pitched\b"
                    ],
                    "low": [
                        r"\blow\b", r"\bdeep\b", r"\bbass\b", r"\bgravelly\b", r"\braspy\b", 
                        r"\bdark\b", r"\bbottom\b", r"\bhollow\b", r"\bheavy\b", r"\bmanly\b"
                    ],
                    "loud": [
                        r"\bloud\b", r"\bloudly\b", r"\bscream\b", r"\bscreaming\b", r"\byell\b", 
                        r"\bshout\b", r"\bshouting\b", r"\bnoisy\b", r"\bbooming\b"
                    ],
                    "quiet": [
                        r"\bquiet\b", r"\bquietly\b", r"\bwhisper\b", r"\bwhispering\b", r"\bsoft\b", 
                        r"\bsoftly\b", r"\bsilent\b", r"\bsilently\b", r"\bhushed\b", r"\bmurmur\b", r"\bmurmur\b", r"\bmuffled\b"
                    ]
                }
                
                result = {"speed": 1.0, "pitch_shift": 0.0, "volume_db": 0.0}
                
                def check_attribute(attr_list: list) -> bool:
                    for pattern in attr_list:
                        if re.search(pattern, text_lower):
                            return True
                    words = re.findall(r"\b[a-zA-Z']+\b", text_lower)
                    candidate_words = [w for w in words if w not in STOP_WORDS]
                    for word in candidate_words[:3]:
                        syns = get_synonyms(word)
                        for syn in syns:
                            for pattern in attr_list:
                                if re.search(pattern, syn):
                                    return True
                    return False
                
                if check_attribute(phys_map["fast"]): result["speed"] = 1.25
                elif check_attribute(phys_map["slow"]): result["speed"] = 0.8
                
                if check_attribute(phys_map["high"]): result["pitch_shift"] = 2.5
                elif check_attribute(phys_map["low"]): result["pitch_shift"] = -2.5
                
                if check_attribute(phys_map["loud"]): result["volume_db"] = 4.0
                elif check_attribute(phys_map["quiet"]): result["volume_db"] = -5.0
                
                return result

            segments = []
            current_emotion = "neutral"
            
            if "[LINE" in self.script.upper():
                # Advanced Structured Parsing Mode
                blocks = re.split(r'\[LINE\s+\d+\]', self.script, flags=re.IGNORECASE)
                for block in blocks:
                    block = block.strip()
                    if not block or "TEXT:" not in block.upper():
                        continue
                    
                    # 1. Pause before
                    pb_match = re.search(r'PAUSE BEFORE:\s*(\d+)', block, re.IGNORECASE)
                    if pb_match:
                        duration = float(pb_match.group(1)) / 1000.0
                        segments.append({"type": "pause", "duration": duration})
                        
                    # 2. Extract state/voice to set emotion
                    state_match = re.search(r'(?:STATE|VOICE|NOTES):\s*(.*?)(?=\n[A-Z\s]+:|$)', block, re.DOTALL | re.IGNORECASE)
                    if state_match:
                        new_emotion = map_emotion(state_match.group(1), available_emotions)
                        if new_emotion:
                            current_emotion = new_emotion
                            
                    # 3. Extract text and bind to emotion clip
                    text_match = re.search(r'TEXT:\s*(.*?)(?=\n[A-Z\s]+:|$)', block, re.DOTALL | re.IGNORECASE)
                    if text_match:
                        text = text_match.group(1).strip()
                        if text:
                            clip_to_use = default_clip
                            line_emotion = infer_sentiment_emotion(text, current_emotion, available_emotions)
                            if line_emotion in clips_by_emotion:
                                clip_to_use = clips_by_emotion[line_emotion][0]
                            phys = infer_physical_prosody(text)
                            segments.append({
                                "type": "text", 
                                "text": text, 
                                "clip": clip_to_use, 
                                "emotion": line_emotion,
                                "speed": phys["speed"],
                                "pitch_shift": phys["pitch_shift"],
                                "volume_db": phys["volume_db"]
                            })
                            
                    # 4. Pause after
                    pa_match = re.search(r'PAUSE AFTER:\s*(\d+)', block, re.IGNORECASE)
                    if pa_match:
                        duration = float(pa_match.group(1)) / 1000.0
                        segments.append({"type": "pause", "duration": duration})
                        
            else:
                # Standard Inline Tag Parsing Mode (supports both () and [])
                parts = re.split(r'[\(\[]([^()\[\]]+)[\)\]]', self.script)
                
                for i, part in enumerate(parts):
                     part = part.strip()
                     if not part: continue
                     
                     if i % 2 == 1:
                         tag_lower = part.lower()
                         
                         # 1. Always attempt to extract emotion (LLM might embed it with pauses)
                         new_emotion = map_emotion(part, available_emotions)
                         if new_emotion is not None:
                             current_emotion = new_emotion
                             
                         # 2. Extract explicit pauses or silences
                         if "pause" in tag_lower or "silence" in tag_lower:
                             m = re.search(r'(\d+(?:\.\d+)?)', tag_lower)
                             if m:
                                 duration = float(m.group(1))
                                 if "ms" in tag_lower or "millisecond" in tag_lower:
                                     duration /= 1000.0
                                 segments.append({"type": "pause", "duration": duration})
                             elif "pause" in tag_lower:
                                 # Default pause if no number is found, but only if "pause" is explicitly requested
                                 segments.append({"type": "pause", "duration": 0.5})
                     else:
                         # NLP Prosody & Breathing Predictor (Phase 2)
                         # Break large chunks of text into sentences, injecting natural breathing pauses
                         import re
                         sentences = re.split(r'(?<=[.!?])\s+', part)
                         for s_idx, sentence in enumerate(sentences):
                             sentence = sentence.strip()
                             if not sentence: continue
                             
                             # Analyze punctuation for implicit prosody
                             inferred_emotion = current_emotion
                             if sentence.endswith('?') and current_emotion == 'neutral' and 'casual' in available_emotions:
                                 inferred_emotion = 'casual' # Questions often sound better casual than monotone
                             elif sentence.endswith('!') and current_emotion == 'neutral' and 'excited' in available_emotions:
                                 inferred_emotion = 'excited'
                             
                             # Smarter Semantic Emotion Predictor (if still neutral)
                             if inferred_emotion == 'neutral':
                                 inferred_emotion = infer_sentiment_emotion(sentence, 'neutral', available_emotions)
                                 
                             clip_to_use = default_clip
                             if inferred_emotion in clips_by_emotion:
                                 clip_to_use = clips_by_emotion[inferred_emotion][0]
                                
                             phys = infer_physical_prosody(sentence)
                             segments.append({
                                 "type": "text", 
                                 "text": sentence, 
                                 "clip": clip_to_use, 
                                 "emotion": inferred_emotion,
                                 "speed": phys["speed"],
                                 "pitch_shift": phys["pitch_shift"],
                                 "volume_db": phys["volume_db"]
                             })
                             
                             # Inject natural breathing pause between sentences (unless it's the last one)
                             if s_idx < len(sentences) - 1:
                                 if sentence.endswith('?'):
                                     segments.append({"type": "pause", "duration": 0.6}) # Thinking pause
                                 elif sentence.endswith('!'):
                                     segments.append({"type": "pause", "duration": 0.8}) # Catch breath after yelling
                                 else:
                                     segments.append({"type": "pause", "duration": 0.4}) # Standard sentence breath
                    
            if not segments:
                self.signals.error.emit("Empty Script", "No text to generate.")
                return

            import os, time
            from legends_labs.core.constants import CACHE_DIR
            preview_path = str(CACHE_DIR / f"preview_voiceover_{int(time.time())}.wav")
            
            import websockets
            import json
            import soundfile as sf
            import numpy as np
            
            uri = "ws://127.0.0.1:54321/ws/inference/tts"
            token = os.environ.get("LL_API_TOKEN", "")
            
            def apply_segment_dsp(data, sr, segment):
                speed = segment.get("speed", 1.0)
                pitch_shift = segment.get("pitch_shift", 0.0)
                volume_db = segment.get("volume_db", 0.0)
                
                if speed == 1.0 and pitch_shift == 0.0 and volume_db == 0.0:
                    return data
                    
                import librosa
                import numpy as np
                from legends_labs.audio.dsp_utils import apply_gain
                
                is_mono = data.shape[1] == 1
                y = data.squeeze() if is_mono else data.T
                
                if pitch_shift != 0.0:
                    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
                    
                if speed != 1.0:
                    y = librosa.effects.time_stretch(y, rate=speed)
                    
                if is_mono:
                    data = y[:, np.newaxis]
                else:
                    data = y.T
                    
                if volume_db != 0.0:
                    data = apply_gain(data, volume_db)
                    
                return data

            final_audio = []
            target_sr = None
            target_channels = 1
            
            text_segments = [s for s in segments if s["type"] == "text"]
            num_text = len(text_segments)
            text_idx = 0
            
            for seg_idx, segment in enumerate(segments):
                if segment["type"] == "pause":
                    if target_sr is not None:
                        silence_frames = int(segment["duration"] * target_sr)
                        final_audio.append(np.zeros((silence_frames, target_channels), dtype=np.float32))
                    continue
                    
                seg_preview_path = str(CACHE_DIR / f"preview_voiceover_seg_{int(time.time())}_{seg_idx}.wav")
                
                # Phase 2: Intelligent Reuse (Query VoiceMemory for exact phrase)
                cached_path = voice_memory.find_cached_audio(profile_name, segment["text"])
                if cached_path and os.path.exists(cached_path):
                    self.signals.progress.emit(int((text_idx / max(1, num_text)) * 100), f"Reusing exact recording from Voice Memory for: '{segment['text']}'")
                    data, sr = sf.read(cached_path, always_2d=True)
                    if target_sr is None:
                        target_sr = sr
                        target_channels = data.shape[1]
                    if sr != target_sr:
                        import librosa
                        data = librosa.resample(data.T, orig_sr=sr, target_sr=target_sr).T
                    data = apply_segment_dsp(data, target_sr, segment)
                    final_audio.append(data.astype(np.float32))
                    text_idx += 1
                    continue
                
                # Generate this segment
                async with websockets.connect(uri) as websocket:
                    # Auth
                    await websocket.send(json.dumps({"token": token}))
                    auth_resp = json.loads(await websocket.recv())
                    if "error" in auth_resp:
                        self.signals.error.emit("Server Auth Failed", auth_resp["error"])
                        return
                        
                    # Apply pronunciation overrides
                    from legends_labs.modules.voice_clone.pronunciation_manager import pronunciation_manager
                    final_text = pronunciation_manager.apply_rules(segment["text"])
                    
                    # Retrieve the reference transcript
                    ref_text = voice_memory.get_clip_transcript(segment["clip"])
                    
                    # Send payload
                    payload = {
                        "engine": self.engine,
                        "text": final_text,
                        "reference_audio": segment["clip"],
                        "reference_text": ref_text,
                        "output_path": seg_preview_path,
                        "emotion_level": self.emotion_level
                    }
                    with open(r"H:\legends-labs\tmp\ui_payload.log", "w") as f:
                        f.write(json.dumps(payload, indent=4))
                    await websocket.send(json.dumps(payload))
                    
                    # Receive progress
                    while True:
                        try:
                            msg = await websocket.recv()
                            data = json.loads(msg)
                            
                            if "error" in data:
                                with open(r"H:\legends-labs\tmp\ui_inference_error.log", "w") as f:
                                    f.write(f"Error: {data['error']}\nTraceback:\n{data.get('traceback', '')}")
                                self.signals.error.emit("Server Inference Error", f"{data['error']}\n{data.get('traceback', '')}")
                                return
                                
                            if "progress" in data and "message" in data:
                                # Scale progress: each text segment gets a portion of 100%
                                base_prog = (text_idx / max(1, num_text)) * 100
                                seg_prog = data["progress"] / max(1, num_text)
                                overall = int(base_prog + seg_prog)
                                
                                msg_suffix = f" [Emotion: {segment['emotion'].title()}]" if segment['emotion'] != 'neutral' else ""
                                self.signals.progress.emit(overall, data["message"] + msg_suffix)
                                
                                if data["progress"] >= 100:
                                    break
                        except websockets.exceptions.ConnectionClosed:
                            break
                            
                # Read generated segment and append
                if os.path.exists(seg_preview_path):
                    data, sr = sf.read(seg_preview_path, always_2d=True)
                    if target_sr is None:
                        target_sr = sr
                        target_channels = data.shape[1]
                    data = apply_segment_dsp(data, target_sr, segment)
                    final_audio.append(data.astype(np.float32))
                else:
                    self.signals.error.emit("Generation Failed", f"Failed to generate segment {seg_idx}")
                    return
                    
                text_idx += 1
                
            # Stitch all together
            self.signals.progress.emit(98, "Stitching emotional segments together...")
            if final_audio:
                stitched = np.concatenate(final_audio, axis=0)
                sf.write(preview_path, stitched, target_sr, subtype="PCM_16")
                self.signals.result.emit(preview_path)
            else:
                self.signals.error.emit("Generation Failed", "No audio was generated.")
                
        except Exception as e:
            import traceback
            self.signals.error.emit(str(type(e).__name__), str(e) + "\n" + traceback.format_exc())
        finally:
            self.signals.finished.emit()
