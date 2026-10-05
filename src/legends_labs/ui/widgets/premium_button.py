from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPainterPath
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QRectF, Property

class PremiumButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40) # Default height
        
        # We handle drawing manually to get pseudo-3D and gradients
        self.setStyleSheet("background: transparent; border: none; color: #F2EFEB; font-family: 'Segoe UI', 'Inter', sans-serif; font-weight: 500;")
        
        # Properties for animation
        self._hover_progress = 0.0
        self._press_progress = 0.0
        
        # Animations
        self.hover_anim = QPropertyAnimation(self, b"hoverProgress")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.press_anim = QPropertyAnimation(self, b"pressProgress")
        self.press_anim.setDuration(100)
        self.press_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # Soft shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

    @Property(float)
    def hoverProgress(self):
        return self._hover_progress

    @hoverProgress.setter
    def hoverProgress(self, val):
        self._hover_progress = val
        self.update()
        
    @Property(float)
    def pressProgress(self):
        return self._press_progress

    @pressProgress.setter
    def pressProgress(self, val):
        self._press_progress = val
        # Adjust shadow based on press
        self.shadow.setYOffset(4 - (3 * val))
        self.shadow.setBlurRadius(15 - (10 * val))
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press_anim.stop()
            self.press_anim.setEndValue(1.0)
            self.press_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press_anim.stop()
            self.press_anim.setEndValue(0.0)
            self.press_anim.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate visual rectangle (lift up on hover, scale down on press)
        w = self.width()
        h = self.height()
        
        # Hover lift: up to 2px up
        y_offset = -2 * self._hover_progress
        
        # Press compress: shrink slightly
        scale = 1.0 - (0.02 * self._press_progress)
        
        painter.translate(w/2, h/2)
        painter.scale(scale, scale)
        painter.translate(-w/2, -h/2 + y_offset)
        
        rect = QRectF(0, 0, w, h)
        
        # Base colors (Analog Graphite Theme)
        base_color = QColor("#1E1E1E")
        hover_color = QColor("#2A2A2A")
        
        # Interpolate background color
        r = base_color.red() + (hover_color.red() - base_color.red()) * self._hover_progress
        g = base_color.green() + (hover_color.green() - base_color.green()) * self._hover_progress
        b = base_color.blue() + (hover_color.blue() - base_color.blue()) * self._hover_progress
        bg = QColor(int(r), int(g), int(b))
        
        # Background
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 6, 6)
        
        # Subtle top highlight (Glass/Bevel effect)
        path = QPainterPath()
        path.addRoundedRect(rect, 6, 6)
        painter.setClipPath(path)
        
        highlight_grad = QLinearGradient(0, 0, 0, h)
        highlight_grad.setColorAt(0.0, QColor(255, 255, 255, 12))
        highlight_grad.setColorAt(0.2, QColor(255, 255, 255, 0))
        painter.fillRect(rect, highlight_grad)
        
        painter.setClipping(False)
        
        # Border
        border_color = QColor(255, 255, 255, 10 + int(10 * self._hover_progress))
        painter.setPen(border_color)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 6, 6)
        
        # Draw Text
        font = self.font()
        painter.setFont(font)
        
        # We set color in stylesheet but QPainter doesn't automatically inherit it if we don't use QStyle.
        # Let's extract the color or just use #F2EFEB
        painter.setPen(QColor("#F2EFEB"))
        painter.drawText(rect, Qt.AlignCenter, self.text())
