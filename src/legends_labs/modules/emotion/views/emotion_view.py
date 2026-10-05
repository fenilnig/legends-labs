from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt

class EmotionView(QWidget):
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
        icon_lbl.setPixmap(get_icon("emotion").pixmap(24, 24))
        
        lbl = QLabel("Emotion Recognition")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        placeholder = QLabel("Emotion timeline visualization will go here.\n(SpeechBrain / SenseVoice)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #888888; border: 2px dashed #333333; border-radius: 10px;")
        layout.addWidget(placeholder, stretch=1)
