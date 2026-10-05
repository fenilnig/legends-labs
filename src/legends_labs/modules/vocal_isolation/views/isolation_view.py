from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QSlider, QProgressBar)
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from legends_labs.ui.widgets.file_drop_zone import FileDropZone

class IsolationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("isolation").pixmap(24, 24))
        
        lbl = QLabel("Vocal Isolation")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        # File Drop Zone
        self.drop_zone = FileDropZone()
        layout.addWidget(self.drop_zone)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        model_layout = QVBoxLayout()
        model_layout.addWidget(QLabel("AI Model"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["HTDemucs", "BS-RoFormer"])
        model_layout.addWidget(self.model_combo)
        controls_layout.addLayout(model_layout)
        
        stems_layout = QVBoxLayout()
        stems_layout.addWidget(QLabel("Stems to Extract"))
        checkboxes_layout = QHBoxLayout()
        self.cb_vocals = QCheckBox("Vocals")
        self.cb_vocals.setChecked(True)
        self.cb_drums = QCheckBox("Drums")
        self.cb_bass = QCheckBox("Bass")
        self.cb_other = QCheckBox("Other")
        checkboxes_layout.addWidget(self.cb_vocals)
        checkboxes_layout.addWidget(self.cb_drums)
        checkboxes_layout.addWidget(self.cb_bass)
        checkboxes_layout.addWidget(self.cb_other)
        stems_layout.addLayout(checkboxes_layout)
        controls_layout.addLayout(stems_layout)
        
        layout.addLayout(controls_layout)
        
        # Segment Size
        segment_layout = QHBoxLayout()
        segment_layout.addWidget(QLabel("Segment Size (VRAM Control)"))
        self.segment_slider = QSlider(Qt.Horizontal)
        self.segment_slider.setRange(5, 20)
        self.segment_slider.setValue(10)
        segment_layout.addWidget(self.segment_slider)
        self.segment_val = QLabel("10")
        self.segment_slider.valueChanged.connect(lambda v: self.segment_val.setText(str(v)))
        segment_layout.addWidget(self.segment_val)
        layout.addLayout(segment_layout)
        
        # Separate Button
        self.separate_btn = QPushButton("Separate Stems")
        self.separate_btn.setProperty("class", "primary-btn")
        self.separate_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        self.separate_btn.clicked.connect(self.start_separation)
        layout.addWidget(self.separate_btn)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { background-color: #242424; border-radius: 5px; color: #e0e0e0; text-align: center; }
            QProgressBar::chunk { background-color: #43b581; border-radius: 5px; }
        """)
        layout.addWidget(self.progress)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #43b581; font-weight: bold; margin-bottom: 10px;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setVisible(False)
        layout.addWidget(self.status_lbl)
        
        # Results Area
        self.results_layout = QVBoxLayout()
        layout.addLayout(self.results_layout)
        
        layout.addStretch()

    def start_separation(self):
        import os
        if not self.drop_zone.selected_file or not os.path.exists(self.drop_zone.selected_file):
            self.progress.setVisible(True)
            self.progress.setFormat("Error: Please select a valid audio file first.")
            return
            
        self.separate_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        
        self.status_lbl.setVisible(True)
        self.status_lbl.setText("Initializing AI Models... (Downloading models may take a few minutes on first run)")
        
        from legends_labs.modules.vocal_isolation.workers.separation_worker import SeparationWorker
        from legends_labs.core.task_queue import task_queue
        
        stems = []
        if self.cb_vocals.isChecked(): stems.append("Vocals")
        if self.cb_drums.isChecked(): stems.append("Drums")
        if self.cb_bass.isChecked(): stems.append("Bass")
        if self.cb_other.isChecked(): stems.append("Other")
        
        # Ensure outputs directory exists as absolute path
        out_dir = os.path.abspath(os.path.join(os.path.dirname(self.drop_zone.selected_file), "stems_output"))
        os.makedirs(out_dir, exist_ok=True)
        
        worker = SeparationWorker(
            audio_path=self.drop_zone.selected_file,
            model_name=self.model_combo.currentText(),
            stems=stems,
            segment_size=self.segment_slider.value(),
            output_dir=out_dir
        )
        
        # Keep track if it failed
        self.has_error = False
        
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.separation_finished)
        worker.signals.error.connect(self.separation_error)
        worker.signals.result.connect(self.show_results)
        
        task_queue.submit(worker)
        
    def update_progress(self, val, msg):
        self.progress.setRange(0, 100)
        self.progress.setValue(val)
        self.status_lbl.setText(msg)
        
    def separation_finished(self):
        self.separate_btn.setEnabled(True)
        if not self.has_error:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.status_lbl.setText("Complete! Stems extracted.")
        
    def separation_error(self, err_type, err_msg):
        self.has_error = True
        self.separate_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_lbl.setText(f"Error: {err_type}")
        print(f"Separation error: {err_msg}")
        
    def show_results(self, stems_dict):
        # Clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        lbl = QLabel("Extracted Stems:")
        lbl.setStyleSheet("color: #e0e0e0; font-weight: bold; margin-top: 10px;")
        self.results_layout.addWidget(lbl)
        
        from legends_labs.ui.widgets.audio_player import AudioPlayerWidget
        
        for stem_name, file_path in stems_dict.items():
            player = AudioPlayerWidget(title=f" {stem_name} ({os.path.basename(file_path)})")
            player.load_audio(file_path)
            self.results_layout.addWidget(player)
