from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt

class LibraryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - Tree
        tree_layout = QVBoxLayout()
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        icon_lbl = QLabel()
        from legends_labs.ui.theme import get_icon
        icon_lbl.setPixmap(get_icon("library").pixmap(24, 24))
        
        lbl = QLabel("Project Library")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        
        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(lbl)
        title_layout.addStretch()
        
        tree_layout.addWidget(title_widget)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("QTreeWidget { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #333333; border-radius: 6px; } QTreeWidget::item { padding: 5px; } QTreeWidget::item:selected { background-color: #5865F2; }")
        
        folders = ["Voiceovers", "Music", "Stems", "Scripts", "Recordings", "Exports"]
        for f in folders:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, f" {f}")
            
        self.tree.itemClicked.connect(self.on_tree_item_selected)
        tree_layout.addWidget(self.tree)
        layout.addLayout(tree_layout, stretch=2)
        
        # Right side - File details
        details_layout = QVBoxLayout()
        details_title = QLabel("File Details")
        details_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #888888;")
        details_layout.addWidget(details_title)
        
        self.details_label = QLabel("Select a file to view its details")
        self.details_label.setAlignment(Qt.AlignCenter)
        self.details_label.setStyleSheet("background-color: #1e1e1e; border: 1px dashed #333333; border-radius: 6px; color: #555555;")
        details_layout.addWidget(self.details_label, stretch=1)
        
        self.open_btn = QPushButton("Open in Editor")
        self.open_btn.setStyleSheet("QPushButton { background-color: #5865F2; color: white; padding: 10px; border-radius: 4px; font-weight: bold; }")
        self.open_btn.clicked.connect(self.on_open_in_editor)
        details_layout.addWidget(self.open_btn)
        
        layout.addLayout(details_layout, stretch=1)

    def on_tree_item_selected(self, item, column):
        name = item.text(0)
        self.details_label.setText(f"Selected: {name}\nType: Folder\nItems: —")
        self.details_label.setStyleSheet("background-color: #1e1e1e; border: 1px dashed #333333; border-radius: 6px; color: #e0e0e0; padding: 10px;")

    def on_open_in_editor(self):
        selected = self.tree.currentItem()
        if selected:
            QMessageBox.information(self, "Open in Editor", f"Opening '{selected.text(0)}' in the Audio Editor is not yet implemented.")
        else:
            QMessageBox.warning(self, "Open in Editor", "Please select an item from the library first.")
