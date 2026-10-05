from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QSplitter, QScrollArea
from PySide6.QtCore import Qt

class StageEditingView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        header = QLabel("Professional Audio Editing & Effects")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        toolbar.addWidget(header)
        
        toolbar.addStretch()
        
        for act in ["Undo", "Redo", "A/B Compare", "Apply Rack"]:
            btn = QPushButton(act)
            btn.setStyleSheet("background-color: #333; color: white; padding: 5px 15px; border-radius: 4px;")
            toolbar.addWidget(btn)
            
        layout.addLayout(toolbar)
        
        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Effects Rack)
        rack_widget = QWidget()
        rack_layout = QVBoxLayout(rack_widget)
        rack_layout.setContentsMargins(0, 0, 0, 0)
        
        rack_lbl = QLabel("Effects Rack")
        rack_lbl.setStyleSheet("font-weight: bold; color: #a0a0a0;")
        rack_layout.addWidget(rack_lbl)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #333; background-color: #1a1a1a; }")
        
        rack_content = QWidget()
        self.rack_vbox = QVBoxLayout(rack_content)
        
        # Dummy Effects
        for effect in ["Parametric EQ", "Multiband Compressor", "Reverb", "Limiter"]:
            eff_frame = QFrame()
            eff_frame.setStyleSheet("background-color: #242424; border: 1px solid #444; border-radius: 4px;")
            eff_layout = QVBoxLayout(eff_frame)
            eff_lbl = QLabel(effect)
            eff_lbl.setStyleSheet("color: white; font-weight: bold;")
            eff_layout.addWidget(eff_lbl)
            
            # Simple slider
            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 100)
            sl.setValue(50)
            eff_layout.addWidget(sl)
            
            self.rack_vbox.addWidget(eff_frame)
            
        self.rack_vbox.addStretch()
        scroll.setWidget(rack_content)
        rack_layout.addWidget(scroll)
        
        splitter.addWidget(rack_widget)
        
        # Right Panel (Waveform / Spectrogram)
        vis_widget = QWidget()
        vis_layout = QVBoxLayout(vis_widget)
        vis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Waveform Placeholder (will integrate pyqtgraph)
        try:
            import pyqtgraph as pg
            self.waveform_plot = pg.PlotWidget(title="Waveform Visualization")
            self.waveform_plot.setBackground("#111")
            self.waveform_plot.showGrid(x=True, y=True, alpha=0.3)
            vis_layout.addWidget(self.waveform_plot, stretch=3)
        except ImportError:
            self.waveform_frame = QFrame()
            self.waveform_frame.setStyleSheet("background-color: #111; border: 1px solid #333;")
            wf_layout = QVBoxLayout(self.waveform_frame)
            wf_lbl = QLabel("Waveform / Spectrogram Visualization\n(Install pyqtgraph to view)")
            wf_lbl.setAlignment(Qt.AlignCenter)
            wf_lbl.setStyleSheet("color: #666; font-size: 16px;")
            wf_layout.addWidget(wf_lbl)
            vis_layout.addWidget(self.waveform_frame, stretch=3)
        
        # Mixer / Meters
        meter_frame = QFrame()
        meter_frame.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        meter_frame.setMinimumHeight(100)
        m_layout = QHBoxLayout(meter_frame)
        m_lbl = QLabel("RMS / LUFS Meters")
        m_lbl.setAlignment(Qt.AlignCenter)
        m_lbl.setStyleSheet("color: #666;")
        m_layout.addWidget(m_lbl)
        vis_layout.addWidget(meter_frame, stretch=1)
        
        splitter.addWidget(vis_widget)
        
        # Set splitter sizes
        splitter.setSizes([300, 900])
        layout.addWidget(splitter, stretch=1)
        
        # Navigation
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Back")
        self.prev_btn.clicked.connect(lambda: self.parent_view.switch_stage(3) if self.parent_view else None)
        
        self.next_btn = QPushButton("Finish & Export →")
        self.next_btn.setStyleSheet("background-color: #5865F2; color: white; font-weight: bold;")
        self.next_btn.clicked.connect(lambda: self.parent_view.switch_stage(5) if self.parent_view else None)
        
        for btn in [self.prev_btn, self.next_btn]:
            btn.setMinimumHeight(40)
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
