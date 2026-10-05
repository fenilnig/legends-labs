from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, Slot

class VRAMIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(10)
        
        self.label = QLabel("CUDA")
        self.label.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #43b581; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.label)
        
        self.text_val = QLabel("0.0 GB / 6.0 GB")
        self.text_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #A89F91; font-size: 12px; font-weight: 500;")
        layout.addWidget(self.text_val)
        
        self.progress = QProgressBar()
        self.progress.setFixedSize(60, 4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #2A2621;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #43b581;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress)
        
        self.pct_val = QLabel("0%")
        self.pct_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #A89F91; font-size: 12px; font-weight: 600; min-width: 30px;")
        layout.addWidget(self.pct_val)
        
    @Slot(int, int)
    def update_vram(self, used_mb: int, total_mb: int):
        self.progress.setMaximum(total_mb)
        self.progress.setValue(used_mb)
        
        # Color based on usage
        pct = used_mb / max(1, total_mb)
        color = "#43b581" # Green
        if pct > 0.8:
            color = "#f04747" # Red
        elif pct > 0.5:
            color = "#faa61a" # Amber
            
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background-color: #2A2621; border-radius: 2px; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}
        """)
        
        self.text_val.setText(f"{used_mb/1024:.1f} GB / {total_mb/1024:.1f} GB")
        self.pct_val.setText(f"{int(pct * 100)}%")
