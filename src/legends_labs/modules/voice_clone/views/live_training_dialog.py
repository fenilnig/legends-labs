import os
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import random

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QTextEdit, QMessageBox, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaDevices

from legends_labs.core.constants import CACHE_DIR

from legends_labs.modules.voice_clone.training_scripts import TRAINING_SCRIPTS

class LiveTrainingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Mic Training")
        self.setFixedSize(750, 580)
        self.setStyleSheet("background-color: #1a1a1a; color: #e0e0e0;")
        
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.stream = None
        self.samplerate = 44100
        self.channels = 1
        self.saved_file_path = None
        self.active_device_index = None
        
        self.setup_ui()
        
        # Hardware Event Listener for Hot-Plugging
        self.media_devices = QMediaDevices(self)
        self.media_devices.audioInputsChanged.connect(self.on_audio_inputs_changed)
        # Run a scan on startup
        self.on_audio_inputs_changed()
        
    def on_audio_inputs_changed(self):
        devices = sd.query_devices()
        best_device_id = None
        best_device_name = None
        
        # Keywords to search for a premium mic
        target_keywords = ["fifine", "maono", "yeti", "shure", "rode", "elgato", "hyperx", "external", "usb", "microphone array"]
        
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = dev['name'].lower()
                for kw in target_keywords:
                    if kw in name:
                        best_device_id = i
                        best_device_name = dev['name']
                        break
            if best_device_id is not None:
                break
                
        if best_device_id is not None:
            self.active_device_index = best_device_id
            try:
                self.status_label.setText(f"Mic Connected: {best_device_name}")
                self.status_label.setStyleSheet("color: #43b581; font-weight: bold;")
            except AttributeError:
                pass # status_label might not be initialized yet on first call
        else:
            self.active_device_index = None
            try:
                self.status_label.setText("Ready to record (System Default Mic)")
                self.status_label.setStyleSheet("color: #888888; font-weight: bold;")
            except AttributeError:
                pass

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Live Voice Training Studio")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #5865F2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        inst = QLabel("Read the following sentence clearly and naturally:")
        inst.setStyleSheet("font-size: 14px; color: #888888;")
        inst.setAlignment(Qt.AlignCenter)
        layout.addWidget(inst)
        
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(TRAINING_SCRIPTS.keys()))
        self.category_combo.setStyleSheet("padding: 5px; background: #242424; color: #e0e0e0; border: 1px solid #333333; border-radius: 4px; font-weight: bold;")
        self.category_combo.currentTextChanged.connect(self.new_sentence)
        layout.addWidget(self.category_combo)
        
        self.script_display = QTextEdit()
        self.script_display.setReadOnly(True)
        self.script_display.setMinimumHeight(240)
        self.script_display.setLineWrapMode(QTextEdit.WidgetWidth)
        self.script_display.setStyleSheet("background-color: #242424; color: #e0e0e0; font-size: 15px; padding: 20px; border: 1px solid #333333; border-radius: 8px; line-height: 1.6; font-family: 'Segoe UI', 'Inter', sans-serif;")
        layout.addWidget(self.script_display)
        self.new_sentence()
        
        # Controls
        ctrl_layout = QHBoxLayout()
        
        self.skip_btn = QPushButton("Skip / New Sentence")
        self.skip_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #333333; border-radius: 5px; } QPushButton:hover { background-color: #444444; }")
        self.skip_btn.clicked.connect(self.new_sentence)
        ctrl_layout.addWidget(self.skip_btn)
        
        self.record_btn = QPushButton("Start Recording")
        # Start button is red
        self.record_btn.setStyleSheet("QPushButton { padding: 10px 20px; font-weight: bold; font-size: 16px; background-color: #f04747; color: white; border-radius: 5px; } QPushButton:hover { background-color: #d84040; }")
        self.record_btn.clicked.connect(self.toggle_recording)
        ctrl_layout.addWidget(self.record_btn)
        
        layout.addLayout(ctrl_layout)
        
        self.status_label = QLabel("Ready to record.")
        self.status_label.setStyleSheet("color: #43b581; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def new_sentence(self):
        if not self.is_recording:
            category = self.category_combo.currentText()
            if category in TRAINING_SCRIPTS:
                self.script_display.setText(random.choice(TRAINING_SCRIPTS[category]))

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def start_recording(self):
        try:
            self.audio_data = []
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()
                
            self.stream = sd.InputStream(
                device=self.active_device_index,
                samplerate=self.samplerate, 
                channels=self.channels, 
                callback=self._audio_callback
            )
            self.stream.start()
            
            self.is_recording = True
            self.record_btn.setText("Stop & Save")
            # Stop button is warning/yellow
            self.record_btn.setStyleSheet("QPushButton { padding: 10px 20px; font-weight: bold; font-size: 16px; background-color: #faa61a; color: white; border-radius: 5px; } QPushButton:hover { background-color: #e39617; }")
            self.status_label.setText("Recording in progress...")
            self.status_label.setStyleSheet("color: #f04747; font-weight: bold;")
            self.skip_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Recording Error", f"Failed to access microphone:\n{e}")

    def stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        self.is_recording = False
        self.skip_btn.setEnabled(True)
        self.record_btn.setText("Start Recording")
        self.record_btn.setStyleSheet("QPushButton { padding: 10px 20px; font-weight: bold; font-size: 16px; background-color: #f04747; color: white; border-radius: 5px; } QPushButton:hover { background-color: #d84040; }")
        
        self.status_label.setText("Processing audio...")
        self.status_label.setStyleSheet("color: #43b581; font-weight: bold;")
        
        while not self.audio_queue.empty():
            self.audio_data.append(self.audio_queue.get())
            
        if self.audio_data:
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.saved_file_path = str(CACHE_DIR / f"live_training_{int(time.time())}.wav")
            
            sf.write(self.saved_file_path, audio_array, self.samplerate)
            self.saved_transcript = self.script_display.toPlainText().strip()
            self.accept() # Close dialog with success (returns QDialog.Accepted)
        else:
            QMessageBox.warning(self, "Warning", "No audio was captured.")
            self.status_label.setText("Ready.")
