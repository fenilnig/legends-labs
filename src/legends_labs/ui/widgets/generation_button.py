from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPainterPath
from PySide6.QtCore import Qt, QPropertyAnimation, QRectF, QEasingCurve, Property, Signal

class GenerationButton(QWidget):
    clicked = Signal()

    def __init__(self, text="Generate Voiceover", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(56)
        
        self.text = text
        self._progress = 0.0
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._is_generating = False
        
        self.hover_anim = QPropertyAnimation(self, b"hoverProgress")
        self.hover_anim.setDuration(150)
        self.hover_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        self.press_anim = QPropertyAnimation(self, b"pressProgress")
        self.press_anim.setDuration(100)
        
    def set_progress(self, val):
        # val 0 to 100
        self._progress = max(0.0, min(100.0, val))
        self.update()
        
    def set_generating(self, state):
        self._is_generating = state
        if state:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)
        self.update()

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
        self.update()

    def enterEvent(self, event):
        if not self._is_generating and self.isEnabled():
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
        if event.button() == Qt.LeftButton and not self._is_generating and self.isEnabled():
            self.press_anim.stop()
            self.press_anim.setEndValue(1.0)
            self.press_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self._is_generating and self.isEnabled():
            self.press_anim.stop()
            self.press_anim.setEndValue(0.0)
            self.press_anim.start()
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Scaling for press effect
        scale = 1.0 - (0.02 * self._press_progress)
        
        painter.translate(w/2, h/2)
        painter.scale(scale, scale)
        painter.translate(-w/2, -h/2)
        
        rect = QRectF(0, 0, w, h)
        radius = 8.0
        
        # Base Color
        if self.isEnabled() or self._is_generating:
            base_bg = QColor("#5865F2")
            hover_bg = QColor("#4752C4")
        else:
            base_bg = QColor("#333333")
            hover_bg = QColor("#333333")
            
        r = base_bg.red() + (hover_bg.red() - base_bg.red()) * self._hover_progress
        g = base_bg.green() + (hover_bg.green() - base_bg.green()) * self._hover_progress
        b = base_bg.blue() + (hover_bg.blue() - base_bg.blue()) * self._hover_progress
        bg = QColor(int(r), int(g), int(b))
        
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        # Draw Progress Fill
        if self._is_generating and self._progress > 0:
            fill_w = w * (self._progress / 100.0)
            fill_rect = QRectF(0, 0, fill_w, h)
            
            # Subtle animated shimmer on the fill
            import time, math
            t = time.time()
            shimmer_offset = (t % 2.0) / 2.0
            
            fill_grad = QLinearGradient(0, 0, w, 0)
            fill_grad.setColorAt(0.0, QColor("#4752C4"))
            fill_grad.setColorAt(max(0.0, min(1.0, shimmer_offset)), QColor("#6B77FF"))
            fill_grad.setColorAt(1.0, QColor("#4752C4"))
            
            painter.setBrush(fill_grad)
            path = QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            painter.setClipPath(path)
            painter.drawRect(fill_rect)
            painter.setClipping(False)
            
        # Subtle top highlight (Glass/Bevel effect)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)
        highlight_grad = QLinearGradient(0, 0, 0, h)
        highlight_grad.setColorAt(0.0, QColor(255, 255, 255, 30))
        highlight_grad.setColorAt(0.3, QColor(255, 255, 255, 0))
        painter.fillRect(rect, highlight_grad)
        painter.setClipping(False)
        
        # Text
        painter.setPen(QColor("#FFFFFF") if self.isEnabled() else QColor("#888888"))
        font = painter.font()
        font.setFamily("'Segoe UI', 'Inter', sans-serif")
        font.setPointSize(12)
        font.setWeight(font.Weight.Bold)
        painter.setFont(font)
        
        display_text = self.text
        if self._is_generating:
            display_text = f"Generating... {int(self._progress)}%"
            
        painter.drawText(rect, Qt.AlignCenter, display_text)
