from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox, QFrame

class StageIsolationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        header = QLabel("Vocal Isolation & Stem Separation")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        options_frame = QFrame()
        options_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(20, 20, 20, 20)
        
        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("AI Engine:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["HTDemucs (Balanced)", "BS-RoFormer (High Quality)", "MDX-Net (Vocals Only)"])
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        options_layout.addLayout(model_layout)
        
        # Stems
        options_layout.addWidget(QLabel("Stems to Extract:"))
        stems_layout = QHBoxLayout()
        for stem in ["Vocals", "Drums", "Bass", "Other / Instruments"]:
            cb = QCheckBox(stem)
            cb.setChecked(stem == "Vocals")
            cb.setStyleSheet("color: #e0e0e0; font-size: 16px;")
            stems_layout.addWidget(cb)
        stems_layout.addStretch()
        options_layout.addLayout(stems_layout)
        
        layout.addWidget(options_frame)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Back")
        self.prev_btn.clicked.connect(lambda: self.parent_view.switch_stage(1) if self.parent_view else None)
        
        self.next_btn = QPushButton("Isolate & Continue →")
        self.next_btn.setStyleSheet("background-color: #5865F2; color: white; font-weight: bold;")
        self.next_btn.clicked.connect(lambda: self.parent_view.switch_stage(3) if self.parent_view else None)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
