import sys
from PySide6.QtWidgets import QApplication
from legends_labs.ui.widgets.audio_player import AudioPlayerWidget

app = QApplication(sys.argv)
try:
    player = AudioPlayerWidget(title="Test")
    player.load_audio("outputs/Recording (3)_(Vocals)_htdemucs.wav")
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
