from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame
from PySide6.QtCore import Qt

class StageExportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        header = QLabel("Preview & Export")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        options_frame = QFrame()
        options_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(20, 20, 20, 20)
        
        # Export Presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Export Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Lossless Archival (WAV 24-bit 48kHz)",
            "Podcast / Voiceover (MP3 320kbps)",
            "YouTube / Social Media (AAC)",
            "Broadcast Standard (LUFS -23)"
        ])
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        options_layout.addLayout(preset_layout)
        
        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Audio Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WAV", "FLAC", "MP3", "AAC", "OGG"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        layout.addWidget(options_frame)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Back to Editing")
        self.prev_btn.clicked.connect(lambda: self.parent_view.switch_stage(4) if self.parent_view else None)
        
        self.export_btn = QPushButton("Render & Export")
        self.export_btn.setStyleSheet("background-color: #43b581; color: white; font-weight: bold;")
        
        for btn in [self.prev_btn, self.export_btn]:
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
