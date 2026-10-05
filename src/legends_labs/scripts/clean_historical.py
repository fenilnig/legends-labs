import sys
import os
import subprocess
from pathlib import Path
from legends_labs.modules.voice_clone.voice_memory import voice_memory

def main():
    profile = "Fenil"
    style = voice_memory.get_style(profile)
    if not style:
        print(f"Profile {profile} not found")
        sys.exit(1)
        
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "..", "modules", "voice_clone", "workers", "cleaner_script.py"
    )
    
    total = len(style.reference_clips)
    print(f"Found {total} clips for profile {profile}. Starting cleaning...")
    
    cleaned_count = 0
    for idx, clip_path in enumerate(style.reference_clips):
        print(f"Cleaning {idx+1}/{total}: {os.path.basename(clip_path)}...")
        
        process = subprocess.Popen(
            [sys.executable, script_path, clip_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Failed to clean {clip_path}: {stderr}")
            continue
            
        success = False
        for line in stdout.splitlines():
            if line.startswith("SUCCESS:"):
                new_path = line.replace("SUCCESS:", "").strip()
                
                # Update SQLite DB
                with voice_memory._get_conn() as conn:
                    conn.execute("UPDATE reference_clips SET audio_path = ? WHERE audio_path = ?", (new_path, clip_path))
                    conn.execute("UPDATE evolution_history SET added_audio_path = ? WHERE added_audio_path = ?", (new_path, clip_path))
                    
                cleaned_count += 1
                success = True
                break
                
        if not success:
            print(f"Failed to find SUCCESS tag for {clip_path}")
            
    print(f"Successfully cleaned and updated {cleaned_count}/{total} clips!")

if __name__ == "__main__":
    main()
