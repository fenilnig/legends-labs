from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, Property

class ProgressRingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(40, 40)
        self.setMaximumSize(40, 40)
        self._progress = 0
        self._text = ""

    @Property(int)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val):
        self._progress = val
        self.update()

    def set_value(self, val, text=""):
        self._text = text
        
        # Smoothly animate the ring
        self.anim = QPropertyAnimation(self, b"progress")
        self.anim.setDuration(300)
        self.anim.setStartValue(self._progress)
        self.anim.setEndValue(val)
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw background ring
        pen_bg = QPen(QColor("#2A2A30"))
        pen_bg.setWidth(4)
        painter.setPen(pen_bg)
        
        rect = QRectF(4, 4, width-8, height-8)
        painter.drawEllipse(rect)
        
        # Draw progress arc
        pen_fg = QPen(QColor("#45E6B0"))
        pen_fg.setWidth(4)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)
        
        span_angle = int((self._progress / 100.0) * -360 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        # Draw text inside
        if self._progress > 0 and self._progress < 100:
            painter.setPen(QColor("#FFFFFF"))
            painter.setFont(QFont("Inter", 8, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, f"{self._progress}%")
        elif self._progress == 100:
            painter.setPen(QColor("#6B4CFF"))
            painter.setFont(QFont("Inter", 12, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, "✓")
