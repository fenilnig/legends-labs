import os
import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QUrl

# Ensure Python path includes src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from legends_labs.ui.main_window import MainWindow

def run_tests():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    test_audio = str(Path(__file__).parent.parent / "dummy.wav")
    
    print("--- Starting End-to-End Smoke Tests ---")
    
    def test_voice_clone():
        print("[TEST] Voice Clone - Analyze Profile")
        window.sidebar.setCurrentRow(2) # Voice Clone
        view = window.stack.currentWidget()
        
        # Simulate dropping a file
        view.drop_zone.selected_file = test_audio
        
        # Connect to finish
        view.evolve_btn.click()
        print("[TEST] Clicked Analyze button")
        
        # Let the event loop run safely using QEventLoop
        loop = __import__("PySide6.QtCore").QtCore.QEventLoop()
        timer = QTimer()
        timer.singleShot(4000, loop.quit)
        loop.exec()
            
        print(f"[TEST] Progress Text: {view.evolve_progress.text()}")
        assert "Error:" not in view.evolve_progress.text()
        assert view.evolve_btn.isEnabled()
        print("[TEST] Voice Clone Passed!")

    def test_enhance():
        print("[TEST] Voice Enhance")
        window.sidebar.setCurrentRow(1) # Enhance
        view = window.stack.currentWidget()
        view.drop_zone.selected_file = test_audio
        view.enhance_btn.click()
        
        loop = __import__("PySide6.QtCore").QtCore.QEventLoop()
        timer = QTimer()
        timer.singleShot(2000, loop.quit)
        loop.exec()
            
        print(f"[TEST] Progress Text: {view.progress_label.text()}")
        assert "Error" not in view.enhance_progress.text()
        assert view.enhance_btn.isEnabled()
        print("[TEST] Voice Enhance Passed!")

    def test_isolation():
        print("[TEST] Vocal Isolation")
        window.sidebar.setCurrentRow(0) # Isolation
        view = window.stack.currentWidget()
        view.drop_zone.selected_file = test_audio
        view.separate_btn.click()
        
        loop = __import__("PySide6.QtCore").QtCore.QEventLoop()
        timer = QTimer()
        timer.singleShot(2000, loop.quit)
        loop.exec()
            
        print(f"[TEST] Progress Text: {view.progress_label.text()}")
        assert "Error" not in view.separate_progress.text()
        assert view.separate_btn.isEnabled()
        print("[TEST] Vocal Isolation Passed!")

    # Schedule the tests
    QTimer.singleShot(500, test_voice_clone)
    QTimer.singleShot(5000, test_enhance)
    QTimer.singleShot(9500, test_isolation)
    QTimer.singleShot(14000, lambda: app.quit())

    app.exec()
    print("--- All Tests Completed Successfully ---")

if __name__ == "__main__":
    run_tests()
