from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QComboBox, QMessageBox, QAbstractItemView, QWidget)
from PySide6.QtCore import Qt, QTimer
import sounddevice as sd
import soundfile as sf
import numpy as np
from legends_labs.modules.voice_clone.pronunciation_db import pronunciation_db

class PronunciationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Pronunciation Learning System")
        self.resize(800, 600)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("AI Pronunciation Memory")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(header)
        
        desc = QLabel("The system continuously observes your recordings and extracts your natural pronunciations. Review and manage the extracted vocabulary here.")
        desc.setStyleSheet("color: #b9bbbe; margin-bottom: 20px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Controls
        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search words or IPA...")
        self.search_input.textChanged.connect(self.filter_table)
        controls.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton("Refresh Database")
        self.refresh_btn.clicked.connect(self.load_data)
        controls.addWidget(self.refresh_btn)
        layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Word", "Category", "Phonetic / IPA", "Context / Emotion", "Confidence", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2f3136; color: #dcddde; border: none; }
            QHeaderView::section { background-color: #202225; color: #ffffff; font-weight: bold; padding: 5px; border: 1px solid #2f3136; }
        """)
        layout.addWidget(self.table)
        
    def load_data(self):
        self.table.setRowCount(0)
        words = pronunciation_db.get_all_words()
        
        row_idx = 0
        for spelling in words:
            word_obj = pronunciation_db.get_word(spelling)
            if not word_obj: continue
            
            for variant in word_obj.variants:
                self.table.insertRow(row_idx)
                
                # Word
                word_item = QTableWidgetItem(spelling)
                if word_obj.default_variant_id == variant.id:
                    word_item.setText(f"★ {spelling}")
                    word_item.setForeground(Qt.yellow)
                self.table.setItem(row_idx, 0, word_item)
                
                # Category
                self.table.setItem(row_idx, 1, QTableWidgetItem(word_obj.category.title()))
                
                # Pronunciation
                pron_text = variant.phonetic
                if variant.ipa:
                    pron_text += f" [{variant.ipa}]"
                self.table.setItem(row_idx, 2, QTableWidgetItem(pron_text))
                
                # Context / Emotion
                if variant.occurrences:
                    occ = variant.occurrences[0]
                    context_str = f"Style: {occ.style_name} | Emotion: {occ.emotion.title()}"
                    conf_str = f"{occ.confidence*100:.1f}%"
                else:
                    context_str = "No occurrences"
                    conf_str = "N/A"
                    
                self.table.setItem(row_idx, 3, QTableWidgetItem(context_str))
                self.table.setItem(row_idx, 4, QTableWidgetItem(conf_str))
                
                # Actions (Play Snippet)
                if variant.occurrences:
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(0, 0, 0, 0)
                    
                    play_btn = QPushButton("▶ Pla")
                    play_btn.setFixedWidth(50)
                    occ = variant.occurrences[0]
                    # Closure capture fix
                    play_btn.clicked.connect(lambda checked=False, o=occ: self.play_snippet(o.audio_path, o.start_time, o.end_time))
                    
                    set_def_btn = QPushButton("Def")
                    set_def_btn.setFixedWidth(30)
                    set_def_btn.setToolTip("Set Default")
                    set_def_btn.clicked.connect(lambda checked=False, w=spelling, v=variant.id: self.set_default(w, v))
                    
                    del_btn = QPushButton("Del")
                    del_btn.setFixedWidth(30)
                    del_btn.setStyleSheet("QPushButton { color: #f04747; }")
                    del_btn.clicked.connect(lambda checked=False, w=spelling: self.delete_word_entry(w))
                    
                    action_layout.addWidget(play_btn)
                    action_layout.addWidget(set_def_btn)
                    action_layout.addWidget(del_btn)
                    self.table.setCellWidget(row_idx, 5, action_widget)
                
                row_idx += 1

    def filter_table(self, query):
        query = query.lower()
        for row in range(self.table.rowCount()):
            word = self.table.item(row, 0).text().lower()
            pron = self.table.item(row, 2).text().lower()
            if query in word or query in pron:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def play_snippet(self, audio_path: str, start_time: float, end_time: float):
        try:
            info = sf.info(audio_path)
            sr = info.samplerate
            
            # Add a small buffer of 0.2s before and after to provide context
            buffer_time = 0.2
            s_t = max(0, start_time - buffer_time)
            e_t = min(info.frames / sr, end_time + buffer_time)
            
            start_frame = int(s_t * sr)
            end_frame = int(e_t * sr)
            
            y, sr = sf.read(audio_path, start=start_frame, stop=end_frame)
            sd.play(y, sr)
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", f"Failed to play snippet: {e}")

    def set_default(self, spelling: str, variant_id: int):
        pronunciation_db.set_default_variant(spelling, variant_id)
        self.load_data()

    def delete_word_entry(self, spelling: str):
        reply = QMessageBox.question(self, "Delete Word", f"Are you sure you want to delete the pronunciation rules for '{spelling}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if pronunciation_db.delete_word(spelling):
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete word.")
