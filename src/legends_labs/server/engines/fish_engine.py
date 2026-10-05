import asyncio
import os
import sys
import torch
import subprocess
from typing import AsyncGenerator
from .base import TTSEngine

class FishSpeechEngine(TTSEngine):
    """
    Fish Speech 1.5 TTS Engine executing in an isolated sub-environment
    to prevent VRAM locks and package dependency conflicts with XTTS.
    """
    def __init__(self):
        # Since it runs in a subprocess, it does not keep anything in memory.
        pass
        
    def load(self) -> None:
        pass
            
    def unload(self) -> None:
        pass
                
    async def generate(self, text: str, reference_audio: str, output_path: str, **kwargs) -> AsyncGenerator[dict, None]:
        # Find project root by traversing upwards until we find the parent containing 'venv_fish' or 'vendors'
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = None
        while True:
            if os.path.exists(os.path.join(curr_dir, "venv_fish")) or os.path.exists(os.path.join(curr_dir, "vendors")):
                project_root = curr_dir
                break
            parent = os.path.dirname(curr_dir)
            if parent == curr_dir:  # reached root of filesystem without finding it
                break
            curr_dir = parent
            
        if not project_root:
            # Fallback to 5 levels if not found dynamically
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            
        # Path setup
        venv_python = os.path.join(project_root, "venv_fish", "Scripts", "python.exe")
        if not os.path.exists(venv_python):
            venv_python = os.path.join(project_root, "venv_fish", "bin", "python")
            
        if not os.path.exists(venv_python):
            yield {"error": f"venv_fish environment not found at: {os.path.join(project_root, 'venv_fish')}. Please wait for the dependency installer to complete."}
            return
            
        inference_script = os.path.join(project_root, "vendors", "fish-speech", "generate_audio.py")
        
        # Checkpoint resolution order: s1-mini (if downloaded) → 1.5 (default, works on 6GB VRAM)
        checkpoint_dir = None
        for candidate in ["openaudio-s1-mini", "fish-speech-1.5"]:
            candidate_path = os.path.join(project_root, "checkpoints", candidate)
            if os.path.exists(candidate_path):
                checkpoint_dir = candidate_path
                break
            
        if not checkpoint_dir:
            yield {"error": f"Fish Speech checkpoints not found. Please download a model first."}
            return
            
        if "s1-mini" in checkpoint_dir:
            model_version_name = "S1 Mini"
        else:
            model_version_name = "1.5"
        
        yield {"progress": 5, "message": f"Initializing Fish Speech {model_version_name} pipeline..."}
            
        # Parse reference text if passed, else query database
        ref_text = kwargs.get("reference_text", "")
        if not ref_text:
            # Fallback to query database locally if not passed
            try:
                from legends_labs.modules.voice_clone.voice_memory import voice_memory
                ref_text = voice_memory.get_clip_transcript(reference_audio)
            except Exception:
                ref_text = ""
                
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Build command args
        cmd = [
            venv_python,
            inference_script,
            text,
            output_path,
            checkpoint_dir
        ]
        
        # Add prompt audio and prompt text if available
        if reference_audio and os.path.exists(reference_audio):
            cmd.extend([reference_audio, ref_text if ref_text else "None"])
                
        # Clean environment to prevent PYTHONPATH inheritance conflicts
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        
        # Run subprocess and stream output
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                cwd=os.path.join(project_root, "vendors", "fish-speech")
            )
            
            # Read stdout line by line
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                
                print(f"[FishSpeech CLI] {line}")
                
                # Parse progress indicators
                if "Loading model ..." in line:
                    yield {"progress": 15, "message": f"Loading Fish Speech {model_version_name} LLaMA model..."}
                elif "Loading codec model for audio encoding..." in line:
                    yield {"progress": 40, "message": "Encoding reference voice DNA..."}
                elif "Sampled text:" in line:
                    yield {"progress": 70, "message": "Synthesizing semantic tokens..."}
                elif "Loading codec model for audio decoding..." in line:
                    yield {"progress": 85, "message": "Decoding semantic tokens to audio waveform..."}
                elif "Saved audio to" in line:
                    yield {"progress": 98, "message": "Saving final wave file..."}
                    
            await process.wait()
            
            if process.returncode != 0:
                yield {"error": f"Fish Speech CLI exited with code {process.returncode}. Check logs."}
            else:
                yield {"progress": 100, "message": "Fish Speech generation complete."}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Original exception: {e}")
            yield {"error": f"Subprocess error: {traceback.format_exc()}"}
