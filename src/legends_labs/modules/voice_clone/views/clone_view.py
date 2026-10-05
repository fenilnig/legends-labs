from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QPlainTextEdit, QComboBox, QSlider, QGroupBox, QFileDialog, QScrollArea, QFrame, QLineEdit, QStackedWidget, QGridLayout)
from PySide6.QtGui import QIcon
from legends_labs.ui.widgets.progress_ring_widget import ProgressRingWidget
from PySide6.QtCore import Qt, QTimer
import os

class CloneView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        from legends_labs.ui.widgets.particle_overlay import ParticleOverlay
        self.particle_overlay = ParticleOverlay(self)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'particle_overlay'):
            self.particle_overlay.setGeometry(self.rect())
            
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ==========================================
        # LEFT PANEL: PROMPT EDITOR (70%)
        # ==========================================
        narration_panel = QVBoxLayout()
        narration_panel.setContentsMargins(0, 0, 0, 0)
        
        # Script Editor Container (Acts as the main hero box)
        editor_container = QWidget()
        editor_container.setObjectName("editorContainer")
        editor_container.setStyleSheet("#editorContainer { background-color: transparent; border: 1px solid #2A2621; border-radius: 8px; }")
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        
        # Editor Top Header (subtle)
        editor_header = QWidget()
        editor_header.setObjectName("editorHeader")
        editor_header.setStyleSheet("#editorHeader { background-color: rgba(0,0,0,0.2); border-bottom: 1px solid #2A2621; border-top: none; border-left: none; border-right: none; border-radius: 0px; }")
        eh_layout = QHBoxLayout(editor_header)
        eh_layout.setContentsMargins(20, 10, 20, 10)
        
        prompt_lbl = QLabel("Prompt")
        prompt_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #F2EFEB; border: none; background: transparent;")
        
        self.dict_btn = QPushButton("Pronunciation Dictionary")
        self.dict_btn.setCursor(Qt.PointingHandCursor)
        self.dict_btn.setStyleSheet("QPushButton { font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; color: #7A7265; background: transparent; border: none; font-weight: 500; } QPushButton:hover { color: #5865F2; }")
        self.dict_btn.clicked.connect(self.open_dictionary)
        
        eh_layout.addWidget(prompt_lbl)
        eh_layout.addStretch()
        eh_layout.addWidget(self.dict_btn)
        
        editor_layout.addWidget(editor_header)
        
        # Prompt Chips (Scrollable row)
        chips_wrapper = QWidget()
        chips_wrapper.setStyleSheet("background: transparent; border: none;")
        chips_layout = QHBoxLayout(chips_wrapper)
        chips_layout.setContentsMargins(20, 10, 20, 0)
        chips_layout.setSpacing(10)
        
        chip_data = [
            ("Pause", "[Pause: 1.0s]"), ("Short Pause", "[Pause: 0.3s]"), ("Breath", "[Breath]"),
            ("Happy", "[Emotion: Happy]"), ("Sad", "[Emotion: Sad]"), ("Serious", "[Emotion: Serious]"),
            ("Whisper", "[Style: Whisper]"), ("Slow", "[Pace: Slow]"), ("Fast", "[Pace: Fast]"),
            ("Emphasis", "[Emphasis]"), ("Pronunciation", "[Pronunciation:]"), ("Spell", "[Spell:]")
        ]
        
        # Scroll area for chips so it doesn't break layout if window shrinks
        chips_scroll = QScrollArea()
        chips_scroll.setWidgetResizable(True)
        chips_scroll.setFixedHeight(46)
        chips_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chips_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chips_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; border-bottom: 1px solid #2A2621; }")
        
        chips_content = QWidget()
        chips_content.setStyleSheet("background: transparent; border: none;")
        cc_layout = QHBoxLayout(chips_content)
        cc_layout.setContentsMargins(20, 5, 20, 5)
        cc_layout.setSpacing(8)
        
        for name, tag in chip_data:
            btn = QPushButton(name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #A89F91;
                    border: 1px solid #2A2621;
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-family: 'Segoe UI', 'Inter', sans-serif;
                    font-size: 11px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #161412;
                    color: #F2EFEB;
                    border-color: #5865F2;
                }
            """)
            btn.clicked.connect(lambda checked=False, t=tag: self._insert_tag(t))
            cc_layout.addWidget(btn)
        
        cc_layout.addStretch()
        chips_scroll.setWidget(chips_content)
        editor_layout.addWidget(chips_scroll)
        
        # Suggestions Bar
        self.suggestions_container = QWidget()
        self.suggestions_container.setStyleSheet("background-color: #12100E; border-bottom: 1px solid #2A2621;")
        self.sug_layout = QHBoxLayout(self.suggestions_container)
        self.sug_layout.setContentsMargins(20, 4, 20, 4)
        self.sug_layout.setSpacing(10)
        
        self.sug_label = QLabel("Suggestions:")
        self.sug_label.setStyleSheet("color: #F5C400; font-size: 11px; font-weight: bold; font-family: 'Segoe UI', sans-serif;")
        self.sug_layout.addWidget(self.sug_label)
        
        self.sug_scroll = QScrollArea()
        self.sug_scroll.setWidgetResizable(True)
        self.sug_scroll.setFixedHeight(28)
        self.sug_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sug_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sug_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.sug_content = QWidget()
        self.sug_content_layout = QHBoxLayout(self.sug_content)
        self.sug_content_layout.setContentsMargins(0, 0, 0, 0)
        self.sug_content_layout.setSpacing(10)
        self.sug_scroll.setWidget(self.sug_content)
        
        self.sug_layout.addWidget(self.sug_scroll, stretch=1)
        editor_layout.addWidget(self.suggestions_container)
        self.suggestions_container.hide() # Hidden initially

        # Text Area
        self.script_input = QPlainTextEdit()
        self.script_input.setPlaceholderText("Start writing your narration...\n\nVoice Tags can be inserted from the chips above.")
        self.script_input.setStyleSheet("""
            QPlainTextEdit { 
                border: none; 
                background-color: transparent; 
                padding: 30px; 
                font-family: 'Segoe UI', 'Inter', sans-serif; 
                font-size: 16px; 
                color: #F2EFEB; 
                line-height: 1.6; 
            } 
            QPlainTextEdit:focus { border: none; background-color: transparent; }
        """)
        self.script_input.textChanged.connect(self.update_editor_stats)
        editor_layout.addWidget(self.script_input, stretch=1)
        
        # Warnings Bar
        self.warning_bar = QWidget()
        self.warning_bar.setStyleSheet("background-color: rgba(240, 71, 71, 0.08); border-top: 1px solid #f04747; border-bottom: 1px solid #f04747;")
        wb_layout = QHBoxLayout(self.warning_bar)
        wb_layout.setContentsMargins(20, 6, 20, 6)
        self.warning_lbl = QLabel("")
        self.warning_lbl.setStyleSheet("color: #f04747; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
        wb_layout.addWidget(self.warning_lbl)
        editor_layout.addWidget(self.warning_bar)
        self.warning_bar.hide()
        
        # Container for the bottom block (allows swapping)
        self.bottom_bar_container = QStackedWidget()
        self.bottom_bar_container.setObjectName("bottomBarContainer")
        self.bottom_bar_container.setStyleSheet("#bottomBarContainer { background-color: #161412; border-top: 1px solid #2A2621; border-bottom: none; border-left: none; border-right: none; border-radius: 0px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }")
        
        # 1. Default Stats Toolbar
        self.stats_toolbar = QWidget()
        tb_layout = QHBoxLayout(self.stats_toolbar)
        tb_layout.setContentsMargins(20, 12, 20, 12)
        
        # Detailed stats labels
        self.stats_lbl = QLabel("0 Words")
        self.stats_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        self.read_time_lbl = QLabel("0s")
        self.read_time_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        self.est_val_lbl = QLabel("Estimated: 0.0s")
        self.est_val_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        self.voice_name_lbl = QLabel("Voice: Fenil Studio")
        self.voice_name_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        self.gpu_ready_lbl = QLabel("GPU Ready")
        self.gpu_ready_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: #43b581; border: none; background: transparent;")
        
        def add_div(layout):
            div = QLabel("│")
            div.setStyleSheet("color: #2A2621; margin: 0 8px; border: none; background: transparent;")
            layout.addWidget(div)
            
        tb_layout.addWidget(self.stats_lbl)
        add_div(tb_layout)
        tb_layout.addWidget(self.read_time_lbl)
        add_div(tb_layout)
        tb_layout.addWidget(self.est_val_lbl)
        add_div(tb_layout)
        tb_layout.addWidget(self.voice_name_lbl)
        add_div(tb_layout)
        tb_layout.addWidget(self.gpu_ready_lbl)
        tb_layout.addStretch()
        
        self.bottom_bar_container.addWidget(self.stats_toolbar)
        
        # 3. Timeline Progress Bar (Permanent widget showing generation progress stages)
        self.timeline_card = QWidget()
        tlt_layout = QHBoxLayout(self.timeline_card)
        tlt_layout.setContentsMargins(15, 8, 15, 8)
        tlt_layout.setSpacing(8)
        
        self.timeline_steps = []
        steps_labels = [
            "Prompt Parsed", "Analysis Complete", "Reference Selected", 
            "Tags Prepared", "Engine Ready", "Generating", "Finalizing"
        ]
        
        for name in steps_labels:
            lbl = QLabel(f"○ {name}")
            lbl.setStyleSheet("color: #7A7265; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
            self.timeline_steps.append(lbl)
            tlt_layout.addWidget(lbl)
            if name != steps_labels[-1]:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: #2A2621; font-family: 'Segoe UI', sans-serif; font-size: 11px;")
                tlt_layout.addWidget(arrow)
                
        tlt_layout.addStretch()
        
        # 2. Playback Toolbar (For Post-Generation)
        self.playback_toolbar = QWidget()
        pb_main_layout = QVBoxLayout(self.playback_toolbar)
        pb_main_layout.setContentsMargins(20, 8, 20, 8)
        pb_main_layout.setSpacing(10)
        
        from legends_labs.ui.widgets.waveform_widget import WaveformWidget
        self.playback_waveform = WaveformWidget()
        self.playback_waveform.setFixedHeight(60)
        self.playback_waveform.seek_requested.connect(self._on_waveform_seek)
        pb_main_layout.addWidget(self.playback_waveform)
        
        pb_layout = QHBoxLayout()
        pb_layout.setContentsMargins(0, 0, 0, 0)
        
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(28, 28)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setStyleSheet("QPushButton { background-color: #5865F2; color: #ffffff; border-radius: 14px; border: none; } QPushButton:hover { background-color: #4752C4; }")
        
        import PySide6.QtWidgets as QtWidgets
        self.play_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        
        self.current_time_lbl = QLabel("0:00")
        self.current_time_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        from legends_labs.ui.widgets.premium_slider import PremiumSlider
        self.seekbar = PremiumSlider(Qt.Horizontal)
        self.total_time_lbl = QLabel("0:00")
        self.total_time_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet("QPushButton { font-family: 'Segoe UI', 'Inter', sans-serif; background-color: transparent; color: #F2EFEB; border: 1px solid #2A2621; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 600; } QPushButton:hover { border-color: #5865F2; }")
        self.download_btn.clicked.connect(self.export_voiceover)
        
        pb_layout.addWidget(self.play_btn)
        pb_layout.addWidget(self.current_time_lbl)
        pb_layout.addWidget(self.seekbar)
        pb_layout.addWidget(self.total_time_lbl)
        pb_layout.addWidget(self.download_btn)
        
        pb_main_layout.addLayout(pb_layout)
        
        self.bottom_bar_container.addWidget(self.playback_toolbar)
        
        editor_layout.addWidget(self.bottom_bar_container)
        narration_panel.addWidget(editor_container, stretch=1)
        
        # Signal Line
        from legends_labs.ui.widgets.signal_line import SignalLineWidget
        self.signal_line = SignalLineWidget()
        narration_panel.addWidget(self.signal_line)
        
        # Generation Progress stages timeline (Permanent Widget)
        narration_panel.addWidget(self.timeline_card)
        
        # AI Prompt Analysis Panel (Collapsible Card)
        self.analysis_panel = QFrame()
        self.analysis_panel.setObjectName("analysisPanel")
        self.analysis_panel.setStyleSheet("#analysisPanel { background-color: #161412; border: 1px solid #2A2621; border-radius: 8px; }")
        ap_layout = QVBoxLayout(self.analysis_panel)
        ap_layout.setContentsMargins(15, 12, 15, 12)
        ap_layout.setSpacing(10)
        
        ap_header = QHBoxLayout()
        ap_title = QLabel("AI Prompt Analysis")
        ap_title.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #F5C400; border: none; background: transparent;")
        
        self.ap_confidence = QLabel("Confidence: 95%")
        self.ap_confidence.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 11px; font-weight: 600; color: #43b581; border: none; background: transparent;")
        ap_header.addWidget(ap_title)
        ap_header.addStretch()
        ap_header.addWidget(self.ap_confidence)
        ap_layout.addLayout(ap_header)
        
        ap_grid = QGridLayout()
        ap_grid.setContentsMargins(0, 0, 0, 0)
        ap_grid.setSpacing(12)
        
        def add_ap_field(label, val_attr, row, col):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #7A7265; font-size: 11px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
            val = QLabel("--")
            val.setStyleSheet("color: #F2EFEB; font-size: 13px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
            setattr(self, val_attr, val)
            ap_grid.addWidget(lbl, row, col)
            ap_grid.addWidget(val, row + 1, col)
            
        add_ap_field("Detected Style", "ap_style", 0, 0)
        add_ap_field("Detected Emotion", "ap_emotion", 0, 1)
        add_ap_field("Energy", "ap_energy", 0, 2)
        add_ap_field("Pace", "ap_pace", 0, 3)
        add_ap_field("Est. Duration", "ap_duration", 2, 0)
        add_ap_field("Est. Gen Time", "ap_gentime", 2, 1)
        
        lbl_profile = QLabel("Current Voice Profile")
        lbl_profile.setStyleSheet("color: #7A7265; font-size: 11px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
        self.ap_profile = QLabel("--")
        self.ap_profile.setStyleSheet("color: #F2EFEB; font-size: 13px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
        ap_grid.addWidget(lbl_profile, 2, 2)
        ap_grid.addWidget(self.ap_profile, 3, 2)
        
        lbl_clip = QLabel("Selected Reference Clip")
        lbl_clip.setStyleSheet("color: #7A7265; font-size: 11px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
        self.ap_clip = QLabel("--")
        self.ap_clip.setStyleSheet("color: #5865F2; font-size: 13px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
        ap_grid.addWidget(lbl_clip, 2, 3)
        ap_grid.addWidget(self.ap_clip, 3, 3)
        
        ap_layout.addLayout(ap_grid)
        narration_panel.addWidget(self.analysis_panel)
        
        # Session Status Card
        self.session_card = QWidget()
        self.session_card.setObjectName("sessionCard")
        self.session_card.setStyleSheet("#sessionCard { background-color: #161412; border: 1px solid #2A2621; border-radius: 8px; }")
        sc_layout = QHBoxLayout(self.session_card)
        sc_layout.setContentsMargins(15, 10, 15, 10)
        
        sc_lbl = QLabel("Fish Speech: Ready")
        sc_lbl.setStyleSheet("color: #43b581; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 600;")
        self.live_engine_lbl = sc_lbl
        sc_layout.addWidget(sc_lbl)
        
        def add_sc_div():
            div = QLabel("│")
            div.setStyleSheet("color: #2A2621; margin: 0 8px;")
            sc_layout.addWidget(div)
            
        add_sc_div()
        
        self.live_cuda_lbl = QLabel("CUDA: Active")
        self.live_cuda_lbl.setStyleSheet("color: #A89F91; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500;")
        sc_layout.addWidget(self.live_cuda_lbl)
        add_sc_div()
        
        self.live_vram_lbl = QLabel("VRAM: 0.0/6.0 GB")
        self.live_vram_lbl.setStyleSheet("color: #A89F91; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500;")
        sc_layout.addWidget(self.live_vram_lbl)
        add_sc_div()
        
        self.live_stage_lbl = QLabel("Stage: Idle")
        self.live_stage_lbl.setStyleSheet("color: #F5C400; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 600;")
        sc_layout.addWidget(self.live_stage_lbl)
        add_sc_div()
        
        self.live_elapsed_lbl = QLabel("Elapsed: 0.0s")
        self.live_elapsed_lbl.setStyleSheet("color: #A89F91; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; font-weight: 500;")
        sc_layout.addWidget(self.live_elapsed_lbl)
        
        sc_layout.addStretch()
        narration_panel.addWidget(self.session_card)

        # Generate Action Area
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 20, 0, 0)
        
        from legends_labs.ui.widgets.generation_button import GenerationButton
        self.gen_btn = GenerationButton("Generate Voiceover")
        self.gen_btn.clicked.connect(self.start_generation)
        
        action_layout.addStretch()
        action_layout.addWidget(self.gen_btn, stretch=2)
        action_layout.addStretch()
        
        narration_panel.addLayout(action_layout)
        
        # Hide old progress widgets but keep them instantiated to prevent crashes
        self.progress_ring = ProgressRingWidget()
        self.progress_ring.hide()
        self.progress = QLabel("")
        self.progress.hide()
        
        from legends_labs.ui.widgets.audio_player import AudioPlayerWidget
        self.audio_player = AudioPlayerWidget("Generated Voiceover")
        self.audio_player.hide()
        narration_panel.addWidget(self.audio_player)
        
        self.export_btn = QPushButton("Export Voiceover")
        self.export_btn.clicked.connect(self.export_voiceover)
        self.export_btn.hide()
        narration_panel.addWidget(self.export_btn)
        
        main_layout.addLayout(narration_panel, stretch=7)
        
        # ==========================================
        # RIGHT PANEL: SETTINGS & MODEL HEALTH
        # ==========================================
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #2A2621;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        right_panel_widget = QWidget()
        right_panel_widget.setStyleSheet("background: transparent;")
        right_panel = QVBoxLayout(right_panel_widget)
        right_panel.setContentsMargins(0, 0, 0, 0)
        
        # --- Voice Section ---
        voice_group = QWidget()
        v_layout = QVBoxLayout(voice_group)
        v_layout.setContentsMargins(10, 0, 10, 20)
        v_layout.setSpacing(15)
        
        # Current Voice Combo
        cv_layout = QVBoxLayout()
        cv_layout.setSpacing(5)
        cv_lbl = QLabel("Current Voice")
        cv_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #A89F91;")
        
        self.profile_combo = QComboBox()
        # Load profiles dynamically from the database
        from legends_labs.modules.voice_clone.voice_memory import voice_memory
        _profile_names = voice_memory.get_all_style_names()
        if _profile_names:
            self.profile_combo.addItems(_profile_names)
        else:
            self.profile_combo.addItems(["Fenil"])
        self.profile_combo.addItem("+ Create New Voice Style")
        self.profile_combo.setStyleSheet("""
            QComboBox { background-color: #161412; color: #F2EFEB; border: 1px solid #2A2621; border-radius: 6px; padding: 8px 12px; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; }
            QComboBox:hover { border-color: #5865F2; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: none; } /* Could add custom arrow here */
        """)
        self.profile_combo.currentIndexChanged.connect(self.update_metrics_display)
        
        cv_layout.addWidget(cv_lbl)
        cv_layout.addWidget(self.profile_combo)
        v_layout.addLayout(cv_layout)
        
        # Dense Metric Grid
        self.health_grid = QWidget()
        hg_layout = __import__('PySide6.QtWidgets').QtWidgets.QGridLayout(self.health_grid)
        hg_layout.setContentsMargins(0, 0, 0, 0)
        hg_layout.setSpacing(10)
        
        def make_metric(val, title, r, c):
            card = QWidget()
            card.setStyleSheet("background-color: #161412; border: 1px solid #2A2621; border-radius: 6px;")
            l = QVBoxLayout(card)
            l.setContentsMargins(10, 10, 10, 10)
            l.setSpacing(2)
            val_l = QLabel(val)
            val_l.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #F2EFEB; border: none; background: transparent;")
            tit_l = QLabel(title)
            tit_l.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 11px; font-weight: 500; color: #7A7265; border: none; background: transparent;")
            l.addWidget(val_l)
            l.addWidget(tit_l)
            hg_layout.addWidget(card, r, c)
            return val_l
            
        self.sim_val = make_metric("Good", "Quality", 0, 0)
        self.nat_val = make_metric("0 Mins", "Duration", 0, 1)
        self.noise_val = make_metric("-45 dB", "Noise Level", 0, 2)
        self.pitch_val = make_metric("120 Hz", "Pitch", 1, 0)
        self.tempo_val = make_metric("3.0 syl/s", "Speaking Rate", 1, 1)
        self.data_val = make_metric("0 Clips", "Dataset", 1, 2)
        
        v_layout.addWidget(self.health_grid)
        
        # Reference Preview & Override Section
        self.ref_preview_group = QWidget()
        self.ref_preview_group.setStyleSheet("background-color: #161412; border: 1px solid #2A2621; border-radius: 6px; padding: 10px;")
        rpg_layout = QVBoxLayout(self.ref_preview_group)
        rpg_layout.setContentsMargins(10, 10, 10, 10)
        rpg_layout.setSpacing(8)
        
        rpg_title = QLabel("Selected Reference Clip")
        rpg_title.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; color: #A89F91;")
        rpg_layout.addWidget(rpg_title)
        
        self.ref_clip_combo = QComboBox()
        self.ref_clip_combo.setStyleSheet("""
            QComboBox { background-color: #0F0E0C; color: #F2EFEB; border: 1px solid #2A2621; border-radius: 4px; padding: 6px; font-size: 12px; }
            QComboBox:hover { border-color: #5865F2; }
        """)
        self.ref_clip_combo.currentIndexChanged.connect(self._on_ref_clip_override_changed)
        rpg_layout.addWidget(self.ref_clip_combo)
        
        # Grid showing metadata for selected clip
        self.ref_meta_grid = QWidget()
        rmg_layout = QGridLayout(self.ref_meta_grid)
        rmg_layout.setContentsMargins(0, 0, 0, 0)
        rmg_layout.setSpacing(6)
        
        def add_rmg_lbl(label, val_attr, row, col):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #7A7265; font-size: 11px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
            val = QLabel("--")
            val.setStyleSheet("color: #F2EFEB; font-size: 11px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
            setattr(self, val_attr, val)
            rmg_layout.addWidget(lbl, row, col)
            rmg_layout.addWidget(val, row, col + 1)
            
        add_rmg_lbl("Duration:", "ref_dur_lbl", 0, 0)
        add_rmg_lbl("Quality:", "ref_qual_lbl", 0, 2)
        add_rmg_lbl("Noise:", "ref_noise_lbl", 1, 0)
        add_rmg_lbl("Style:", "ref_style_lbl", 1, 2)
        
        rpg_layout.addWidget(self.ref_meta_grid)
        v_layout.addWidget(self.ref_preview_group)
        
        # Action Buttons
        rec_actions = QHBoxLayout()
        rec_actions.setSpacing(10)
        
        from legends_labs.ui.widgets.premium_button import PremiumButton
        self.add_rec_btn = PremiumButton("Upload Recording")
        self.live_rec_btn = PremiumButton("Live Microphone")
        
        for btn in [self.add_rec_btn, self.live_rec_btn]:
            rec_actions.addWidget(btn)
            
        self.add_rec_btn.clicked.connect(self.start_batch_import)
        self.live_rec_btn.clicked.connect(self.start_live_training)
        
        v_layout.addLayout(rec_actions)
        
        # Evolve Progress and Cancel
        prog_layout = QHBoxLayout()
        self.evolve_ring = ProgressRingWidget()
        self.evolve_ring.hide()
        self.evolve_progress = QLabel("")
        self.evolve_progress.setObjectName("success_text")
        self.evolve_progress.hide()
        
        self.cancel_task_btn = QPushButton("✖")
        self.cancel_task_btn.setFixedSize(20, 20)
        self.cancel_task_btn.setStyleSheet("QPushButton { background: transparent; color: #f04747; font-weight: bold; border: none; } QPushButton:hover { background: #f04747; color: white; border-radius: 10px; }")
        self.cancel_task_btn.hide()
        self.cancel_task_btn.clicked.connect(self.cancel_current_task)
        
        prog_layout.addWidget(self.evolve_ring)
        prog_layout.addWidget(self.evolve_progress)
        prog_layout.addWidget(self.cancel_task_btn)
        prog_layout.addStretch()
        
        v_layout.addLayout(prog_layout)
        right_panel.addWidget(voice_group)
        
        # --- Generation Settings ---
        settings_group = QGroupBox()
        sg_layout = QVBoxLayout(settings_group)
        sg_layout.setSpacing(20)
        sg_layout.setContentsMargins(10, 20, 10, 10)
        
        # Style Selector (No header needed, clean)
        style_label = QLabel("Style")
        style_label.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        sg_layout.addWidget(style_label)
        
        self.style_grid = QWidget()
        self.style_grid_layout = __import__('PySide6.QtWidgets').QtWidgets.QGridLayout(self.style_grid)
        self.style_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.style_grid_layout.setSpacing(8)
        
        styles = ["Natural", "Podcast", "Documentary", "Cinematic", "Storytelling", "Tutorial", "Advertisement", "Whisper"]
        self.style_btns = []
        for i, s in enumerate(styles):
            btn = QPushButton(s)
            btn.setCheckable(True)
            btn.setMinimumHeight(32)
            btn.setStyleSheet("""
                QPushButton { background-color: transparent; color: #A89F91; border: 1px solid #2A2621; border-radius: 6px; padding: 8px; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
                QPushButton:checked { background-color: rgba(88, 101, 242, 0.1); color: #5865F2; border: 1px solid #5865F2; font-weight: 600; }
                QPushButton:hover:!checked { background-color: #161412; color: #F2EFEB; }
            """)
            btn.clicked.connect(lambda checked, b=btn: self._on_style_selected(b))
            self.style_btns.append(btn)
            self.style_grid_layout.addWidget(btn, i // 4, i % 4)
            
        if self.style_btns:
            self.style_btns[0].setChecked(True)
        sg_layout.addWidget(self.style_grid)
        
        # Expressiveness
        exp_header_layout = QHBoxLayout()
        exp_lbl = QLabel("Expressiveness")
        exp_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        exp_header_layout.addWidget(exp_lbl)
        
        self.exp_val_lbl = QLabel("72%")
        self.exp_val_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #5865F2; border: none; background: transparent;")
        exp_header_layout.addWidget(self.exp_val_lbl, alignment=Qt.AlignRight)
        sg_layout.addLayout(exp_header_layout)
        
        from legends_labs.ui.widgets.premium_slider import PremiumSlider
        self.emotion_slider = PremiumSlider(Qt.Horizontal)
        self.emotion_slider.setRange(0, 100)
        self.emotion_slider.setValue(72)
        self.emotion_slider.valueChanged.connect(lambda v: self.exp_val_lbl.setText(f"{v}%"))
        sg_layout.addWidget(self.emotion_slider)
        
        exp_labels_layout = QHBoxLayout()
        lbl_nat = QLabel("Natural"); lbl_nat.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #7A7265; font-size: 11px;")
        lbl_cin = QLabel("Cinematic"); lbl_cin.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #7A7265; font-size: 11px;")
        exp_labels_layout.addWidget(lbl_nat)
        exp_labels_layout.addWidget(lbl_cin, alignment=Qt.AlignRight)
        sg_layout.addLayout(exp_labels_layout)
        
        # Narration Pace
        pace_header_layout = QHBoxLayout()
        pace_lbl = QLabel("Pace")
        pace_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #A89F91; border: none; background: transparent;")
        pace_header_layout.addWidget(pace_lbl)
        
        self.pace_val_lbl = QLabel("Normal")
        self.pace_val_lbl.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #5865F2; border: none; background: transparent;")
        pace_header_layout.addWidget(self.pace_val_lbl, alignment=Qt.AlignRight)
        sg_layout.addLayout(pace_header_layout)
        
        self.speed_slider = PremiumSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 150)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self._on_pace_changed)
        sg_layout.addWidget(self.speed_slider)
        
        pace_labels_layout = QHBoxLayout()
        lbl_slow = QLabel("Slow"); lbl_slow.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #7A7265; font-size: 11px;")
        lbl_fast = QLabel("Fast"); lbl_fast.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; color: #7A7265; font-size: 11px;")
        pace_labels_layout.addWidget(lbl_slow)
        pace_labels_layout.addWidget(lbl_fast, alignment=Qt.AlignRight)
        sg_layout.addLayout(pace_labels_layout)
        
        # Advanced Settings Accordion
        self.adv_btn = QPushButton("Advanced Settings ▼")
        self.adv_btn.setCursor(Qt.PointingHandCursor)
        self.adv_btn.setStyleSheet("QPushButton { font-family: 'Segoe UI', 'Inter', sans-serif; background: transparent; color: #7A7265; text-align: left; font-weight: 500; border: none; padding: 15px 0px 5px 0px; } QPushButton:hover { color: #A89F91; }")
        
        self.adv_content = QWidget()
        self.adv_content.hide()
        adv_layout = __import__('PySide6.QtWidgets').QtWidgets.QFormLayout(self.adv_content)
        adv_layout.setContentsMargins(0, 10, 0, 10)
        
        self.temp_input = QLineEdit("0.7")
        self.top_p_input = QLineEdit("0.7")
        self.top_k_input = QLineEdit("50")
        self.chunk_len_input = QLineEdit("200")
        self.rep_pen_input = QLineEdit("1.5")
        self.seed_input = QLineEdit("Auto")
        self.max_tokens_input = QLineEdit("1024")
        
        self.compile_cb = __import__('PySide6.QtWidgets').QtWidgets.QCheckBox("Compile Model (Faster)")
        self.compile_cb.setChecked(False)
        self.fp16_cb = __import__('PySide6.QtWidgets').QtWidgets.QCheckBox("FP16 Inference")
        self.fp16_cb.setChecked(True)
        
        cb_style = "QCheckBox { color: #F2EFEB; font-size: 12px; } QCheckBox::indicator { width: 14px; height: 14px; border-radius: 4px; border: 1px solid #5865F2; background: transparent; } QCheckBox::indicator:checked { background: #5865F2; }"
        self.compile_cb.setStyleSheet(cb_style)
        self.fp16_cb.setStyleSheet(cb_style)
        
        inputs = [self.temp_input, self.top_p_input, self.top_k_input, self.chunk_len_input, self.rep_pen_input, self.seed_input, self.max_tokens_input]
        for inp in inputs:
            inp.setStyleSheet("background: #0F0E0C; border: 1px solid #2A2621; color: #F2EFEB; padding: 6px; border-radius: 6px; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px;")
            
        def mk_lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color: #A89F91; font-size: 12px; font-family: 'Segoe UI', 'Inter', sans-serif;")
            return l
            
        adv_layout.addRow(mk_lbl("Temperature:"), self.temp_input)
        adv_layout.addRow(mk_lbl("Top P:"), self.top_p_input)
        adv_layout.addRow(mk_lbl("Top K:"), self.top_k_input)
        adv_layout.addRow(mk_lbl("Chunk Length:"), self.chunk_len_input)
        adv_layout.addRow(mk_lbl("Repetition Penalty:"), self.rep_pen_input)
        adv_layout.addRow(mk_lbl("Seed:"), self.seed_input)
        adv_layout.addRow(mk_lbl("Max Tokens:"), self.max_tokens_input)
        adv_layout.addRow(self.compile_cb)
        adv_layout.addRow(self.fp16_cb)
        
        self.adv_btn.clicked.connect(self._toggle_advanced)
        sg_layout.addWidget(self.adv_btn)
        sg_layout.addWidget(self.adv_content)
        
        sg_layout.addStretch()
        
        # Professional Voice Training CTA (Premium Card)
        train_card = QWidget()
        train_card.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F1B12, stop:1 #161412); border: 1px solid #3A3221; border-radius: 8px;")
        train_layout = QVBoxLayout(train_card)
        train_layout.setContentsMargins(15, 15, 15, 15)
        
        train_lbl = QLabel("Studio Voice Model")
        train_lbl.setStyleSheet("color: #F5C400; font-weight: bold; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; border: none; background: transparent;")
        
        train_desc = QLabel("Train a hyper-realistic dedicated model. Takes ~30 mins on RTX 4050.")
        train_desc.setWordWrap(True)
        train_desc.setStyleSheet("color: #A89F91; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 12px; border: none; background: transparent;")
        
        from legends_labs.ui.widgets.premium_button import PremiumButton
        self.lora_btn = PremiumButton("Create Studio Voice →")
        self.lora_btn.setStyleSheet("""
            QPushButton { background-color: #F5C400; color: #161412; font-weight: 700; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; border: none; }
        """)
        self.lora_btn.clicked.connect(self.start_lora_training)
        
        train_layout.addWidget(train_lbl)
        train_layout.addWidget(train_desc)
        train_layout.addWidget(self.lora_btn)
        sg_layout.addWidget(train_card)
        
        settings_group.setLayout(sg_layout)
        right_panel.addWidget(settings_group)
        
        right_scroll.setWidget(right_panel_widget)
        main_layout.addWidget(right_scroll, stretch=3)
        
        # Connect global signals
        from legends_labs.core.signals import signal_bus
        signal_bus.vram_updated.connect(self._on_vram_updated)
        
        # Initial stats setup
        self.update_metrics_display()

    def _on_vram_updated(self, used_mb, total_mb):
        used_gb = used_mb / 1024.0
        total_gb = total_mb / 1024.0
        self.live_vram_lbl.setText(f"VRAM: {used_gb:.1f}/{total_gb:.1f} GB")

    def _insert_tag(self, tag_text: str):
        cursor = self.script_input.textCursor()
        cursor.insertText(tag_text + " ")
        self.script_input.setFocus()

    def update_editor_stats(self):
        text = self.script_input.toPlainText()
        words = len(text.split())
        
        # Words
        self.stats_lbl.setText(f"{words} Words")
        
        # Average reading speed is ~150 words per minute
        seconds = int((words / 150) * 60)
        mins = seconds // 60
        secs = seconds % 60
        self.read_time_lbl.setText(f"{mins}m {secs:02d}s")
        
        # Generation time estimate: roughly 4.0 secs per 100 words on RTX
        gen_time = max(0.0, (words / 100.0) * 4.0)
        self.est_val_lbl.setText(f"Estimated: {gen_time:.1f}s")
        
        # AI Prompt Analysis Live Updates
        if not text.strip():
            self.ap_style.setText("--")
            self.ap_emotion.setText("--")
            self.ap_energy.setText("--")
            self.ap_pace.setText("--")
            self.ap_duration.setText("0.0s")
            self.ap_gentime.setText("0.0s")
            self.ap_profile.setText(getattr(self, "current_profile_name", "Fenil"))
            self.ap_clip.setText("Auto Selection")
            self.ap_confidence.setText("Confidence: --")
            self.suggestions_container.hide()
            return
            
        text_lower = text.lower()
        
        # Style
        style = "Neutral"
        if any(w in text_lower for w in ["once upon a time", "lived", "forest", "journey", "whispered", "dark"]):
            style = "Storytelling"
        elif any(w in text_lower for w in ["code", "python", "data", "system", "science", "technical", "engine"]):
            style = "Technical"
        elif any(w in text_lower for w in ["epic", "cinematic", "universe", "battle", "legend"]):
            style = "Cinematic"
            
        # Emotion
        emotion = "neutral"
        if "!" in text or any(w in text_lower for w in ["incredible", "awesome", "great", "excited", "wow"]):
            emotion = "excited"
        elif "?" in text or any(w in text_lower for w in ["maybe", "perhaps", "guess", "hey"]):
            emotion = "casual"
        elif any(w in text_lower for w in ["must", "command", "never", "authority", "strict"]):
            emotion = "authoritative"
            
        # Energy / Pace
        energy = "Medium"
        pace = "Normal"
        if emotion == "excited":
            energy = "High"
            pace = "Fast"
        elif style == "Storytelling":
            energy = "Low"
            pace = "Slow"
            
        self.ap_style.setText(style)
        self.ap_emotion.setText(emotion.capitalize())
        self.ap_energy.setText(energy)
        self.ap_pace.setText(pace)
        self.ap_duration.setText(f"{mins}m {secs:02d}s" if mins > 0 else f"{seconds}s")
        self.ap_gentime.setText(f"{gen_time:.1f}s")
        self.ap_profile.setText(getattr(self, "current_profile_name", "Fenil"))
        
        active_clip_name = "Auto Select"
        active_clip_path = None
        
        if getattr(self, "selected_ref_override_path", None):
            active_clip_path = self.selected_ref_override_path
            active_clip_name = os.path.basename(self.selected_ref_override_path) + " (Overridden)"
            self.ap_confidence.setText("Confidence: 100% (Manual)")
        else:
            clips = getattr(self, "current_clips", [])
            match_clip = None
            for c in clips:
                if c["emotion"] == emotion:
                    match_clip = c
                    break
            if not match_clip:
                for c in clips:
                    if c["emotion"] == "neutral":
                        match_clip = c
                        break
            if not match_clip and clips:
                match_clip = clips[0]
                
            if match_clip:
                active_clip_path = match_clip["path"]
                active_clip_name = os.path.basename(match_clip["path"]) + f" ({match_clip['emotion'].capitalize()})"
                self.ap_confidence.setText("Confidence: 92% (Smart)")
            else:
                active_clip_name = "No Clip Available"
                self.ap_confidence.setText("Confidence: 0%")
                
        self.ap_clip.setText(active_clip_name)
        
        # Voice Tag Suggestions
        suggestions = []
        if "?" in text and "[Pause:" not in text:
            suggestions.append(("Add thinking pause", "[Pause: 0.6s]"))
        if "!" in text and "[Pause:" not in text:
            suggestions.append(("Add breath pause", "[Pause: 0.8s]"))
        if "whisper" in text_lower and "[Style: Whisper]" not in text:
            suggestions.append(("Whisper recommended", "[Style: Whisper]"))
        if "fast" in text_lower and "[Pace: Fast]" not in text:
            suggestions.append(("Fast pacing recommended", "[Pace: Fast]"))
        if "never" in text_lower and "[Emphasis]" not in text:
            suggestions.append(("Strong emphasis detected", "[Emphasis]"))
            
        # Re-populate suggestions layout
        for i in reversed(range(self.sug_content_layout.count())): 
            item = self.sug_content_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            
        if suggestions:
            for title, tag in suggestions:
                pill = QWidget()
                pill.setStyleSheet("background-color: #1A1816; border: 1px solid #3A3221; border-radius: 10px; padding: 2px 8px;")
                pl = QHBoxLayout(pill)
                pl.setContentsMargins(5, 2, 5, 2)
                pl.setSpacing(6)
                
                lbl = QLabel(title)
                lbl.setStyleSheet("color: #A89F91; font-size: 11px; font-family: 'Segoe UI', sans-serif; border: none; background: transparent;")
                
                btn = QPushButton("Apply")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("QPushButton { color: #5865F2; font-size: 11px; font-weight: bold; border: none; background: transparent; } QPushButton:hover { color: #F5C400; }")
                btn.clicked.connect(lambda checked=False, t=tag: self._insert_tag(t))
                
                pl.addWidget(lbl)
                pl.addWidget(btn)
                self.sug_content_layout.addWidget(pill)
            self.sug_content_layout.addStretch()
            self.suggestions_container.show()
        else:
            self.suggestions_container.hide()

    def open_dictionary(self):
        from legends_labs.modules.voice_clone.views.pronunciation_view import PronunciationDialog
        dialog = PronunciationDialog(self)
        dialog.exec()
        
    def _update_ref_preview_details(self):
        active_path = None
        if getattr(self, "selected_ref_override_path", None):
            active_path = self.selected_ref_override_path
        else:
            clips = getattr(self, "current_clips", [])
            if clips:
                def clip_score(c):
                    dur = c.get("duration") or 0.0
                    if dur <= 0.0:
                        return -10000.0
                    noise = c.get("noise_level") or -60.0
                    return (dur * 1.0) - (noise * 2.0)
                clips_sorted = sorted(clips, key=clip_score, reverse=True)
                active_path = clips_sorted[0]["path"]
                
        clip_obj = None
        for c in getattr(self, "current_clips", []):
            if c["path"] == active_path:
                clip_obj = c
                break
                
        if clip_obj:
            dur = clip_obj.get("duration") or 0.0
            noise = clip_obj.get("noise_level") or -60.0
            emotion = clip_obj.get("emotion") or "neutral"
            
            self.ref_dur_lbl.setText(f"{dur:.1f}s")
            self.ref_noise_lbl.setText(f"{noise:.1f} dB")
            
            if noise < -48.0:
                self.ref_qual_lbl.setText("Clean")
                self.ref_qual_lbl.setStyleSheet("color: #43b581; font-weight: 600;")
            elif noise < -38.0:
                self.ref_qual_lbl.setText("Good")
                self.ref_qual_lbl.setStyleSheet("color: #faa61a; font-weight: 600;")
            else:
                self.ref_qual_lbl.setText("Fair")
                self.ref_qual_lbl.setStyleSheet("color: #f04747; font-weight: 600;")
                
            self.ref_style_lbl.setText(emotion.capitalize())
            
            warnings = []
            if noise > -30.0:
                warnings.append("High background noise (> -30 dB)")
            if dur < 5.0:
                warnings.append("Reference clip is very short (< 5s)")
            if clip_obj.get("silence_percentage", 0.0) > 30.0:
                warnings.append("Long silences (> 30%)")
            if clip_obj.get("sample_rate", 44100.0) < 22050.0:
                warnings.append(f"Low sample rate ({clip_obj.get('sample_rate')/1000.0:.1f} kHz)")
            if clip_obj.get("clipping_ratio", 0.0) > 0.005:
                warnings.append("Audio clipping/distortion detected")
            if not clip_obj.get("transcript") or len(clip_obj.get("transcript").strip()) < 3:
                warnings.append("Missing transcript (alignment degraded)")
                
            if warnings:
                self.warning_lbl.setText("⚠️ Warning: " + " | ".join(warnings))
                self.warning_bar.show()
            else:
                self.warning_bar.hide()
        else:
            self.ref_dur_lbl.setText("--")
            self.ref_qual_lbl.setText("--")
            self.ref_qual_lbl.setStyleSheet("color: #F2EFEB;")
            self.ref_noise_lbl.setText("--")
            self.ref_style_lbl.setText("--")
            self.warning_bar.hide()

    def _on_ref_clip_override_changed(self, index):
        path = self.ref_clip_combo.itemData(index)
        if path:
            self.selected_ref_override_path = path
        else:
            self.selected_ref_override_path = None
        self._update_ref_preview_details()
        self.update_editor_stats()
        
    def update_metrics_display(self):
        profile_name = self.profile_combo.currentText()
        if profile_name.startswith("+"):
            # Use first available profile or fallback
            from legends_labs.modules.voice_clone.voice_memory import voice_memory as _vm
            _all = _vm.get_all_style_names()
            profile_name = _all[0] if _all else "Fenil"
        self.current_profile_name = profile_name
        self.voice_name_lbl.setText(f"Voice: {profile_name}")
        
        from legends_labs.modules.voice_clone.voice_memory import voice_memory
        style = voice_memory.get_style(profile_name)
        clips = voice_memory.get_clips_with_emotions(profile_name)
        
        self.current_clips = clips
        
        self.ref_clip_combo.blockSignals(True)
        self.ref_clip_combo.clear()
        self.ref_clip_combo.addItem("Auto (Smart Selection)", "")
        for c in clips:
            filename = os.path.basename(c["path"])
            self.ref_clip_combo.addItem(filename, c["path"])
        self.ref_clip_combo.setCurrentIndex(0)
        self.ref_clip_combo.blockSignals(False)
        
        self.selected_ref_override_path = None
        
        if clips:
            refs = len(clips)
            total_dur = sum(c.get("duration") or 0.0 for c in clips)
            avg_noise = sum(c.get("noise_level") or -60.0 for c in clips) / refs
            avg_pitch = sum(c.get("avg_pitch") or 120.0 for c in clips) / refs
            avg_rate = sum(c.get("speaking_rate") or 3.0 for c in clips) / refs
            
            if total_dur >= 60.0:
                dur_text = f"{total_dur/60.0:.1f} Mins"
            else:
                dur_text = f"{total_dur:.1f}s"
                
            if avg_noise < -48.0:
                qual_text = "Clean"
                self.sim_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #43b581; border: none; background: transparent;")
            elif avg_noise < -38.0:
                qual_text = "Good"
                self.sim_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #faa61a; border: none; background: transparent;")
            else:
                qual_text = "Fair"
                self.sim_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #f04747; border: none; background: transparent;")
                
            self.sim_val.setText(qual_text)
            self.nat_val.setText(dur_text)
            self.noise_val.setText(f"{avg_noise:.1f} dBFS")
            self.pitch_val.setText(f"{avg_pitch:.1f} Hz")
            self.tempo_val.setText(f"{avg_rate:.2f} syl/s")
            self.data_val.setText(f"{refs} Clips")
        else:
            self.sim_val.setText("--")
            self.nat_val.setText("0s")
            self.noise_val.setText("--")
            self.pitch_val.setText("--")
            self.tempo_val.setText("--")
            self.data_val.setText("0 Clips")
            self.sim_val.setStyleSheet("font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #f04747; border: none; background: transparent;")
            
        self._update_ref_preview_details()
        self.update_editor_stats()

    def _update_generation_elapsed_time(self):
        import time
        elapsed = time.time() - self.generation_start_time
        self.live_elapsed_lbl.setText(f"Elapsed: {elapsed:.1f}s")

    def start_generation(self):
        script = self.script_input.toPlainText().strip()
        if not script:
            return
            
        self.gen_btn.set_generating(True)
        
        if hasattr(self, 'signal_line'):
            self.signal_line.set_active(True)
        if hasattr(self, 'particle_overlay'):
            self.particle_overlay.start_emission()
            
        # Start waveform thinking animation
        self.playback_waveform.start_animation("generating")
            
        # Reset timeline steps
        for lbl in self.timeline_steps:
            lbl.setStyleSheet("color: #7A7265; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
            txt = lbl.text().replace("✓ ", "").replace("⏳ ", "").replace("○ ", "")
            lbl.setText(f"○ {txt}")
            
        # Start timer
        import time
        self.generation_start_time = time.time()
        if not hasattr(self, "generation_timer"):
            self.generation_timer = QTimer(self)
            self.generation_timer.timeout.connect(self._update_generation_elapsed_time)
        self.generation_timer.start(100)
        
        from legends_labs.modules.voice_clone.workers.tts_worker import TTSWorker
        from legends_labs.core.task_queue import task_queue
        
        engine = "Fish Speech 1.5"

        worker = TTSWorker(
            script=script,
            engine=engine,
            voice_profile=getattr(self, "current_profile_name", "Fenil"),
            emotion_level=self.emotion_slider.value(),
            selected_reference_clip=getattr(self, "selected_ref_override_path", None)
        )
        
        def on_prog(val, msg):
            self.gen_btn.set_progress(val)
            self.live_stage_lbl.setText(f"Stage: {msg}")
            
            # Map val to active stepper index
            active_idx = 0
            if val >= 98: active_idx = 7
            elif val >= 80: active_idx = 6
            elif val >= 65: active_idx = 5
            elif val >= 50: active_idx = 4
            elif val >= 35: active_idx = 3
            elif val >= 20: active_idx = 2
            elif val >= 10: active_idx = 1
            
            for idx, lbl in enumerate(self.timeline_steps):
                txt = lbl.text().replace("✓ ", "").replace("⏳ ", "").replace("○ ", "")
                if idx < active_idx:
                    lbl.setStyleSheet("color: #43b581; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
                    lbl.setText(f"✓ {txt}")
                elif idx == active_idx:
                    lbl.setStyleSheet("color: #F5C400; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
                    lbl.setText(f"⏳ {txt}")
                else:
                    lbl.setStyleSheet("color: #7A7265; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600;")
                    lbl.setText(f"○ {txt}")
            
        def on_fin():
            self.gen_btn.set_generating(False)
            self.gen_btn.set_progress(0)
            self.live_stage_lbl.setText("Stage: Idle")
            self.playback_waveform.stop_animation()
            if hasattr(self, "generation_timer"):
                self.generation_timer.stop()
            if hasattr(self, 'signal_line'):
                self.signal_line.set_active(False)
            if hasattr(self, 'particle_overlay'):
                self.particle_overlay.stop_emission()
                
        worker.signals.progress.connect(on_prog)
        worker.signals.finished.connect(on_fin)
        
        def on_generation_complete(result_path):
            self.progress.setText(f"Generation Complete!")
            self.progress.setStyleSheet("color: #43b581;")
            self.last_generated_path = result_path
            
            # Switch to playback toolbar
            self.bottom_bar_container.setCurrentIndex(1)
            
            # Load audio engine
            if not hasattr(self, "audio_engine"):
                from legends_labs.audio.audio_engine import AudioEngine
                self.audio_engine = AudioEngine(self)
                self.audio_engine.position_changed.connect(self._on_audio_pos_changed)
                self.audio_engine.duration_changed.connect(self._on_audio_duration_changed)
                self.audio_engine.state_changed.connect(self._on_audio_state_changed)
                self.seekbar.sliderMoved.connect(self._on_seek_moved)
                self.play_btn.clicked.connect(self._toggle_playback)
            
            self.audio_engine.load(result_path)
            
            # Show live
            try:
                import soundfile as sf
                import numpy as np
                data, sr = sf.read(result_path, always_2d=True)
                mono = data[:, 0]
                
                target_samples = 4000
                if len(mono) > target_samples:
                    indices = np.linspace(0, len(mono) - 1, target_samples).astype(int)
                    mono = mono[indices]
                
                self.playback_waveform.set_audio_data(mono)
                self.playback_waveform.playhead_pos = 0.0
            except Exception as e:
                print(f"Error loading waveform visualizer: {e}")
            
        worker.signals.result.connect(on_generation_complete)
        worker.signals.error.connect(self.show_error)
        
        task_queue.submit(worker)

    def _on_audio_pos_changed(self, pos_ms):
        if not self.seekbar.isSliderDown():
            self.seekbar.setValue(pos_ms)
        s = pos_ms // 1000
        m = s // 60
        s = s % 60
        self.current_time_lbl.setText(f"{m}:{s:02d}")
        
        if hasattr(self, "audio_engine") and self.audio_engine.duration > 0:
            self.playback_waveform.playhead_pos = pos_ms / self.audio_engine.duration
            self.playback_waveform.update()

    def _on_audio_duration_changed(self, dur_ms):
        self.seekbar.setRange(0, dur_ms)
        s = dur_ms // 1000
        m = s // 60
        s = s % 60
        self.total_time_lbl.setText(f"{m}:{s:02d}")

    def _on_audio_state_changed(self, state):
        import PySide6.QtWidgets as QtWidgets
        if state == 1: # Playing
            self.play_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))

    def _on_waveform_seek(self, pos_ratio):
        if hasattr(self, "audio_engine") and self.audio_engine.duration > 0:
            self.audio_engine.set_position(int(pos_ratio * self.audio_engine.duration))

    def _on_seek_moved(self, pos):
        if hasattr(self, "audio_engine"):
            self.audio_engine.set_position(pos)

    def _toggle_playback(self):
        if not hasattr(self, "audio_engine"): return
        
        if getattr(self.audio_engine, "_is_playing", False):
            self.audio_engine.pause()
        else:
            self.audio_engine.play()

    def show_error(self, err_type, err_msg):
        self.gen_btn.setEnabled(True)
        self.gen_btn.set_generating(False)
        self.gen_btn.set_progress(0)
        if hasattr(self, 'signal_line'):
            self.signal_line.set_active(False)
        if hasattr(self, 'particle_overlay'):
            self.particle_overlay.stop_emission()
            
        self.progress_ring.hide()
        self.progress.setStyleSheet("color: #f04747; font-weight: bold;")
        self.progress.setText(f"Error: {err_type}")
        self.progress.show()
        print(f"Generation worker error [{err_type}]: {err_msg}")

    def show_evolve_error(self, err_type, err_msg):
        self.add_rec_btn.setEnabled(True)
        self.live_rec_btn.setEnabled(True)
        self.lora_btn.setEnabled(True)
        self.evolve_ring.hide()
        self.evolve_progress.setStyleSheet("color: #f04747; font-weight: bold;")
        self.evolve_progress.setText(f"Error: {err_type}")
        self.evolve_progress.show()
        print(f"Evolution worker error [{err_type}]: {err_msg}")
        with open(r"H:\legends-labs\error_log2.txt", "w") as f:
            f.write(err_msg)
        
    def export_voiceover(self):
        import shutil
        from PySide6.QtWidgets import QFileDialog
        if getattr(self, "last_generated_path", None):
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Voiceover", "", "Audio Files (*.wav *.m4a)")
            if file_path:
                shutil.copy(self.last_generated_path, file_path)
                self.progress.setText(f"Exported successfully to {file_path}")

    def start_batch_import(self):
        from PySide6.QtWidgets import QFileDialog
        from legends_labs.modules.voice_clone.workers.batch_import_worker import BatchImportWorker
        from legends_labs.core.task_queue import task_queue
        
        folder = QFileDialog.getExistingDirectory(self, "Select Folder of Old Recordings")
        if not folder: return
            
        self.add_rec_btn.setEnabled(False)
        self.evolve_ring.show()
        self.evolve_progress.show()
        self.evolve_progress.setText("Importing recordings...")
        self.evolve_progress.setStyleSheet("color: #5865F2;")
        
        profile_name = self.profile_combo.currentText().strip()
        if profile_name.startswith("+"): profile_name = "Fenil"
        
        worker = BatchImportWorker(folder_path=folder, style_name=profile_name, auto_clean=True)
        worker.signals.progress.connect(lambda val, msg: (self.evolve_progress.setText(f"{msg} ({val}%)" if val > 0 else msg), self.evolve_ring.set_value(val)))
        
        def on_batch_result(msg):
            self.evolve_progress.setText(msg)
            self.evolve_progress.setStyleSheet("color: #43b581;")
            self.update_metrics_display()
            
        worker.signals.result.connect(on_batch_result)
        worker.signals.error.connect(self.show_evolve_error)
        self.cancel_task_btn.show()
        worker.signals.finished.connect(self.cancel_task_btn.hide)
        task_queue.submit(worker)

    def start_live_training(self):
        from PySide6.QtWidgets import QDialog
        from legends_labs.modules.voice_clone.views.live_training_dialog import LiveTrainingDialog
        
        dialog = LiveTrainingDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.saved_file_path:
            self.evolve_ring.show()
            self.evolve_progress.show()
            self.evolve_progress.setText("Learning from new recording...")
            self.add_rec_btn.setEnabled(False)
            self.live_rec_btn.setEnabled(False)
            
            from legends_labs.modules.voice_clone.workers.performance_analyzer import PerformanceAnalyzerWorker
            from legends_labs.core.task_queue import task_queue
            
            profile_name = getattr(self, "current_profile_name", "Fenil")
            
            worker = PerformanceAnalyzerWorker(audio_path=dialog.saved_file_path, style_name=profile_name, auto_clean=True)
            worker.signals.progress.connect(lambda val, msg: (self.evolve_progress.setText(f"{msg} ({val}%)" if val > 0 else msg), self.evolve_ring.set_value(val)))
            
            
            def on_evolve_result(msg):
                self.evolve_progress.setText(msg)
                self.evolve_progress.setStyleSheet("color: #43b581;")
                self.update_metrics_display()
                
            worker.signals.result.connect(on_evolve_result)
            worker.signals.error.connect(self.show_evolve_error)
            self.cancel_task_btn.show()
            worker.signals.finished.connect(self.cancel_task_btn.hide)
            task_queue.submit(worker)

    def start_lora_training(self):
        profile_name = getattr(self, "current_profile_name", "Fenil")
            
        self.lora_btn.setEnabled(False)
        self.evolve_ring.show()
        self.evolve_progress.show()
        self.evolve_progress.setText("Preparing LoRA Dataset...")
        self.evolve_progress.setStyleSheet("color: #f5c400; font-weight: bold;")
        
        from legends_labs.modules.voice_clone.workers.lora_trainer import LoRATrainingWorker
        from legends_labs.core.task_queue import task_queue
        
        worker = LoRATrainingWorker(style_name=profile_name)
        worker.signals.progress.connect(lambda val, msg: (self.evolve_progress.setText(f"{msg} ({val}%)" if val > 0 else msg), self.evolve_ring.set_value(val)))
        
        def on_lora_result(msg):
            self.evolve_progress.setText(msg)
            self.evolve_progress.setStyleSheet("color: #43b581;")
            
            from legends_labs.modules.voice_clone.voice_memory import voice_memory
            self.profile_combo.clear()
            for style_name in voice_memory.styles.keys():
                self.profile_combo.addItem(style_name)
            self.profile_combo.addItem("+ Create New Voice Style")
            self.profile_combo.setCurrentText(profile_name)
            self.update_metrics_display()
                
        worker.signals.result.connect(on_lora_result)
        worker.signals.error.connect(self.show_evolve_error)
        self.cancel_task_btn.show()
        worker.signals.finished.connect(self.cancel_task_btn.hide)
        task_queue.submit(worker)

    def cancel_current_task(self):
        # We perform a soft UI reset (the thread will finish in background but UI is freed)
        self.evolve_progress.setText("Task cancelled.")
        self.evolve_progress.setStyleSheet("color: #f04747;")
        self.cancel_task_btn.hide()
        self.add_rec_btn.setEnabled(True)
        self.live_rec_btn.setEnabled(True)
        self.lora_btn.setEnabled(True)
        
        # If the python cleaner script is running as a subprocess, forcefully kill it
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info.get('cmdline')
                if cmd and 'cleaner_script.py' in cmd:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def _on_style_selected(self, btn):
        for b in self.style_btns:
            if b != btn:
                b.setChecked(False)
        btn.setChecked(True)
        # Mock logic: adjust sliders/advanced settings based on style
        style = btn.text()
        if style == "Natural":
            self.emotion_slider.setValue(40)
            self.speed_slider.setValue(100)
        elif style == "Podcast":
            self.emotion_slider.setValue(60)
            self.speed_slider.setValue(110)
        elif style == "Documentary":
            self.emotion_slider.setValue(30)
            self.speed_slider.setValue(90)
        elif style == "Cinematic":
            self.emotion_slider.setValue(90)
            self.speed_slider.setValue(85)
        elif style == "Storytelling":
            self.emotion_slider.setValue(80)
            self.speed_slider.setValue(95)
        elif style == "Tutorial":
            self.emotion_slider.setValue(30)
            self.speed_slider.setValue(115)
        elif style == "Advertisement":
            self.emotion_slider.setValue(100)
            self.speed_slider.setValue(120)
        elif style == "Whisper":
            self.emotion_slider.setValue(10)
            self.speed_slider.setValue(80)
            
    def _on_pace_changed(self, val):
        if val < 80:
            self.pace_val_lbl.setText("Slow")
        elif val > 120:
            self.pace_val_lbl.setText("Fast")
        else:
            self.pace_val_lbl.setText("Normal")
            
    def _toggle_advanced(self):
        visible = not self.adv_content.isVisible()
        self.adv_content.setVisible(visible)
        self.adv_btn.setText("Advanced Settings ▲" if visible else "Advanced Settings ▼")
