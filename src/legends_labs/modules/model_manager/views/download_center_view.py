from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt

MODELS = [
    ("Whisper Large V3 Turbo", "1.5 GB", "Installed", "#43b581"),
    ("Chatterbox Turbo", "2.1 GB", "Installed", "#43b581"),
    ("XTTS v2", "1.8 GB", "Update Available", "#faa61a"),
    ("BS-RoFormer", "800 MB", "Download", "#5865F2"),
    ("Qwen3 0.6B", "400 MB", "Installed", "#43b581"),
]

class DownloadCenterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        header = QHBoxLayout()
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("models").pixmap(24, 24))
        
        lbl = QLabel("AI Download Center")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        self.main_layout.addWidget(title_widget)
        
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.setStyleSheet("background-color: #242424; color: #e0e0e0; padding: 8px 15px; border-radius: 4px; border: 1px solid #333333;")
        self.refresh_btn.clicked.connect(self.refresh_model_list)
        header.addWidget(self.refresh_btn, alignment=Qt.AlignRight)
        self.main_layout.addLayout(header)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #43b581; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.status_label)
        
        # Scroll area for models
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.main_layout.addWidget(self.scroll)

        self.populate_models()

    def populate_models(self):
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        for name, size, status, color in MODELS:
            card = QFrame()
            card.setStyleSheet(f"QFrame {{ background-color: #1e1e1e; border: 1px solid #333333; border-radius: 8px; }}")
            card_layout = QHBoxLayout(card)
            
            info = QVBoxLayout()
            model_name = QLabel(name)
            model_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; border: none;")
            info.addWidget(model_name)
            
            model_size = QLabel(f"Size: {size}")
            model_size.setStyleSheet("color: #888888; border: none;")
            info.addWidget(model_size)
            card_layout.addLayout(info)
            
            btn = QPushButton(status)
            btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: {'white' if color != '#faa61a' else 'black'}; font-weight: bold; padding: 8px 20px; border-radius: 4px; border: none; }}")
            btn.clicked.connect(lambda checked, n=name, s=status: self.on_model_action(n, s))
            card_layout.addWidget(btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
            
            container_layout.addWidget(card)
            
        container_layout.addStretch()
        self.scroll.setWidget(container)

    def on_model_action(self, model_name: str, status: str):
        if status == "Installed":
            self.status_label.setText(f"✓ '{model_name}' is already installed and ready to use.")
        elif status == "Update Available":
            self.status_label.setText(f"↻ Updating '{model_name}'... (not yet implemented)")
        elif status == "Download":
            self.status_label.setText(f"↓ Downloading '{model_name}'... (not yet implemented)")
        else:
            self.status_label.setText(f"Action for '{model_name}': {status}")

    def refresh_model_list(self):
        self.status_label.setText("Refreshing model list...")
        self.populate_models()
        self.status_label.setText("Model list refreshed.")
