import os
import sys
from pathlib import Path

# Setup Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Add bin to PATH for FFmpeg
bin_path = project_root / "src" / "legends_labs" / "bin"
if bin_path.exists():
    os.environ["PATH"] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"

from legends_labs.audio.dsp_utils import process_reference_audio
from legends_labs.modules.voice_clone.voice_memory import voice_memory

folder = project_root / "Historical_Recordings"
style_name = "Fenil"

print(f"--- Voice Evolution Analytics ---")
print(f"Target Style: {style_name}\n")

files = list(folder.glob("*.m4a"))
if not files:
    print("No .m4a files found in Historical_Recordings.")
    sys.exit(0)

success_count = 0
for file in files:
    print(f"Analyzing {file.name}...")
    try:
        results = process_reference_audio(str(file))
        print(f"  > Extracted DNA -> Pitch: {results['pitch']:.1f}Hz, Tempo: {results['tempo']:.1f}BPM")
        voice_memory.update_from_recording(
            style_name, 
            results['clean_path'], 
            results['tempo'], 
            results['pitch'], 
            "neutral"  # Default emotion
        )
        print("  > Added to SQLite Memory Database.")
        success_count += 1
    except Exception as e:
        print(f"  [X] Error processing {file.name}: {e}")

print("\n--- Summary ---")
print(f"Successfully processed {success_count}/{len(files)} files.")

style = voice_memory.get_style(style_name)
if style:
    print(f"\nFinal Voice DNA for '{style_name}':")
    print(f"  Aggregate Pitch: {style.avg_pitch:.1f}Hz")
    print(f"  Aggregate Tempo: {style.avg_tempo:.1f}BPM")
    print(f"  Total Clean References: {len(style.reference_clips)}")
