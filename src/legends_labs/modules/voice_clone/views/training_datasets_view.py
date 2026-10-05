import os
import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame, QGridLayout, 
                               QSpacerItem, QSizePolicy, QComboBox)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPainter, QColor, QFont, QLinearGradient
from legends_labs.ui.widgets.premium_slider import PremiumSlider
from legends_labs.modules.voice_clone.voice_memory import voice_memory

class TrainingDatasetsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("training_view")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Panel (Dataset Manager)
        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_panel.setStyleSheet("QWidget#left_panel { background-color: #11100F; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(30)
        
        # Header
        header_layout = QHBoxLayout()
        header_title = QLabel("Training & Datasets")
        header_title.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        self.voice_selector = QComboBox()
        self.voice_selector.setFixedHeight(40)
        self.voice_selector.setMinimumWidth(200)
        self.voice_selector.setStyleSheet("""
            QComboBox {
                background-color: #191816;
                color: #FFFFFF;
                border: 1px solid #2A2621;
                border-radius: 8px;
                padding: 0 16px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #191816;
                color: #FFFFFF;
                border: 1px solid #2A2621;
                selection-background-color: #5865F2;
            }
        """)
        self.voice_selector.currentTextChanged.connect(self.load_dataset)
        header_layout.addWidget(self.voice_selector)
        left_layout.addLayout(header_layout)
        
        # Stats Bar
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        left_layout.addLayout(self.stats_layout)
        
        # Grid Area for Clips
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        self.scroll_area.setWidget(self.grid_widget)
        left_layout.addWidget(self.scroll_area)
        
        # Right Panel (Training Config)
        right_panel = QWidget()
        right_panel.setFixedWidth(320)
        right_panel.setObjectName("right_panel")
        right_panel.setStyleSheet("QWidget#right_panel { background-color: #151413; border-left: 1px solid #1E1C1A; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 40, 24, 40)
        right_layout.setSpacing(24)
        
        config_title = QLabel("Fine-Tuning")
        config_title.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 20px; font-weight: 600; color: #FFFFFF;")
        right_layout.addWidget(config_title)
        
        # Model Selector
        model_lbl = QLabel("Base Model")
        model_lbl.setStyleSheet("color: #8C877D; font-size: 12px; font-weight: 600;")
        right_layout.addWidget(model_lbl)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Fish Speech 1.5", "XTTS v2", "GPT-SoVITS"])
        self.model_combo.setFixedHeight(40)
        self.model_combo.setStyleSheet(self.voice_selector.styleSheet())
        right_layout.addWidget(self.model_combo)
        
        # Training Mode
        mode_lbl = QLabel("Training Mode")
        mode_lbl.setStyleSheet("color: #8C877D; font-size: 12px; font-weight: 600; margin-top: 10px;")
        right_layout.addWidget(mode_lbl)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Fast LoRA (5 mins)", "Standard (30 mins)", "Studio Quality (2 hrs)"])
        self.mode_combo.setFixedHeight(40)
        self.mode_combo.setStyleSheet(self.voice_selector.styleSheet())
        right_layout.addWidget(self.mode_combo)
        
        right_layout.addStretch()
        
        # Train Button
        self.train_btn = QPushButton("Start Fine-Tuning")
        self.train_btn.setFixedHeight(56)
        self.train_btn.setCursor(Qt.PointingHandCursor)
        self.train_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #888888;
            }
        """)
        right_layout.addWidget(self.train_btn)
        
        # Assemble Main Layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 0)
        
        # Initial Load
        self.refresh_voices()

    def refresh_voices(self):
        self.voice_selector.blockSignals(True)
        self.voice_selector.clear()
        styles = voice_memory.get_all_style_names()
        if not styles:
            self.voice_selector.addItem("No Voices Found")
            self.train_btn.setEnabled(False)
        else:
            self.voice_selector.addItems(styles)
            self.train_btn.setEnabled(True)
        self.voice_selector.blockSignals(False)
        
        if styles:
            self.load_dataset(styles[0])
            
    def load_dataset(self, profile_name):
        if not profile_name or profile_name == "No Voices Found":
            return
            
        # Clear stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        clips = voice_memory.get_clips_with_emotions(profile_name)
        
        # Update Stats
        total_clips = len(clips)
        total_duration = sum([c.get("duration", 0) for c in clips])
        
        def make_stat(val, label):
            w = QWidget()
            l = QVBoxLayout(w)
            l.setContentsMargins(0,0,0,0)
            l.setSpacing(4)
            v = QLabel(str(val))
            v.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; font-family: 'Segoe UI', 'Inter', sans-serif;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #8C877D; font-size: 12px; font-weight: 600;")
            l.addWidget(v)
            l.addWidget(lbl)
            return w
            
        self.stats_layout.addWidget(make_stat(total_clips, "Audio Clips"))
        mins = int(total_duration // 60)
        secs = int(total_duration % 60)
        self.stats_layout.addWidget(make_stat(f"{mins}m {secs}s", "Total Dataset Duration"))
        self.stats_layout.addStretch()
        
        # Populate Grid
        row, col = 0, 0
        max_cols = 3
        
        for clip in clips:
            card = self._create_clip_card(clip)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        # Add Drop Zone Card
        drop_card = self._create_drop_zone_card()
        self.grid_layout.addWidget(drop_card, row, col)

    def _create_clip_card(self, clip_data):
        card = QFrame()
        card.setFixedHeight(140)
        card.setStyleSheet("""
            QFrame {
                background-color: #191816;
                border: 1px solid #2A2621;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 1px solid #5865F2;
                background-color: #1E1C1A;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Top row: Play button + Emotion + Duration
        top_row = QHBoxLayout()
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(32, 32)
        play_btn.setCursor(Qt.PointingHandCursor)
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2621;
                color: #FFFFFF;
                border: none;
                border-radius: 16px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #5865F2; }
        """)
        
        emotion = clip_data.get("emotion", "neutral").title()
        emotion_lbl = QLabel(emotion)
        emotion_lbl.setStyleSheet(f"color: {'#5865F2' if emotion != 'Neutral' else '#8C877D'}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        
        dur = clip_data.get("duration", 0)
        dur_lbl = QLabel(f"{dur:.1f}s")
        dur_lbl.setStyleSheet("color: #8C877D; font-size: 12px; border: none; background: transparent;")
        
        top_row.addWidget(play_btn)
        top_row.addWidget(emotion_lbl)
        top_row.addStretch()
        top_row.addWidget(dur_lbl)
        layout.addLayout(top_row)
        
        layout.addStretch()
        
        # Fake mini waveform
        wave = QWidget()
        wave.setFixedHeight(24)
        wave.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(wave)
        
        return card

    def _create_drop_zone_card(self):
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px dashed #2A2621;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 2px dashed #5865F2;
                background-color: rgba(88, 101, 242, 0.05);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("⇧")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("color: #8C877D; font-size: 24px; border: none;")
        
        text = QLabel("Import New Audio")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("color: #8C877D; font-size: 14px; font-weight: 600; border: none;")
        
        layout.addWidget(icon)
        layout.addWidget(text)
        
        return card
