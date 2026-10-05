from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap, QColor, QPainter, QFont, QLinearGradient, QPen, QBrush
from PySide6.QtCore import Qt, QRect

class AnimatedSplashScreen(QSplashScreen):
    def __init__(self):
        pix = QPixmap(600, 360)
        pix.fill(Qt.transparent)
        super().__init__(pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._progress = 0
        self._message = ""

    def drawContents(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw modern gradient background with rounded corners
        bg_gradient = QLinearGradient(0, 0, 0, 360)
        bg_gradient.setColorAt(0.0, QColor("#181614"))
        bg_gradient.setColorAt(1.0, QColor("#0a0908"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_gradient)
        painter.drawRoundedRect(0, 0, 600, 360, 16, 16)
        
        # Draw subtle border
        painter.setPen(QColor("#2a2722"))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, 600, 360, 16, 16)
        
        # Draw Logo Text
        logo_gradient = QLinearGradient(0, 0, 600, 0)
        logo_gradient.setColorAt(0.25, QColor("#D4AF37")) # Metallic Gold
        logo_gradient.setColorAt(0.75, QColor("#AA7E24")) # Deep Amber
        
        painter.setPen(QPen(QBrush(logo_gradient), 1))
        logo_font = QFont("Georgia", 48, QFont.Bold)
        logo_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
        painter.setFont(logo_font)
        # Increased QRect height to 120 and adjusted Y to 60 to prevent clipping descenders like 'g'
        painter.drawText(QRect(0, 60, 600, 120), Qt.AlignCenter, "Legend's Labs")
        
        # Draw Subtitle
        painter.setPen(QColor("#9E9585"))
        sub_font = QFont("Palatino Linotype", 13, QFont.Bold)
        sub_font.setLetterSpacing(QFont.AbsoluteSpacing, 6)
        painter.setFont(sub_font)
        painter.drawText(QRect(0, 165, 600, 30), Qt.AlignCenter, "AI VOICE STUDIO")
        
        # Draw Progress Bar Track
        bar_y = 260
        bar_height = 6
        bar_margin = 120
        bar_width = 600 - 2 * bar_margin
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#201e1a"))
        painter.drawRoundedRect(bar_margin, bar_y, bar_width, bar_height, bar_height//2, bar_height//2)
        
        # Draw Progress Fill
        if self._progress > 0:
            fill_width = int(bar_width * self._progress / 100)
            fill_gradient = QLinearGradient(bar_margin, 0, bar_margin + bar_width, 0)
            fill_gradient.setColorAt(0.0, QColor("#E5C158"))
            fill_gradient.setColorAt(1.0, QColor("#A88022"))
            painter.setBrush(fill_gradient)
            painter.drawRoundedRect(bar_margin, bar_y, fill_width, bar_height, bar_height//2, bar_height//2)
            
        # Draw Message
        painter.setPen(QColor("#8C8476"))
        msg_font = QFont("Palatino Linotype", 10)
        msg_font.setItalic(True)
        painter.setFont(msg_font)
        painter.drawText(QRect(0, bar_y + 20, 600, 30), Qt.AlignCenter, self._message)

    def showMessage(self, message: str, alignment: int = Qt.AlignBottom | Qt.AlignHCenter, color: QColor = QColor("#888888")):
        self._progress = min(100, self._progress + 50)
        self._message = message
        self.repaint()

