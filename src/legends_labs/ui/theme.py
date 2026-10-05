from PySide6.QtGui import QColor, QPalette, QIcon
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from pathlib import Path

# Premium Cinematic Color Palette
class Colors:
    BACKGROUND_MAIN = "#121212" # Dark graphite
    BACKGROUND_SECONDARY = "#1E1E1E" # Neutral surface
    BACKGROUND_TERTIARY = "#262626" # Slightly lighter surface
    
    ACCENT_PRIMARY = "#5865F2" # Blue/Purple primary
    ACCENT_SECONDARY = "#4752C4"
    ACCENT_WARNING = "#F5C400" # Amber warning (Studio Gold)
    ACCENT_ERROR = "#F04747" # Cinematic red
    ACCENT_SUCCESS = "#43B581" # Green success
    
    TEXT_PRIMARY = "#F2EFEB"
    TEXT_SECONDARY = "#A89F91"
    TEXT_MUTED = "#6B6A68"
    
    BORDER_SUBTLE = "rgba(255, 255, 255, 0.05)" # Almost invisible divider

# Global Stylesheet
PREMIUM_STYLESHEET = f"""
    QWidget {{
        color: {Colors.TEXT_PRIMARY};
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}
    
    /* Main Window Gradient Background */
    QMainWindow, QDialog {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0A0A0A, stop:1 {Colors.BACKGROUND_MAIN});
    }}
    
    /* Borderless Group Boxes */
    QGroupBox {{
        background-color: transparent;
        border: none;
        margin-top: 10px;
        padding: 0px;
    }}
    QGroupBox::title {{
        color: {Colors.TEXT_PRIMARY};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-weight: 600;
        font-size: 16px;
        background-color: transparent;
    }}
    
    /* Input Fields (Prompt Editor) */
    QPlainTextEdit, QLineEdit {{
        background-color: transparent;
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: 8px;
        padding: 20px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 15px;
        color: {Colors.TEXT_PRIMARY};
        selection-background-color: rgba(88, 101, 242, 0.3);
    }}
    QPlainTextEdit:focus, QLineEdit:focus {{
        border: 1px solid rgba(88, 101, 242, 0.3);
        background-color: rgba(88, 101, 242, 0.01);
    }}
    
    /* We will replace buttons and sliders with custom classes, but provide a subtle fallback */
    QPushButton {{
        background-color: transparent;
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: 6px;
        padding: 10px 15px;
        color: {Colors.TEXT_PRIMARY};
    }}
    
    /* Combo Boxes (Frosted Glass Fallback) */
    QComboBox {{
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: 6px;
        padding: 8px 12px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: none;
    }}
    QComboBox:hover {{
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BACKGROUND_SECONDARY};
        border: 1px solid {Colors.BORDER_SUBTLE};
        selection-background-color: rgba(88, 101, 242, 0.2);
    }}
"""

def create_drop_shadow(blur_radius=20, offset_y=5, opacity=150):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(0)
    shadow.setYOffset(offset_y)
    shadow.setColor(QColor(0, 0, 0, opacity))
    return shadow

def load_theme(app):
    # Try to load the original dark theme QSS first
    qss_content = ""
    qss_path = Path(__file__).parent / "resources" / "styles" / "dark_theme.qss"
    if qss_path.exists():
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss_content = f.read()
        except Exception as e:
            print(f"Warning: Could not read dark_theme.qss: {e}")
            
    # Append our premium visual override styles
    merged_qss = qss_content + "\n" + PREMIUM_STYLESHEET
    app.setStyleSheet(merged_qss)
    
    # Set default palette just in case
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(Colors.BACKGROUND_MAIN))
    palette.setColor(QPalette.WindowText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(Colors.BACKGROUND_SECONDARY))
    palette.setColor(QPalette.AlternateBase, QColor(Colors.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ToolTipBase, QColor(Colors.BACKGROUND_TERTIARY))
    palette.setColor(QPalette.ToolTipText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.Text, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(Colors.BACKGROUND_SECONDARY))
    palette.setColor(QPalette.ButtonText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.BrightText, QColor(Colors.ACCENT_WARNING))
    palette.setColor(QPalette.Highlight, QColor(Colors.ACCENT_PRIMARY))
    palette.setColor(QPalette.HighlightedText, QColor(Colors.TEXT_PRIMARY))
    app.setPalette(palette)

def get_icon(name: str) -> QIcon:
    icon_path = Path(__file__).parent / "resources" / "icons" / f"{name}.svg"
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()
