from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame
from PySide6.QtCore import Qt

class AudioPostProductionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Top Pipeline Navigation Bar
        self.nav_bar = QFrame()
        self.nav_bar.setStyleSheet("background-color: #1a1a1a; border-bottom: 2px solid #333333;")
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(20, 10, 20, 10)
        self.nav_layout.setSpacing(10)
        
        self.stages = [
            "1. Import",
            "2. Cleanup",
            "3. Isolate",
            "4. Enhance",
            "5. Edit",
            "6. Export"
        ]
        
        self.nav_buttons = []
        for i, stage_name in enumerate(self.stages):
            btn = QPushButton(stage_name)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #888888;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    color: #e0e0e0;
                    background-color: #2a2a2a;
                }
                QPushButton:checked {
                    color: white;
                    background-color: #5865F2;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_stage(idx))
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            # Add separator arrows between stages, except for the last one
            if i < len(self.stages) - 1:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold;")
                self.nav_layout.addWidget(arrow)
                
        self.nav_layout.addStretch()
        self.layout.addWidget(self.nav_bar)
        
        # Stacked Widget for Stages
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.init_stages()
        
        # Set initial stage
        self.switch_stage(0)
        
    def init_stages(self):
        # We will lazy-load or import the UI views for the 6 stages here.
        from legends_labs.modules.audio_post_production.views.stage_1_import import StageImportView
        from legends_labs.modules.audio_post_production.views.stage_2_cleanup import StageCleanupView
        from legends_labs.modules.audio_post_production.views.stage_3_isolation import StageIsolationView
        from legends_labs.modules.audio_post_production.views.stage_4_enhancement import StageEnhancementView
        from legends_labs.modules.audio_post_production.views.stage_5_editing import StageEditingView
        from legends_labs.modules.audio_post_production.views.stage_6_export import StageExportView
        
        self.stack.addWidget(StageImportView(self))
        self.stack.addWidget(StageCleanupView(self))
        self.stack.addWidget(StageIsolationView(self))
        self.stack.addWidget(StageEnhancementView(self))
        self.stack.addWidget(StageEditingView(self))
        self.stack.addWidget(StageExportView(self))

    def switch_stage(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i != index:
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.blockSignals(False)
            else:
                btn.blockSignals(True)
                btn.setChecked(True)
                btn.blockSignals(False)
                
        self.stack.setCurrentIndex(index)
