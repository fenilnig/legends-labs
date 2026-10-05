from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QLinearGradient
from PySide6.QtCore import Qt, QTimer
import time, math

class SignalLineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self.is_active = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(33) # 30fps
        
    def set_active(self, active):
        self.is_active = active
        if active:
            self.timer.start()
        else:
            self.timer.stop()
            self.update()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Base subtle line
        painter.fillRect(0, 0, w, h, QColor(255, 255, 255, 5))
        
        if self.is_active:
            t = time.time()
            # Animate 0.0 to 1.0 back to 0.0, or continuous sweeping?
            # A continuous sweeping signal
            progress = (t * 0.5) % 1.0 # Takes 2 seconds to cross
            
            # Draw a glowing segment
            segment_width = w * 0.15
            start_x = (w + segment_width) * progress - segment_width
            
            grad = QLinearGradient(start_x, 0, start_x + segment_width, 0)
            grad.setColorAt(0.0, QColor(88, 101, 242, 0))
            grad.setColorAt(0.5, QColor(88, 101, 242, 255))
            grad.setColorAt(1.0, QColor(88, 101, 242, 0))
            
            painter.fillRect(int(start_x), 0, int(segment_width), h, grad)
