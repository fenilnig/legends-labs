from PySide6.QtWidgets import QSlider
from PySide6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient
from PySide6.QtCore import Qt, QPropertyAnimation, QRectF, QEasingCurve, Property

class PremiumSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(24)
        
        self._hover_progress = 0.0
        
        self.hover_anim = QPropertyAnimation(self, b"hoverProgress")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.OutQuad)

    @Property(float)
    def hoverProgress(self):
        return self._hover_progress

    @hoverProgress.setter
    def hoverProgress(self, val):
        self._hover_progress = val
        self.update()

    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Track
        track_h = 4
        track_y = (h - track_h) / 2
        track_rect = QRectF(0, track_y, w, track_h)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1E1E1E"))
        painter.drawRoundedRect(track_rect, track_h/2, track_h/2)
        
        # Fill
        min_val = self.minimum()
        max_val = self.maximum()
        val = self.value()
        
        if max_val > min_val:
            ratio = (val - min_val) / (max_val - min_val)
        else:
            ratio = 0
            
        fill_w = w * ratio
        fill_rect = QRectF(0, track_y, fill_w, track_h)
        
        fill_grad = QLinearGradient(0, 0, w, 0)
        fill_grad.setColorAt(0.0, QColor("#4752C4"))
        fill_grad.setColorAt(1.0, QColor("#5865F2"))
        
        painter.setBrush(fill_grad)
        painter.drawRoundedRect(fill_rect, track_h/2, track_h/2)
        
        # Glow Effect on Hover (very subtle)
        if self._hover_progress > 0:
            glow_h = track_h + (4 * self._hover_progress)
            glow_rect = QRectF(0, (h - glow_h)/2, fill_w, glow_h)
            painter.setBrush(QColor(88, 101, 242, int(30 * self._hover_progress)))
            painter.drawRoundedRect(glow_rect, glow_h/2, glow_h/2)
        
        # Handle
        handle_size = 12 + (4 * self._hover_progress)
        handle_x = fill_w - (handle_size / 2)
        # Keep handle within bounds
        handle_x = max(0, min(w - handle_size, handle_x))
        handle_y = (h - handle_size) / 2
        
        handle_rect = QRectF(handle_x, handle_y, handle_size, handle_size)
        
        painter.setBrush(QColor("#F2EFEB"))
        
        # Handle border (shadow simulation)
        border_c = QColor(0, 0, 0, 100)
        painter.setPen(border_c)
        painter.drawEllipse(handle_rect)
