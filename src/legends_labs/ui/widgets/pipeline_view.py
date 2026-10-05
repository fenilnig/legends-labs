from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, Signal
from legends_labs.core.pipeline import ProcessingPipeline, PipelineNode

class PipelineNodeWidget(QWidget):
    def __init__(self, node: PipelineNode, parent=None):
        super().__init__(parent)
        self.node = node
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Status indicator
        self.status_lbl = QLabel("")
        self.update_status()
        layout.addWidget(self.status_lbl)
        
        # Name
        name_lbl = QLabel(self.node.operation.title())
        name_lbl.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        layout.addWidget(name_lbl)
        
        layout.addStretch()
        
    def update_status(self):
        if self.node.is_dirty:
            self.status_lbl.setStyleSheet("color: #faa61a;") # Yellow
        else:
            self.status_lbl.setStyleSheet("color: #43b581;") # Green


class PipelineView(QWidget):
    
    def __init__(self, pipeline: ProcessingPipeline = None, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("AI History Pipeline")
        header.setStyleSheet("color: #888888; font-weight: bold;")
        layout.addWidget(header)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background: #1e1e1e; border: 1px solid #333333; border-radius: 4px; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid #333333; }
            QListWidget::item:selected { background: #2a2a2a; border-left: 3px solid #5865F2; }
        """)
        layout.addWidget(self.list_widget)
        
        self.refresh()
        
    def refresh(self):
        self.list_widget.clear()
        if not self.pipeline: return
        
        for node in self.pipeline.nodes:
            item = QListWidgetItem()
            widget = PipelineNodeWidget(node)
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            item.setData(Qt.UserRole, node.id)
            
    def set_pipeline(self, pipeline: ProcessingPipeline):
        self.pipeline = pipeline
        self.refresh()
