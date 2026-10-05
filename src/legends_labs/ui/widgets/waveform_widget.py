from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath
from PySide6.QtCore import Qt, Signal, QRectF, QTimer
import numpy as np

class WaveformWidget(QWidget):
    playhead_moved = Signal(float)
    seek_requested = Signal(float) # 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        
        # Dummy data for visualization if no audio is loaded
        self.audio_data = np.random.randn(1000) * 0.5 
        self.playhead_pos = 0.3 # 30% through
        
        # Live Animation setup
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate_step)
        self.anim_phase = 0.0
        self.is_animating = False
        self.anim_type = "idle" # "idle", "generating", "recording"

    def set_audio_data(self, data: np.ndarray):
        self.audio_data = data
        self.update()
        
    def start_animation(self, anim_type="generating"):
        self.anim_type = anim_type
        self.is_animating = True
        self.animation_timer.start(30) # ~33 fps
        self.update()
        
    def stop_animation(self):
        self.is_animating = False
        self.animation_timer.stop()
        self.update()
        
    def _animate_step(self):
        self.anim_phase += 0.15
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        mid_y = height / 2
        
        # Background
        painter.fillRect(rect, QColor("#1a1a1a"))
        
        # Draw Waveform Gradient setup
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0.0, QColor("#5865F2"))
        gradient.setColorAt(1.0, QColor("#8b5cf6"))
        
        # 1. Live Undulating Wave Animation for Generating/Recording
        if self.is_animating and self.anim_type in ["generating", "recording"]:
            path = QPainterPath()
            path.moveTo(0, mid_y)
            
            # Draw multiple waves for a rich overlap effect
            for wave_idx in range(3):
                path.moveTo(0, mid_y)
                phase_offset = wave_idx * np.pi / 3
                frequency_scale = 1.0 + wave_idx * 0.5
                amplitude_scale = 0.6 if wave_idx > 0 else 1.0
                
                for x in range(0, width, 4):
                    val = np.sin(x / 30.0 * frequency_scale + self.anim_phase + phase_offset) * \
                          np.cos(x / 60.0 * frequency_scale - self.anim_phase)
                    edge_damp = np.sin(x / width * np.pi)
                    amp = val * (height / 2.8) * edge_damp * amplitude_scale
                    path.lineTo(x, mid_y + amp)
                    
            pen = QPen(gradient, 1.8)
            painter.setPen(pen)
            painter.drawPath(path)
            return
            
        if self.audio_data is None or len(self.audio_data) == 0:
            return
            
        # Draw Smooth Waveform Path (Continuous Polygon envelope)
        samples_per_pixel = max(1, len(self.audio_data) // width)
        
        path = QPainterPath()
        path.moveTo(0, mid_y)
        
        envelope_upper = []
        envelope_lower = []
        
        for x in range(0, width, 2):
            start_idx = x * samples_per_pixel
            end_idx = min(len(self.audio_data), (x + 2) * samples_per_pixel)
            
            if start_idx < len(self.audio_data):
                chunk = self.audio_data[start_idx:end_idx]
                if len(chunk) > 0:
                    max_val = np.max(chunk)
                    min_val = np.min(chunk)
                    amp_max = (max_val * height / 2) * 0.92
                    amp_min = (min_val * height / 2) * 0.92
                    envelope_upper.append((x, mid_y - max(0.5, amp_max)))
                    envelope_lower.append((x, mid_y - min(-0.5, amp_min)))
                    
        if envelope_upper and envelope_lower:
            for x_val, y_val in envelope_upper:
                path.lineTo(x_val, y_val)
            for x_val, y_val in reversed(envelope_lower):
                path.lineTo(x_val, y_val)
            path.closeSubpath()
            
            # Fill the smooth path with gradient
            painter.fillPath(path, QBrush(gradient))
            
        # Draw Playhead
        playhead_x = int(width * self.playhead_pos)
        pen = QPen(QColor("#f04747"), 2)
        painter.setPen(pen)
        painter.drawLine(playhead_x, 0, playhead_x, height)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.position().x()
            pos_ratio = x / self.width()
            pos_ratio = max(0.0, min(1.0, pos_ratio))
            self.seek_requested.emit(pos_ratio)
