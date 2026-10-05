from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
                               QLineEdit, QPushButton, QFormLayout, QGroupBox, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaDevices
from legends_labs.core.config import get_config
from legends_labs.ui.widgets.animated_waveform_widget import AnimatedWaveformWidget
import sounddevice as sd
import numpy as np
import queue

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setup_ui()
        
        self.media_devices = QMediaDevices(self)
        self.media_devices.audioInputsChanged.connect(self.populate_audio_devices)
        self.media_devices.audioOutputsChanged.connect(self.populate_audio_devices)
        self.populate_audio_devices()
        
    def populate_audio_devices(self):
        self.input_combo.blockSignals(True)
        self.output_combo.blockSignals(True)
        
        self.input_combo.clear()
        self.output_combo.clear()
        
        try:
            devices = sd.query_devices()
            saved_input = self.config.get("audio.input_device", "")
            saved_output = self.config.get("audio.output_device", "")
            
            in_idx, out_idx = 0, 0
            in_count, out_count = 0, 0
            
            seen_inputs = set()
            seen_outputs = set()
            
            for d in devices:
                name = d['name']
                if d['max_input_channels'] > 0 and name not in seen_inputs:
                    seen_inputs.add(name)
                    self.input_combo.addItem(name, d['name'])
                    if saved_input == name:
                        in_idx = in_count
                    in_count += 1
                if d['max_output_channels'] > 0 and name not in seen_outputs:
                    seen_outputs.add(name)
                    self.output_combo.addItem(name, d['name'])
                    if saved_output == name:
                        out_idx = out_count
                    out_count += 1
                    
            if self.input_combo.count() > 0:
                self.input_combo.setCurrentIndex(in_idx)
            if self.output_combo.count() > 0:
                self.output_combo.setCurrentIndex(out_idx)
                
        except Exception as e:
            print(f"Error querying devices: {e}")
            
        self.input_combo.blockSignals(False)
        self.output_combo.blockSignals(False)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("settings").pixmap(24, 24))
        
        lbl = QLabel("Settings")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #333333; background: #1e1e1e; border-radius: 4px; } QTabBar::tab { background: #242424; color: #888888; padding: 10px 20px; border: 1px solid #333333; } QTabBar::tab:selected { background: #5865F2; color: white; }")
        
        # General Tab with ElevenLabs API Key field
        general_tab = QWidget()
        gen_layout = QVBoxLayout(general_tab)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        
        el_group = QGroupBox("ElevenLabs API Integration")
        el_form = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.config.get("elevenlabs.api_key", ""))
        self.api_key_input.setPlaceholderText("Enter your ElevenLabs API Key here...")
        
        el_form.addRow("ElevenLabs API Key:", self.api_key_input)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(150)
        
        el_form.addRow("", save_btn)
        el_group.setLayout(el_form)
        
        gen_layout.addWidget(el_group)
        gen_layout.addStretch()
        
        self.tabs.addTab(general_tab, "General")
        
        # Audio Devices Tab
        audio_tab = QWidget()
        audio_layout = QVBoxLayout(audio_tab)
        audio_layout.setContentsMargins(20, 20, 20, 20)
        
        audio_group = QGroupBox("Hardware Configuration")
        audio_form = QFormLayout()
        
        self.input_combo = QComboBox()
        self.output_combo = QComboBox()
        
        audio_form.addRow("Input Device (Microphone):", self.input_combo)
        audio_form.addRow("Output Device (Speakers):", self.output_combo)
        
        audio_save_btn = QPushButton("Save Settings")
        audio_save_btn.clicked.connect(self.save_settings)
        audio_save_btn.setFixedWidth(150)
        
        audio_form.addRow("", audio_save_btn)
        audio_group.setLayout(audio_form)
        
        audio_layout.addWidget(audio_group)
        
        # Test Microphone Section
        test_group = QGroupBox("Microphone Test")
        test_layout = QVBoxLayout(test_group)
        
        self.test_mic_btn = QPushButton("Test Microphone")
        self.test_mic_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #333333; border-radius: 5px; } QPushButton:hover { background-color: #444444; }")
        self.test_mic_btn.clicked.connect(self.toggle_mic_test)
        
        self.waveform_widget = AnimatedWaveformWidget()
        
        test_layout.addWidget(self.test_mic_btn)
        test_layout.addWidget(self.waveform_widget)
        
        audio_layout.addWidget(test_group)
        audio_layout.addStretch()
        
        self.tabs.addTab(audio_tab, "Audio Devices")
        
        # Mic stream variables
        self.mic_stream = None
        self.mic_queue = queue.Queue()
        self.test_timer = __import__("PySide6.QtCore").QtCore.QTimer(self)
        self.test_timer.timeout.connect(self.process_mic_data)
        
        # Other Placeholders
        categories = ["GPU & VRAM", "Storage", "Shortcuts", "Export Defaults"]
        for cat in categories:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            lbl = QLabel(f"{cat} Settings (Coming Soon)")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #888888;")
            tab_layout.addWidget(lbl)
            self.tabs.addTab(tab, cat)
            
        layout.addWidget(self.tabs)
        
    def save_settings(self):
        # Save ElevenLabs API key
        key = self.api_key_input.text().strip()
        self.config.set("elevenlabs.api_key", key)
        
        # Save Audio Devices
        in_dev = self.input_combo.currentData()
        out_dev = self.output_combo.currentData()
        if in_dev:
            self.config.set("audio.input_device", in_dev)
        if out_dev:
            self.config.set("audio.output_device", out_dev)
            
        # Visual feedback
        sender = self.sender()
        if sender:
            sender.setText("Settings Saved! ✓")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: sender.setText("Save Settings"))

    def _audio_callback(self, indata, frames, time_info, status):
        self.mic_queue.put(indata.copy())
        
    def toggle_mic_test(self):
        if self.mic_stream is not None:
            self.stop_mic_test()
        else:
            self.start_mic_test()
            
    def start_mic_test(self):
        in_name = self.input_combo.currentText()
        if not in_name:
            return
            
        devices = sd.query_devices()
        dev_idx = None
        for i, d in enumerate(devices):
            if d['name'] == in_name and d['max_input_channels'] > 0:
                dev_idx = i
                break
                
        if dev_idx is None:
            return
            
        try:
            while not self.mic_queue.empty():
                self.mic_queue.get_nowait()
                
            self.mic_stream = sd.InputStream(device=dev_idx, samplerate=44100, channels=1, callback=self._audio_callback)
            self.mic_stream.start()
            self.test_timer.start(50)  # Check queue every 50ms (20fps)
            self.test_mic_btn.setText("Stop Test")
            self.test_mic_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #f04747; color: white; border-radius: 5px; }")
        except Exception as e:
            print(f"Failed to start mic test: {e}")
            self.stop_mic_test()
            
    def stop_mic_test(self):
        if self.mic_stream:
            self.mic_stream.stop()
            self.mic_stream.close()
            self.mic_stream = None
            
        self.test_timer.stop()
        self.waveform_widget.stop_animation()
        self.waveform_widget.update()
        self.test_mic_btn.setText("Test Microphone")
        self.test_mic_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #333333; border-radius: 5px; } QPushButton:hover { background-color: #444444; }")
        
    def process_mic_data(self):
        chunks = []
        while not self.mic_queue.empty():
            chunks.append(self.mic_queue.get_nowait())
            
        if chunks:
            data = np.concatenate(chunks, axis=0)
            self.waveform_widget.set_live_data(data)
            self.waveform_widget.update()
