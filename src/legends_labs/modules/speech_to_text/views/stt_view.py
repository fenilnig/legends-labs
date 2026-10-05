from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt

class STTView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("stt").pixmap(24, 24))
        
        lbl = QLabel("Speech To Text")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        self.drop_zone = QLabel("Drop audio files here to transcribe")
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setStyleSheet("border: 2px dashed #5865F2; border-radius: 10px; background-color: #1e1e1e; color: #888888; padding: 20px; font-size: 16px;")
        layout.addWidget(self.drop_zone)
        
        self.transcript_output = QTextEdit()
        self.transcript_output.setReadOnly(True)
        self.transcript_output.setPlaceholderText("Transcription will appear here...")
        self.transcript_output.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #333333; border-radius: 6px; padding: 10px; font-size: 14px; }")
        layout.addWidget(self.transcript_output, stretch=1)
        
        controls = QHBoxLayout()
        self.transcribe_btn = QPushButton("Transcribe (faster-whisper)")
        self.transcribe_btn.setStyleSheet("QPushButton { background-color: #5865F2; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 16px; }")
        controls.addWidget(self.transcribe_btn)
        
        self.export_btn = QPushButton("Export Subtitles (.srt)")
        self.export_btn.setStyleSheet("QPushButton { background-color: #242424; color: #e0e0e0; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 16px; border: 1px solid #333333; }")
        controls.addWidget(self.export_btn)
        
        layout.addLayout(controls)
