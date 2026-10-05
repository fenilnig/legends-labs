from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox, QLineEdit
from PySide6.QtCore import Qt
class DirectorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("director").pixmap(24, 24))
        
        lbl = QLabel("AI Director Mode")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        preset_lbl = QLabel("Preset:")
        preset_lbl.setStyleSheet("color: #e0e0e0;")
        title_layout.addWidget(preset_lbl)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["None (Raw)", "Elliot Alderson (Mr. Robot)", "LLM Director (Advanced)"])
        self.preset_combo.setStyleSheet("QComboBox { background-color: #242424; color: #e0e0e0; border: 1px solid #333333; padding: 5px; border-radius: 4px; }")
        title_layout.addWidget(self.preset_combo)
        
        layout.addWidget(title_widget)
        
        # LLM Settings Row
        llm_layout = QHBoxLayout()
        llm_layout.setContentsMargins(0, 0, 0, 10)
        
        provider_lbl = QLabel("LLM Provider:")
        provider_lbl.setStyleSheet("color: #888888; font-weight: bold;")
        llm_layout.addWidget(provider_lbl)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gemini", "OpenAI", "Ollama"])
        self.provider_combo.setStyleSheet("QComboBox { background-color: #242424; color: #e0e0e0; border: 1px solid #333333; padding: 5px; border-radius: 4px; }")
        llm_layout.addWidget(self.provider_combo)
        
        key_lbl = QLabel("API Key:")
        key_lbl.setStyleSheet("color: #888888; font-weight: bold; margin-left: 15px;")
        llm_layout.addWidget(key_lbl)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Paste API Key here (or leave blank for Ollama)")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("QLineEdit { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #333333; padding: 5px; border-radius: 4px; }")
        llm_layout.addWidget(self.api_key_input, stretch=1)
        
        layout.addLayout(llm_layout)
        
        subtitle = QLabel("Paste your script below. The local LLM will analyze it line-by-line and suggest pacing, emotion, and emphasis.")
        subtitle.setStyleSheet("color: #888888; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        content = QHBoxLayout()
        
        # Script input
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter your script to be analyzed...")
        self.script_input.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #333333; border-radius: 6px; padding: 10px; font-size: 14px; }")
        content.addWidget(self.script_input, stretch=1)
        
        # Analysis results
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setPlaceholderText("AI Director analysis will appear here...")
        self.analysis_output.setStyleSheet("QTextEdit { background-color: #242424; color: #43b581; border: 1px solid #333333; border-radius: 6px; padding: 10px; font-size: 14px; }")
        content.addWidget(self.analysis_output, stretch=1)
        
        layout.addLayout(content)
        
        self.analyze_btn = QPushButton("Analyze Script")
        self.analyze_btn.setStyleSheet("QPushButton { background-color: #5865F2; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 16px; } QPushButton:hover { background-color: #4752c4; }")
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        layout.addWidget(self.analyze_btn)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #faa61a; font-size: 14px; margin-top: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def on_analyze_clicked(self):
        text = self.script_input.toPlainText().strip()
        if not text:
            self.status_label.setText("Please enter a script to analyze.")
            return
            
        preset = self.preset_combo.currentText()
        if preset == "Elliot Alderson (Mr. Robot)":
            import re
            self.status_label.setText("Applying Elliot Alderson Preset...")
            
            output = "(Quiet. Thoughtful)\n"
            
            # Split by sentences (handling . ? !)
            sentences = re.split(r'(?<=[.?!])\s+', text)
            
            formatted_sentences = []
            for sentence in sentences:
                if not sentence: continue
                # Add micro-pauses after commas
                sentence = re.sub(r'(,)\s+', r'\1\n(Pause - 0.5s)\n', sentence)
                formatted_sentences.append(sentence)
                
            # Join with long pauses
            output += "\n(Pause - 1.2s)\n".join(formatted_sentences)
            
            self.analysis_output.setPlainText(output)
            self.status_label.setText("Success! Copy the output and paste it into the Voice Clone tab.")
        elif preset == "LLM Director (Advanced)":
            provider = self.provider_combo.currentText()
            api_key = self.api_key_input.text().strip()
            
            if provider in ["Gemini", "OpenAI"] and not api_key:
                self.status_label.setText(f"Error: Please enter an API key for {provider}.")
                return
                
            self.status_label.setText(f"Connecting to {provider} AI Director...")
            self.analyze_btn.setEnabled(False)
            self.analysis_output.clear()
            
            from legends_labs.modules.ai_director.workers.director_worker import AIDirectorWorker
            from legends_labs.core.task_queue import task_queue
            
            worker = AIDirectorWorker(script=text, provider=provider, api_key=api_key)
            
            def append_text(chunk):
                # Using cursor to append stream text
                cursor = self.analysis_output.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText(chunk)
                self.analysis_output.setTextCursor(cursor)
                
            worker.signals.chunk_received.connect(append_text)
            
            def on_finished():
                self.analyze_btn.setEnabled(True)
                self.status_label.setText("LLM Director analysis complete! Copy the output to the Voice Clone tab.")
                
            worker.signals.finished.connect(on_finished)
            
            def on_error(err_type, err_msg):
                self.analyze_btn.setEnabled(True)
                self.status_label.setText(f"Error: {err_type}")
                print(f"DirectorWorker Error: {err_msg}")
                
            worker.signals.error.connect(on_error)
            
            task_queue.submit(worker)
        else:
            self.status_label.setText("AI Director analysis coming soon - full models not yet integrated.")
            self.analysis_output.setPlainText(text)
