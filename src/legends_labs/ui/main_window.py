from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QDockWidget, QLabel, QListWidget, QListWidgetItem, QStatusBar)
from PySide6.QtCore import Qt

from legends_labs.ui.widgets.vram_indicator import VRAMIndicator
from legends_labs.engine.vram_manager import get_vram_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Legend's Labs — Untitled Project")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        
        from legends_labs.ui.widgets.cinematic_overlay import CinematicOverlay
        self.cinematic_overlay = CinematicOverlay(self)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'cinematic_overlay'):
            self.cinematic_overlay.setGeometry(self.rect())
            
    def setup_ui(self):
        # Create central widget layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setIconSize(__import__("PySide6.QtCore").QtCore.QSize(20, 20))
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #0F0E0C;
                border-right: 1px solid #2A2621;
                outline: none;
                padding-top: 20px;
            }
            QListWidget::item {
                color: #A89F91;
                padding: 12px 20px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 600;
            }
            QListWidget::item:selected {
                background-color: rgba(88, 101, 242, 0.1);
                color: #5865F2;
                border-left: 3px solid #5865F2;
            }
            QListWidget::item:hover:!selected {
                background-color: #161412;
            }
        """)
        
        from legends_labs.ui.theme import get_icon
        from PySide6.QtGui import QFont, QColor
        
        sidebar_structure = [
            ("VOICE", None),
            ("Generate", "clone"),
            ("LIBRARY", None),
            ("Voice Models", "models"),
            ("Voice Memory", "library"),
            ("Training & Datasets", "batch"),
            ("TOOLS", None),
            ("Audio Post Production", "editor"),
            ("Model Manager", "models"),
            ("PROJECT", None),
            ("History", "stt"),
            ("Settings", "settings")
        ]
                  
        for label, icon_name in sidebar_structure:
            if icon_name is None:
                # Section Header
                item = QListWidgetItem(label)
                item.setFlags(Qt.ItemIsEnabled)  # Not selectable
                font = QFont("Segoe UI", 11, QFont.Bold)
                item.setFont(font)
                item.setForeground(QColor("#7A7265"))
                # Add extra spacing above headers except the first one
                if self.sidebar.count() > 0:
                    item.setSizeHint(__import__("PySide6.QtCore").QtCore.QSize(0, 45))
                else:
                    item.setSizeHint(__import__("PySide6.QtCore").QtCore.QSize(0, 30))
                self.sidebar.addItem(item)
            else:
                # Nav Item
                item = QListWidgetItem(get_icon(icon_name), f"  {label}")
                self.sidebar.addItem(item)
            
        main_layout.addWidget(self.sidebar)
        
        # Top Status Bar
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: transparent; border-bottom: 1px solid #2A2621;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(30, 15, 30, 15)
        top_layout.setAlignment(Qt.AlignVCenter)
        
        proj_title = QLabel("Fenil Studio")
        proj_title.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 16px; font-weight: 600; color: #F2EFEB;")
        
        dot = QLabel("●")
        dot.setStyleSheet("color: #43b581; font-size: 12px; margin-left: 10px; margin-right: 5px;")
        
        status = QLabel("Ready")
        status.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #43b581;")
        
        divider1 = QLabel("│")
        divider1.setStyleSheet("color: #2A2621; margin: 0 15px;")
        
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        if os.path.exists(os.path.join(project_root, "checkpoints", "openaudio-s1-mini")):
            engine_text = "Fish Speech S1 Mini"
        elif os.path.exists(os.path.join(project_root, "checkpoints", "fish-speech-s2-pro")):
            engine_text = "Fish Speech S2 Pro"
        else:
            engine_text = "Fish Speech 1.5"
            
        engine = QLabel(engine_text)
        engine.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #A89F91;")
        
        divider2 = QLabel("│")
        divider2.setStyleSheet("color: #2A2621; margin: 0 15px;")
        
        top_layout.addWidget(proj_title)
        top_layout.addWidget(dot)
        top_layout.addWidget(status)
        top_layout.addWidget(divider1)
        top_layout.addWidget(engine)
        top_layout.addWidget(divider2)
        
        self.vram_ind = VRAMIndicator()
        top_layout.addWidget(self.vram_ind)
        
        top_layout.addStretch()
        
        from PySide6.QtWidgets import QPushButton
        save_btn = QPushButton("Save Project")
        save_btn.setStyleSheet("QPushButton { background-color: transparent; color: #F2EFEB; border: 1px solid #2A2621; padding: 6px 20px; border-radius: 6px; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; font-weight: 600; margin-left: 15px; } QPushButton:hover { border-color: #5865F2; }")
        top_layout.addWidget(save_btn)
        
        # Right side wrapper (Top bar + Stack)
        right_wrapper = QWidget()
        right_layout = QVBoxLayout(right_wrapper)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        right_layout.addWidget(top_bar)
        
        # Stacked Widget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #0F0E0C;")
        right_layout.addWidget(self.stack)
        
        main_layout.addWidget(right_wrapper, stretch=1)
        
        self.setCentralWidget(main_widget)
        
        # Map modules to their views
        # Note: Indexing must account for the header rows in sidebar!
        nav_indexes = []
        for i in range(self.sidebar.count()):
            if self.sidebar.item(i).flags() & Qt.ItemIsSelectable:
                nav_indexes.append(i)
                
        # Initialize views for selectable items
        # 1: Generate, 3: Voice Models, 4: Voice Memory, 5: Training
        # 7: Post Processing, 9: History, 10: Settings
        
        def create_placeholder(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #7A7265; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl
            
        for i in range(len(sidebar_structure)):
            label, icon_name = sidebar_structure[i]
            if icon_name is None:
                self.stack.addWidget(QWidget()) # Empty widget for header index
                continue
                
            try:
                if label == "Generate":
                    from legends_labs.modules.voice_clone.views.clone_view import CloneView
                    widget = CloneView()
                elif label == "Post Processing":
                    from legends_labs.modules.audio_post_production.views.audio_post_production_view import AudioPostProductionView
                    widget = AudioPostProductionView()
                elif label == "Voice Models":
                    from legends_labs.modules.model_manager.views.download_center_view import DownloadCenterView
                    widget = DownloadCenterView()
                elif label == "Settings":
                    from legends_labs.modules.settings.views.settings_view import SettingsView
                    widget = SettingsView()
                elif label == "Training & Datasets":
                    from legends_labs.modules.voice_clone.views.training_datasets_view import TrainingDatasetsView
                    widget = TrainingDatasetsView()
                else:
                    widget = create_placeholder(f"{label} Workspace Placeholder")
            except ImportError as e:
                widget = create_placeholder(f"{label} Module (Error: {e})")
                
            self.stack.addWidget(widget)
            
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(1) # Select 'Generate'
        
        from PySide6.QtCore import QTimer
        get_vram_manager().vram_updated.connect(self.vram_ind.update_vram)
        get_vram_manager().update_vram()
        
        self.vram_timer = QTimer(self)
        self.vram_timer.timeout.connect(get_vram_manager().update_vram)
        self.vram_timer.start(5000)

    def _on_sidebar_item_changed(self, current, previous):
        pass
