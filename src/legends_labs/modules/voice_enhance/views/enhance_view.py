from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QProgressBar
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from legends_labs.ui.widgets.file_drop_zone import FileDropZone

class EnhanceView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("enhance").pixmap(24, 24))
        
        lbl = QLabel("Voice Enhance")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        self.drop_zone = FileDropZone()
        layout.addWidget(self.drop_zone)
        
        controls = QVBoxLayout()
        
        controls.addWidget(QLabel("Noise Reduction Strength", styleSheet="color: #e0e0e0; font-weight: bold;"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(80)
        self.slider.setStyleSheet("QSlider::groove:horizontal { height: 6px; background: #333333; border-radius: 3px; } QSlider::handle:horizontal { background: #5865F2; width: 16px; margin: -5px 0; border-radius: 8px; }")
        controls.addWidget(self.slider)
        
        self.cb_clarity = QCheckBox("Voice Clarity Boost")
        self.cb_clarity.setChecked(True)
        controls.addWidget(self.cb_clarity)
        
        self.cb_dereverb = QCheckBox("De-Reverb")
        self.cb_dereverb.setChecked(True)
        controls.addWidget(self.cb_dereverb)
        
        layout.addLayout(controls)
        
        self.enhance_btn = QPushButton("Enhance Audio")
        self.enhance_btn.setStyleSheet("QPushButton { background-color: #5865F2; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 16px; } QPushButton:hover { background-color: #4752c4; }")
        self.enhance_btn.clicked.connect(self.start_enhancement)
        layout.addWidget(self.enhance_btn)
        
        self.progress = QLabel("")
        self.progress.setStyleSheet("color: #43b581; font-weight: bold;")
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)
        
        # Results Area
        self.results_layout = QVBoxLayout()
        layout.addLayout(self.results_layout)
        
        layout.addStretch()

    def start_enhancement(self):
        import os
        if not self.drop_zone.selected_file or not os.path.exists(self.drop_zone.selected_file):
            self.progress.setText("Error: Please select a valid audio file first.")
            return
            
        self.enhance_btn.setEnabled(False)
        self.progress.setStyleSheet("color: #43b581;")
        self.progress.setText("Initializing AI Model...")
        
        from legends_labs.modules.voice_enhance.workers.enhance_worker import EnhanceWorker
        from legends_labs.core.task_queue import task_queue
        
        worker = EnhanceWorker(
            audio_path=self.drop_zone.selected_file, 
            strength=self.slider.value(),
            clarity_boost=self.cb_clarity.isChecked(),
            dereverb=self.cb_dereverb.isChecked()
        )
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.enhancement_finished)
        worker.signals.result.connect(self.show_results)
        worker.signals.error.connect(self.show_error)
        
        task_queue.submit(worker)

    def update_progress(self, val, msg):
        self.progress.setText(f"{val}% - {msg}")
            
    def enhancement_finished(self):
        self.enhance_btn.setEnabled(True)

    def show_results(self, enhanced_path):
        self.progress.setText(f"100% - Saved enhanced audio to {enhanced_path}")
        
        # Clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        from legends_labs.ui.widgets.audio_player import AudioPlayerWidget
        
        # Before Player
        before_player = AudioPlayerWidget(title=" Before (Original)")
        before_player.load_audio(self.drop_zone.selected_file)
        self.results_layout.addWidget(before_player)
        
        # After Player
        after_player = AudioPlayerWidget(title=" After (Enhanced)")
        after_player.load_audio(enhanced_path)
        self.results_layout.addWidget(after_player)

    def show_error(self, err_type, err_msg):
        self.enhance_btn.setEnabled(True)
        self.progress.setStyleSheet("color: #f04747; font-weight: bold;")
        self.progress.setText(f"Error: {err_type}")
        print(f"Enhancement error [{err_type}]: {err_msg}")
