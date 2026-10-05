import random
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QImage, QBrush
from PySide6.QtCore import Qt, QRect

class CinematicOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Pre-render a noise image once to save CPU
        self.noise_img = self._generate_noise_texture(256, 256)
        
    def _generate_noise_texture(self, w, h):
        img = QImage(w, h, QImage.Format_ARGB32)
        # Create subtle grain
        for y in range(h):
            for x in range(w):
                # We want mostly transparent, occasionally dark or light specks
                val = random.randint(0, 255)
                # Opacity between 1 and 4 for extremely subtle grain
                alpha = random.randint(1, 4)
                img.setPixelColor(x, y, QColor(val, val, val, alpha))
        return img
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        width = self.width()
        height = self.height()
        
        # 1. Draw Vignette (soft radial shadow from edges)
        gradient = QRadialGradient(width/2, height/2, width * 0.75)
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, 80)) # Subtle
        painter.fillRect(self.rect(), gradient)
        
        # 2. Draw Tiled Noise
        brush = QBrush(self.noise_img)
        painter.fillRect(self.rect(), brush)
