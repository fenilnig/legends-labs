import random
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QTimer

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(1.0, 3.0)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.5)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        # Gold/amber glowing dust
        self.color = QColor(245, 196, 0)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

class ParticleOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        self.particles = []
        self.is_active = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_particles)
        # 30 fps is enough for subtle dust
        self.timer.setInterval(33)
        
    def start_emission(self):
        self.is_active = True
        self.timer.start()
        
    def stop_emission(self):
        self.is_active = False
        # Let particles die out naturally, timer stops when empty
        
    def _update_particles(self):
        if self.is_active:
            # Spawn new particles randomly (low density)
            if random.random() > 0.6:
                # Spawn near the bottom edge
                px = random.uniform(0, self.width())
                py = self.height()
                self.particles.append(Particle(px, py))
                
        # Update and cull
        alive = []
        for p in self.particles:
            p.update()
            if p.life > 0:
                alive.append(p)
                
        self.particles = alive
        
        if not self.is_active and not self.particles:
            self.timer.stop()
            
        self.update()
        
    def paintEvent(self, event):
        if not self.particles:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        for p in self.particles:
            # Calculate alpha based on life (0-255)
            # Max alpha very low (e.g. 150) so it's subtle dust
            alpha = int(max(0, min(150, p.life * 150)))
            p.color.setAlpha(alpha)
            painter.setBrush(p.color)
            painter.drawEllipse(int(p.x), int(p.y), int(p.size), int(p.size))
