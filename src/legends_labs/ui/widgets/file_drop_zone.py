import os
from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".alac", ".opus", ".webm"}

class FileDropZone(QLabel):
    file_selected = Signal(str)

    def __init__(self, text="Drop audio recording here\n(or double-click to browse)", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #5865F2; border-radius: 10px; background-color: #1e1e1e; color: #888888; padding: 40px; font-size: 16px;")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.selected_file = ""

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    self.setText(f"Unsupported format: {ext}\nUse WAV, MP3, MP4, M4A, FLAC, OGG, AAC")
                    self.setStyleSheet("border: 2px dashed #f04747; border-radius: 10px; background-color: #1e1e1e; color: #f04747; padding: 40px; font-size: 16px;")
                    return
                self.setStyleSheet("border: 2px dashed #43b581; border-radius: 10px; background-color: #1e1e1e; color: #43b581; padding: 40px; font-size: 16px;")
                self.selected_file = file_path
                self.setText(f"✓ Selected: {os.path.basename(file_path)}")
                self.file_selected.emit(file_path)

    def mouseDoubleClickEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio File", 
            "", 
            "Audio Files (*.wav *.mp3 *.mp4 *.m4a *.flac *.ogg *.aac *.wma *.alac *.opus *.webm);;All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.setText(f"✓ Selected: {os.path.basename(file_path)}")
            self.file_selected.emit(file_path)
