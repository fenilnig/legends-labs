from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QFrame
from PySide6.QtCore import Qt

class StageEnhancementView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        header = QLabel("AI Vocal Enhancement")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        options_frame = QFrame()
        options_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(20, 20, 20, 20)
        
        # Options
        for opt in [
            "Dialogue Enhancement (Clarity)",
            "Dynamic Range Optimization (Auto-Leveling)",
            "Spectral Repair & Bandwidth Extension",
            "Automatic EQ & Presence",
            "Pitch Stabilization"
        ]:
            cb = QCheckBox(opt)
            cb.setChecked(True)
            cb.setStyleSheet("color: #e0e0e0; font-size: 16px;")
            options_layout.addWidget(cb)
            
        layout.addWidget(options_frame)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Back")
        self.prev_btn.clicked.connect(lambda: self.parent_view.switch_stage(2) if self.parent_view else None)
        
        self.next_btn = QPushButton("Enhance & Continue →")
        self.next_btn.setStyleSheet("background-color: #5865F2; color: white; font-weight: bold;")
        self.next_btn.clicked.connect(lambda: self.parent_view.switch_stage(4) if self.parent_view else None)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
