import os
import soundfile as sf
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from legends_labs.ui.widgets.waveform_widget import WaveformWidget
from legends_labs.audio.audio_engine import AudioEngine

class AudioPlayerWidget(QWidget):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.engine = AudioEngine(self)
        self.setup_ui(title)
        self.connect_signals()
        
    def setup_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            layout.addWidget(lbl)
            
        # Waveform
        self.waveform = WaveformWidget()
        self.waveform.setMinimumHeight(80)
        layout.addWidget(self.waveform)
        
        # Transport
        transport = QHBoxLayout()
        
        self.btn_play = QPushButton()
        self.btn_stop = QPushButton()
        
        style = self.style()
        import PySide6.QtWidgets as QtWidgets
        self.btn_play.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_stop.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaStop))
        
        for btn in [self.btn_play, self.btn_stop]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("background-color: #242424; border-radius: 16px; border: 1px solid #333333;")
            transport.addWidget(btn)
            
        self.time_lbl = QLabel("00:00 / 00:00")
        self.time_lbl.setStyleSheet("color: #888888;")
        transport.addWidget(self.time_lbl)
        
        transport.addStretch()
        
        # Volume slider
        transport.addWidget(QLabel("", styleSheet="color: #888888;"))
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.setStyleSheet("QSlider::groove:horizontal { height: 4px; background: #333333; } QSlider::handle:horizontal { background: #5865F2; width: 10px; margin: -3px 0; border-radius: 5px; }")
        transport.addWidget(self.vol_slider)
        
        layout.addLayout(transport)
        
    def connect_signals(self):
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.engine.stop)
        self.vol_slider.valueChanged.connect(lambda v: self.engine.set_volume(v / 100.0))
        
        self.engine.position_changed.connect(self.on_position_changed)
        self.engine.duration_changed.connect(self.on_duration_changed)
        self.engine.state_changed.connect(self.on_state_changed)
        
        self.waveform.seek_requested.connect(self.on_seek_requested)
        
    def on_seek_requested(self, pos_ratio: float):
        duration = self.engine.duration
        if duration > 0:
            target_ms = int(duration * pos_ratio)
            self.engine.set_position(target_ms)
            
    def load_audio(self, file_path: str):
        if not os.path.exists(file_path):
            return
            
        self.engine.load(file_path)
        
        # Extract waveform data for visualizer
        try:
            # Read first channel only, downsample for speed if needed
            data, samplerate = sf.read(file_path, always_2d=True)
            mono_data = data[:, 0]
            # Downsample visually
            target_samples = 4000
            if len(mono_data) > target_samples:
                indices = np.linspace(0, len(mono_data) - 1, target_samples).astype(int)
                mono_data = mono_data[indices]
            self.waveform.set_audio_data(mono_data)
        except Exception as e:
            print(f"Error loading waveform visualizer: {e}")
            
    def toggle_play(self):
        if self.engine.state == 1:
            self.engine.pause()
        else:
            self.engine.play()
            
    def on_state_changed(self, state):
        import PySide6.QtWidgets as QtWidgets
        style = self.style()
        if state == 1: # Playing
            self.btn_play.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.btn_play.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            
    def on_duration_changed(self, duration_ms):
        self.update_time_label(self.engine.position, duration_ms)
        
    def on_position_changed(self, pos_ms):
        duration = self.engine.duration
        if duration > 0:
            self.waveform.playhead_pos = pos_ms / duration
            self.waveform.update()
        self.update_time_label(pos_ms, duration)
        
    def update_time_label(self, pos_ms, dur_ms):
        def format_ms(ms):
            s = ms // 1000
            m = s // 60
            s = s % 60
            return f"{m:02d}:{s:02d}"
        self.time_lbl.setText(f"{format_ms(pos_ms)} / {format_ms(dur_ms)}")
