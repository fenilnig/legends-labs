import random
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PySide6.QtCore import Qt, QTimer, QRectF

class AnimatedWaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.is_playing = False
        self.live_mode = False
        
        # Audio frequencies mock data
        self.bars = [0.1] * 40
        self.target_bars = [0.1] * 40
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(50)  # 20 fps

    def start_animation(self):
        self.is_playing = True
        self.live_mode = False

    def stop_animation(self):
        self.is_playing = False
        self.live_mode = False
        self.target_bars = [0.1] * 40

    def set_live_data(self, chunk):
        """Accepts a numpy array of audio data to visualize in real-time."""
        self.is_playing = True
        self.live_mode = True
        
        if len(chunk) == 0:
            return
            
        import numpy as np
        # Convert to 1D if stereo
        if chunk.ndim > 1:
            chunk = chunk[:, 0]
            
        # Calculate RMS for different segments
        n_bars = len(self.bars)
        segment_len = max(1, len(chunk) // n_bars)
        
        for i in range(n_bars):
            start = i * segment_len
            end = min(len(chunk), start + segment_len)
            segment = chunk[start:end]
            
            if len(segment) > 0:
                rms = np.sqrt(np.mean(segment**2))
                # Map RMS (typically 0.0 to 0.3 for speech) to 0.1-1.0
                mapped = min(1.0, (rms * 4.0) + 0.1)
                self.target_bars[i] = mapped
            else:
                self.target_bars[i] = 0.1

    def update_waveform(self):
        if self.is_playing and not self.live_mode:
            # Generate new random target heights to simulate audio
            for i in range(len(self.target_bars)):
                if __import__("random").random() > 0.4:
                    self.target_bars[i] = __import__("random").uniform(0.2, 0.9)
                else:
                    self.target_bars[i] = __import__("random").uniform(0.1, 0.3)
        elif not self.is_playing:
            # Low idle animation (breathing effect)
            t = __import__("time").time()
            for i in range(len(self.target_bars)):
                self.target_bars[i] = 0.1 + (__import__("math").sin(t * 2 + i * 0.2) * 0.05)
                
        # Interpolate current bars towards target
        needs_update = False
        for i in range(len(self.bars)):
            diff = self.target_bars[i] - self.bars[i]
            if abs(diff) > 0.005:
                self.bars[i] += diff * 0.2
                needs_update = True
                
        if needs_update or not self.is_playing:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        if width == 0 or height == 0:
            return
            
        # Solid core path
        path = __import__("PySide6.QtGui").QtGui.QPainterPath()
        center_y = height / 2.0
        
        points = []
        n_points = len(self.bars)
        step = width / max(1, n_points - 1)
        
        for i, val in enumerate(self.bars):
            x = i * step
            amplitude = (val * height / 2.0)
            points.append(__import__("PySide6.QtCore").QtCore.QPointF(x, center_y - amplitude))
            
        if points:
            path.moveTo(points[0])
            for i in range(1, len(points)):
                p0 = points[i-1]
                p1 = points[i]
                c1 = __import__("PySide6.QtCore").QtCore.QPointF((p0.x() + p1.x()) / 2, p0.y())
                c2 = __import__("PySide6.QtCore").QtCore.QPointF((p0.x() + p1.x()) / 2, p1.y())
                path.cubicTo(c1, c2, p1)
                
            bottom_points = []
            for i in reversed(range(n_points)):
                x = i * step
                amplitude = (self.bars[i] * height / 2.0)
                bottom_points.append(__import__("PySide6.QtCore").QtCore.QPointF(x, center_y + amplitude))
                
            path.lineTo(bottom_points[0])
            for i in range(1, len(bottom_points)):
                p0 = bottom_points[i-1]
                p1 = bottom_points[i]
                c1 = __import__("PySide6.QtCore").QtCore.QPointF((p0.x() + p1.x()) / 2, p0.y())
                c2 = __import__("PySide6.QtCore").QtCore.QPointF((p0.x() + p1.x()) / 2, p1.y())
                path.cubicTo(c1, c2, p1)
                
            path.closeSubpath()
            
        # Draw soft outer glow / shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(88, 101, 242, 20)) # Very soft
        painter.translate(0, 4)
        painter.drawPath(path)
        painter.translate(0, -4)
        
        # Fill
        gradient = QLinearGradient(0, 0, width, 0)
        gradient.setColorAt(0.0, QColor(71, 82, 196, 180)) # Semi-transparent
        gradient.setColorAt(1.0, QColor(88, 101, 242, 180))
        
        painter.setBrush(gradient)
        
        # Stroke (Core signal line)
        pen = QPen(QColor(255, 255, 255, 80))
        pen.setWidth(2)
        painter.setPen(pen)
        
        painter.drawPath(path)
