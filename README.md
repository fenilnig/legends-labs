# Legend's Labs

**The DaVinci Resolve of AI audio.** A Windows desktop app that brings voice cloning, expressive speech generation, and AI audio processing into one editor — with the heavy models running locally on your own GPU.

## Modules

| Module | What it does |
|---|---|
| **Voice Clone** | Build a voice from reference clips and generate expressive speech in it. Pluggable engines: **Fish Speech 1.5 / OpenAudio S1-mini**, **XTTS**, **Chatterbox**, **GPT-SoVITS**. Includes training datasets, live training, a pronunciation dictionary, and voice memory. |
| **AI Director** | Annotates a script for natural delivery — pacing, breaths, pauses, and emotional progression sentence by sentence — so the cloned voice performs instead of just reading. Works with GPT-4o, Gemini 1.5 Flash, or a local Llama 3 via Ollama. |
| **Vocal Isolation** | AI stem separation (Demucs, MDX, RoFormer models via audio-separator) to pull vocals, music, and effects apart. |
| **Voice Enhance** | AI noise reduction and cleanup with DeepFilterNet. |
| **Speech to Text** | Transcription with faster-whisper, plus forced alignment and phoneme extraction (Allosaurus). |
| **Emotion** | Speech emotion recognition with SpeechBrain. |
| **Audio Editor & Post-Production** | Trim, split, merge, and fade; real-time effect chains (EQ, compression, reverb) with Spotify's Pedalboard; spectrogram, loudness, and clipping analysis. |
| **Batch Processor** | Run processing jobs over many files at once. |
| **Model Manager** | Download and manage models, with VRAM-aware loading. |
| **Library** | Projects, voice styles, and reference clips in one place. |

There's also a **local inference server** (FastAPI + WebSocket, token-authenticated) that streams TTS from the engines, so other tools can use the same voices.

## Stack

Python 3.12 · PySide6 (Qt) · PyTorch / torchaudio · Fish Speech · Coqui XTTS · Chatterbox · GPT-SoVITS · faster-whisper · audio-separator · DeepFilterNet · SpeechBrain · Pedalboard · librosa · FastAPI

## Setup

Requires Python 3.12+ and **ffmpeg** on your PATH (or `ffmpeg.exe`/`ffprobe.exe` placed in `src/legends_labs/bin/`). An NVIDIA GPU is strongly recommended.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -e .
```

`setup_venv.ps1` installs CUDA-enabled PyTorch and XTTS into a `venv_ml` environment next to the project.

Run it:

```powershell
python launcher.py
```

Model weights are not included in this repo — download them from the in-app **Model Manager** (or run `download_s1_mini.bat` for the S1-mini checkpoint). Cloud LLMs for the AI Director need your own API key, entered in the AI Director panel; the local Ollama option needs none.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT

---

Made by **Fenil Shah** — [GitHub](https://github.com/fenilnig)
