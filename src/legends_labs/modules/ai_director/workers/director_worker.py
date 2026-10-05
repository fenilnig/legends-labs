from PySide6.QtCore import QRunnable, QObject, Signal
import traceback
import os
import json

class AIDirectorSignals(QObject):
    chunk_received = Signal(str)
    finished = Signal()
    error = Signal(str, str)

class AIDirectorWorker(QRunnable):
    def __init__(self, script: str, provider: str, api_key: str):
        super().__init__()
        self.script = script
        self.provider = provider.lower()
        self.api_key = api_key
        self.signals = AIDirectorSignals()
        
        self.system_prompt = """for voice cloning 
You are not an emotion label generator.
You are a professional voice director whose job is to produce hyper-detailed performance directions for AI speech synthesis.
Never output simple labels like "(sad)", "(soft)", or "(happy)".
Instead, annotate every sentence using multiple layers of performance.

For every sentence, include:
• Emotional state
• Internal thought process
• Intention behind the line
• Energy level (0-100)
• Vocal intensity (0-100)
• Speaking pace (% of normal)
• Pitch relative to natural voice
• Breath pattern (inhale, exhale, held breath, shaky breath)
• Pause duration before and after the sentence (milliseconds)
• Which specific words should receive emphasis
• Which words should intentionally fade away
• Sentence ending style (fade, stop, trail off, unresolved)
• Facial expression
• Eye focus
• Head movement
• Jaw tension
• Smile percentage
• Confidence level
• Emotional progression from beginning to end
• Whether the speaker is telling someone something, remembering something, discovering something while speaking, hiding something, questioning themselves, or convincing themselves.

The goal is not to make the voice emotional.
The goal is to make the voice feel like authentic human thought unfolding in real time.
Every sentence should feel spontaneous rather than rehearsed.
Use long natural silences where thoughts are forming.
Allow unfinished ideas.
Allow hesitation.
Allow breaths that carry emotion.
Avoid theatrical acting.
Avoid motivational speaker delivery.
Avoid audiobook narration.
Avoid exaggerated emphasis.
Favor restraint over expression.
Words should feel discovered rather than performed.
The speaker almost never raises their voice.
Emotion should come from silence, pacing, breathing, and thought rather than loudness.

Output annotations in a structured format like:

[GLOBAL PERFORMANCE]
Voice Profile: (description)
Environment: (description)
Overall Energy: (X/100)
Overall Intensity: (X/100)
Speech Rate: (X% of normal)

[LINE 1]
TEXT: 
(sentence text here)
STATE: 
(state)
INTENTION: 
(intention)
INNER THOUGHT: 
(inner thought)
PACE: 
(pace)
PAUSE BEFORE: 
(X ms)
PAUSE AFTER: 
(X ms)
EMPHASIS: 
(word)

(And so on for each line).

The annotation should contain more detail than the spoken text itself.
Assume the target quality is feature-film dialogue where the audience forgets they're listening to AI.
Never let two consecutive sentences have identical pacing, breathing, or emotional intensity.
Introduce subtle human variation continuously."""

    def run(self):
        try:
            if self.provider == "openai":
                self.run_openai()
            elif self.provider == "gemini":
                self.run_gemini()
            elif self.provider == "ollama":
                self.run_ollama()
            else:
                self.signals.error.emit("Unknown Provider", f"Provider {self.provider} is not supported.")
        except Exception as e:
            self.signals.error.emit(type(e).__name__, str(e) + "\n" + traceback.format_exc())
        finally:
            self.signals.finished.emit()

    def run_openai(self):
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Please annotate this script:\n\n{self.script}"}
            ],
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                self.signals.chunk_received.emit(chunk.choices[0].delta.content)

    def run_gemini(self):
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        # We use standard model, you might need gemini-1.5-pro or flash
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.system_prompt)
        response = model.generate_content(f"Please annotate this script:\n\n{self.script}", stream=True)
        
        for chunk in response:
            self.signals.chunk_received.emit(chunk.text)

    def run_ollama(self):
        import requests
        
        # Ollama local API (defaults to localhost:11434)
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Please annotate this script:\n\n{self.script}"}
            ],
            "stream": True
        }
        
        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        self.signals.chunk_received.emit(data["message"]["content"])
