import os
import re

# We will just strip all characters in the typical emoji Unicode ranges
# Or safer: we have the powershell output, we can strip characters that are not ascii, except for em-dash and mid-dot.
# Actually, let's just strip everything out of the ASCII range except em-dash \u2014, en-dash \u2013, mid-dot \u00B7, copyright, etc.
# But even safer, just let a regex remove the known emoji ranges.

emoji_pattern = re.compile(
    r"["
    r"\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"  # symbols & pictographs
    r"\U0001F680-\U0001F6FF"  # transport & map symbols
    r"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    r"\U00002702-\U000027B0"
    r"\U000024C2-\U0001F251"
    r"✨🎙️🗣️🎬😊📝🎛️📦📁🧠⚙️🎤🧬⎌📂💾✅⏳🎧🎵🔊🔈🔉🔇⏯️⏹️⏪⏩✂️✅❌📁"
    r"]+",
    flags=re.UNICODE
)

def strip_emojis_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Also strip some specific hardcoded emojis in case the pattern misses them
    new_content = emoji_pattern.sub('', content)
    
    # Strip lingering zero-width joiners and variation selectors common in emojis
    new_content = re.sub(r'[\uFE0F\u200D]', '', new_content)
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned {os.path.basename(filepath)}")

src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "legends_labs")

for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith(".py"):
            strip_emojis_from_file(os.path.join(root, file))

print("Done stripping emojis from UI files.")
