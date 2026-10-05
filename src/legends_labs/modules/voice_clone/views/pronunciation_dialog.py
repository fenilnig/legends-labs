from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from legends_labs.modules.voice_clone.pronunciation_manager import pronunciation_manager

class PronunciationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pronunciation Dictionary")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")
        
        self.setup_ui()
        self.refresh_list()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        lbl = QLabel("Custom Pronunciations (G2P Override)")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl)
        
        # List of rules
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #242424; border: 1px solid #333333; padding: 5px;")
        layout.addWidget(self.list_widget)
        
        # Add new rule
        add_layout = QHBoxLayout()
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Word (e.g. Varuynmaya)")
        self.word_input.setStyleSheet("padding: 5px; background: #242424; border: 1px solid #333;")
        
        self.pron_input = QLineEdit()
        self.pron_input.setPlaceholderText("Pronunciation (e.g. Vuh-ROON my-YAH)")
        self.pron_input.setStyleSheet("padding: 5px; background: #242424; border: 1px solid #333;")
        
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("background-color: #43b581; color: white; padding: 5px; font-weight: bold; border-radius: 4px;")
        self.add_btn.clicked.connect(self.add_rule)
        
        add_layout.addWidget(self.word_input)
        add_layout.addWidget(self.pron_input)
        add_layout.addWidget(self.add_btn)
        
        layout.addLayout(add_layout)
        
        # Delete rule
        self.del_btn = QPushButton("Delete Selected")
        self.del_btn.setStyleSheet("background-color: #f04747; color: white; padding: 5px; border-radius: 4px; margin-top: 10px;")
        self.del_btn.clicked.connect(self.delete_rule)
        layout.addWidget(self.del_btn)
        
    def refresh_list(self):
        self.list_widget.clear()
        for word, pron in pronunciation_manager.dictionary.items():
            item = QListWidgetItem(f"{word}  ->  {pron}")
            item.setData(Qt.UserRole, word)
            self.list_widget.addItem(item)
            
    def add_rule(self):
        word = self.word_input.text().strip()
        pron = self.pron_input.text().strip()
        
        if not word or not pron:
            QMessageBox.warning(self, "Error", "Both Word and Pronunciation are required.")
            return
            
        pronunciation_manager.add_rule(word, pron)
        self.word_input.clear()
        self.pron_input.clear()
        self.refresh_list()
        
    def delete_rule(self):
        item = self.list_widget.currentItem()
        if not item:
            return
            
        word = item.data(Qt.UserRole)
        pronunciation_manager.remove_rule(word)
        self.refresh_list()
