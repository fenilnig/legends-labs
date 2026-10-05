from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from legends_labs.ui.widgets.file_drop_zone import FileDropZone

class StageImportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Import Audio Media")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        desc = QLabel("Select the primary audio file you want to edit or restore.")
        desc.setStyleSheet("color: #a0a0a0; font-size: 16px; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Drop Zone
        self.drop_zone = FileDropZone()
        layout.addWidget(self.drop_zone, stretch=1)
        
        # Next Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.next_btn = QPushButton("Continue to Cleanup →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2; color: white; font-weight: bold;
                padding: 12px 24px; border-radius: 6px; font-size: 16px;
            }
            QPushButton:hover { background-color: #4752c4; }
        """)
        self.next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
        
    def go_next(self):
        # Notify master view to switch to stage 1 (Cleanup)
        if self.parent_view:
            self.parent_view.switch_stage(1)
