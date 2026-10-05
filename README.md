# Legend's Labs

**The DaVinci Resolve of AI audio.** A standalone Windows desktop app that puts voice cloning, expressive speech generation, and AI audio processing into one editor — running locally on your own GPU.

## Modules

| Module | What it does |
|---|---|
| **Voice Clone** | Build a voice from reference clips, then generate expressive speech in that voice (Chatterbox, Kokoro; optional XTTS) |
| **AI Director** | Parses a script and directs delivery — emotion, pacing, emphasis — with a local LLM (llama.cpp) |
| **Vocal Isolation** | Stem separation: pull vocals, music, and effects apart |
| **Voice Enhance** | AI noise reduction and cleanup (DeepFilterNet) |
| **Speech to Text** | Fast transcription with faster-whisper, plus forced alignment and phoneme extraction |
| **Emotion** | Speech emotion recognition (SpeechBrain, FunASR) |
| **Audio Editor & Post-Production** | Waveform editing, DSP, and finishing |
| **Batch Processor** | Run any pipeline over a whole folder |
| **Model Manager** | Download and manage models, with VRAM-aware loading |
| **Library** | Projects, voice styles, and reference clips in one place |

## Stack

Python 3.12 · PySide6 (Qt) · PyTorch / torchaudio · faster-whisper · audio-separator · DeepFilterNet · SpeechBrain · Chatterbox TTS · Kokoro · llama-cpp-python · librosa

## Setup

```powershell
# Python 3.12+, an NVIDIA GPU recommended
.\setup_venv.ps1
# or manually:
python -m venv venv
venv\Scripts\activate
pip install -e .
```

**ffmpeg** is required — install it and make sure `ffmpeg`/`ffprobe` are on your PATH (or place them in `src/legends_labs/bin/`).

Run it:

```powershell
python launcher.py
# or double-click "Launch Legends Labs.bat"
```

Model weights are not included in this repo; download them through the in-app **Model Manager** (or `download_s1_mini.bat` for the S1-mini checkpoint).

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT

---

Made by **Fenil Shah** — [GitHub](https://github.com/fenilnig)
