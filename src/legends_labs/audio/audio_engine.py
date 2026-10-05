import os
import threading
import time
import numpy as np
import soundfile as sf
from PySide6.QtCore import QObject, Signal
import sounddevice as sd

class AudioEngine(QObject):
    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(int) # 0 = Stopped, 1 = Playing, 2 = Paused
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._sr = 44100
        self._duration_ms = 0
        self._position_frames = 0
        self._volume = 1.0
        
        self._is_playing = False
        self._stream = None
        self._stream_thread = None
        
    def _on_error(self, msg):
        print(msg)
        self.error_occurred.emit(msg)

    def load(self, file_path: str):
        if not os.path.exists(file_path):
            self._on_error(f"Audio file not found: {file_path}")
            return
            
        self.stop()
        
        try:
            # Load into memory (always 2D for sounddevice)
            data, sr = sf.read(file_path, always_2d=True)
            self._data = data.astype(np.float32)
            self._sr = sr
            self._duration_ms = int((len(self._data) / sr) * 1000)
            self._position_frames = 0
            self.duration_changed.emit(self._duration_ms)
            self.position_changed.emit(0)
            self.state_changed.emit(0) # Stopped
        except Exception as e:
            self._on_error(f"Failed to load audio: {e}")
            
    def play(self):
        if self._data is None:
            return
            
        if self._is_playing:
            return
            
        if self._position_frames >= len(self._data):
            self._position_frames = 0
            
        self._is_playing = True
        self.state_changed.emit(1) # Playing
        
        def _play_thread():
            def callback(outdata, frames, time, status):
                if not self._is_playing:
                    raise sd.CallbackStop()
                    
                chunk_end = self._position_frames + frames
                if self._position_frames >= len(self._data):
                    outdata.fill(0)
                    raise sd.CallbackStop()
                    
                valid_frames = len(self._data) - self._position_frames
                if valid_frames >= frames:
                    outdata[:] = self._data[self._position_frames:chunk_end] * self._volume
                else:
                    outdata[:valid_frames] = self._data[self._position_frames:] * self._volume
                    outdata[valid_frames:].fill(0)
                    
                self._position_frames += frames
                self.position_changed.emit(int((self._position_frames / self._sr) * 1000))
                
                if self._position_frames >= len(self._data):
                    raise sd.CallbackStop()

            try:
                with sd.OutputStream(samplerate=self._sr, channels=self._data.shape[1], callback=callback):
                    while self._is_playing and self._position_frames < len(self._data):
                        sd.sleep(50)
            except Exception as e:
                self.error_occurred.emit(str(e))
                
            self._is_playing = False
            self.state_changed.emit(0) # Stopped/Paused
            
        self._stream_thread = threading.Thread(target=_play_thread, daemon=True)
        self._stream_thread.start()
        
    def pause(self):
        self._is_playing = False
        self.state_changed.emit(2) # Paused
        
    def stop(self):
        self._is_playing = False
        self._position_frames = 0
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=1.0)
        self.position_changed.emit(0)
        self.state_changed.emit(0)
        
    def set_position(self, pos_ms: int):
        if self._data is None:
            return
        self._position_frames = min(int((pos_ms / 1000.0) * self._sr), len(self._data))
        self.position_changed.emit(int((self._position_frames / self._sr) * 1000))
        
    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
        
    @property
    def duration(self) -> int:
        return self._duration_ms
        
    @property
    def position(self) -> int:
        return int((self._position_frames / self._sr) * 1000) if self._data is not None else 0

    @property
    def state(self):
        return 1 if self._is_playing else 0
