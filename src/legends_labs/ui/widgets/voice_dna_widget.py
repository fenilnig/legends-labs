import math
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath
from PySide6.QtCore import Qt, QTimer

class VoiceDNAWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.offset = 0
        self.active = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_active(self, is_active):
        self.active = is_active
        self.update()

    def animate(self):
        if self.active:
            self.offset += 0.15
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background subtle grid
        pen_grid = QPen(QColor(255, 255, 255, 10))
        pen_grid.setWidth(1)
        painter.setPen(pen_grid)
        for i in range(0, width, 20):
            painter.drawLine(i, 0, i, height)
        for i in range(0, height, 20):
            painter.drawLine(0, i, width, i)
        
        if not self.active:
            # Draw flat line if no voice data
            pen = QPen(QColor(255, 255, 255, 50))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, height/2, width, height/2)
            return
            
        # Draw dynamic DNA wave
        path = QPainterPath()
        path.moveTo(0, height/2)
        
        points = 100
        for i in range(points + 1):
            x = (i / points) * width
            # Complex sine wave combination
            y_offset1 = math.sin((i / 10.0) + self.offset) * 15
            y_offset2 = math.cos((i / 5.0) - self.offset * 1.5) * 10
            y = (height / 2) + y_offset1 + y_offset2
            path.lineTo(x, y)
            
        gradient = QLinearGradient(0, 0, width, 0)
        gradient.setColorAt(0.0, QColor("#6B4CFF"))
        gradient.setColorAt(0.5, QColor("#45E6B0"))
        gradient.setColorAt(1.0, QColor("#FF4C6A"))
        
        pen = QPen(gradient, 3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        # Draw second offset wave for depth
        path2 = QPainterPath()
        path2.moveTo(0, height/2)
        for i in range(points + 1):
            x = (i / points) * width
            y_offset1 = math.sin((i / 12.0) + self.offset * 1.2) * -12
            y_offset2 = math.cos((i / 7.0) - self.offset * 0.8) * -8
            y = (height / 2) + y_offset1 + y_offset2
            path2.lineTo(x, y)
            
        pen2 = QPen(QColor(107, 76, 255, 100), 2)
        painter.setPen(pen2)
        painter.drawPath(path2)
