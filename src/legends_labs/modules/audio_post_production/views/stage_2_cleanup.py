from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QFrame
from PySide6.QtCore import Qt

class StageCleanupView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Background Noise Reduction & Cleanup")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        # Options
        options_frame = QFrame()
        options_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(20, 20, 20, 20)
        
        self.cb_hiss = QCheckBox("Remove Hiss & Hum")
        self.cb_hiss.setChecked(True)
        self.cb_clicks = QCheckBox("De-click (Mouth noise, keyboard)")
        self.cb_clicks.setChecked(True)
        self.cb_plosives = QCheckBox("De-plosive (Pops)")
        self.cb_reverb = QCheckBox("De-reverb (Room Ambience)")
        
        for cb in [self.cb_hiss, self.cb_clicks, self.cb_plosives, self.cb_reverb]:
            cb.setStyleSheet("color: #e0e0e0; font-size: 16px;")
            options_layout.addWidget(cb)
            
        # Intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Reduction Intensity:"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(70)
        intensity_layout.addWidget(self.intensity_slider)
        options_layout.addLayout(intensity_layout)
        
        layout.addWidget(options_frame)
        layout.addStretch()
        
        # Navigation
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Back")
        self.prev_btn.clicked.connect(lambda: self.parent_view.switch_stage(0) if self.parent_view else None)
        
        self.next_btn = QPushButton("Process & Continue →")
        self.next_btn.setStyleSheet("background-color: #5865F2; color: white; font-weight: bold;")
        self.next_btn.clicked.connect(lambda: self.parent_view.switch_stage(2) if self.parent_view else None)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
