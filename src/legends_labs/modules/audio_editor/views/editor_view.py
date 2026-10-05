from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QGroupBox, QSpacerItem, QSizePolicy, QFileDialog)
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from legends_labs.ui.widgets.waveform_widget import WaveformWidget
from legends_labs.ui.widgets.pipeline_view import PipelineView
from legends_labs.core.pipeline import ProcessingPipeline

class EditorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title & Toolbar
        header = QHBoxLayout()
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("editor").pixmap(24, 24))
        
        lbl = QLabel("Audio Editor")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        
        toolbar = QHBoxLayout()
        self.btn_trim = QPushButton(" Trim")
        self.btn_fade_in = QPushButton(" Fade In")
        self.btn_fade_out = QPushButton(" Fade Out")
        self.btn_normalize = QPushButton(" Normalize")
        self.btn_compress = QPushButton(" Compress")
        
        self.current_file = ""
        
        for btn in [self.btn_trim, self.btn_fade_in, self.btn_fade_out, self.btn_normalize, self.btn_compress]:
            btn.setStyleSheet("""
                QPushButton { background-color: #242424; color: #e0e0e0; padding: 6px 12px; border-radius: 4px; border: 1px solid #333333; }
                QPushButton:hover { background-color: #333333; border: 1px solid #5865F2; }
            """)
            toolbar.addWidget(btn)
            
        self.btn_normalize.clicked.connect(lambda: self.run_effect("normalize"))
        self.btn_trim.clicked.connect(lambda: self.run_effect("trim", start_ms=0, end_ms=5000))
        self.btn_fade_in.clicked.connect(lambda: self.run_effect("fade", fade_in_ms=2000))
        self.btn_fade_out.clicked.connect(lambda: self.run_effect("fade", fade_out_ms=2000))
        self.btn_compress.clicked.connect(lambda: self.run_effect("compression"))
        
        header.addStretch()
        header.addLayout(toolbar)
        layout.addLayout(header)

        # File picker row
        file_row = QHBoxLayout()
        self.btn_open_file = QPushButton(" Open Audio File")
        self.btn_open_file.setStyleSheet("""
            QPushButton { background-color: #5865F2; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #4752c4; }
        """)
        self.btn_open_file.clicked.connect(self.open_file_dialog)
        file_row.addWidget(self.btn_open_file)

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #888888; font-size: 13px;")
        file_row.addWidget(self.file_label)
        file_row.addStretch()
        layout.addLayout(file_row)
        
        # Main content area
        content = QHBoxLayout()
        
        # Left: Waveform
        wave_layout = QVBoxLayout()
        self.waveform = WaveformWidget()
        wave_layout.addWidget(self.waveform)
        
        # Transport controls
        transport = QHBoxLayout()
        transport.setAlignment(Qt.AlignCenter)
        transport_actions = [
            ("⏮", "Rewind"),
            ("⏸", "Pause"),
            ("", "Play"),
            ("⏭", "Forward"),
            ("", "Stop"),
        ]
        for icon, action_name in transport_actions:
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("background-color: #242424; border-radius: 20px; font-size: 16px; border: 1px solid #333333;")
            btn.clicked.connect(lambda checked, a=action_name: self.on_transport_action(a))
            transport.addWidget(btn)
        wave_layout.addLayout(transport)
        
        content.addLayout(wave_layout, stretch=3)
        
        # Right: Properties Panel (EQ & Dynamics)
        props_layout = QVBoxLayout()
        
        eq_group = QGroupBox("Parametric EQ")
        eq_v = QVBoxLayout()
        self.eq_sliders = {}
        for band in ["Low Cut (Hz)", "Mid Boost (dB)", "Presence (dB)", "High Cut (Hz)"]:
            eq_v.addWidget(QLabel(band, styleSheet="color: #888888;"))
            slider = QSlider(Qt.Horizontal)
            slider.setStyleSheet("QSlider::groove:horizontal { height: 4px; background: #333333; } QSlider::handle:horizontal { background: #5865F2; width: 12px; margin: -4px 0; border-radius: 6px; }")
            self.eq_sliders[band] = slider
            eq_v.addWidget(slider)
        eq_group.setLayout(eq_v)
        props_layout.addWidget(eq_group)
        
        dyn_group = QGroupBox("Dynamics")
        dyn_v = QVBoxLayout()
        self.dynamics_sliders = {}
        for param in ["Compression Ratio", "Threshold (dB)", "Makeup Gain"]:
            dyn_v.addWidget(QLabel(param, styleSheet="color: #888888;"))
            slider = QSlider(Qt.Horizontal)
            slider.setStyleSheet("QSlider::groove:horizontal { height: 4px; background: #333333; } QSlider::handle:horizontal { background: #5865F2; width: 12px; margin: -4px 0; border-radius: 6px; }")
            self.dynamics_sliders[param] = slider
            dyn_v.addWidget(slider)
        dyn_group.setLayout(dyn_v)
        props_layout.addWidget(dyn_group)
        
        # AI History Pipeline View
        self.pipeline = ProcessingPipeline("project_123")
        self.pipeline_view = PipelineView(self.pipeline)
        props_layout.addWidget(self.pipeline_view, stretch=1)
        
        content.addLayout(props_layout, stretch=1)
        
        layout.addLayout(content)

    def on_transport_action(self, action: str):
        print(f"[Audio Editor] Transport: {action}")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.aac *.m4a);;All Files (*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_label.setText(file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1])
            print(f"[Audio Editor] Loaded file: {file_path}")

    def run_effect(self, operation: str, **kwargs):
        from legends_labs.modules.audio_editor.workers.editor_worker import EditorWorker
        from legends_labs.core.task_queue import task_queue
        
        # Add to pipeline
        node = self.pipeline.add_node(operation, kwargs)
        self.pipeline_view.refresh()
        
        # Disable buttons while running
        self.btn_trim.setEnabled(False)
        self.btn_fade_in.setEnabled(False)
        self.btn_fade_out.setEnabled(False)
        self.btn_normalize.setEnabled(False)
        self.btn_compress.setEnabled(False)
        
        worker = EditorWorker(operation=operation, audio_path=self.current_file, **kwargs)
        
        def on_finished():
            self.btn_trim.setEnabled(True)
            self.btn_fade_in.setEnabled(True)
            self.btn_fade_out.setEnabled(True)
            self.btn_normalize.setEnabled(True)
            self.btn_compress.setEnabled(True)
            node.is_dirty = False
            self.pipeline_view.refresh()
            
        worker.signals.finished.connect(on_finished)
        worker.signals.result.connect(lambda p: print(f"Saved edited audio to {p}"))
        
        task_queue.submit(worker)
