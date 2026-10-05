from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

class WorkerSignals(QObject):
    started = Signal()
    progress = Signal(int, str)  # percentage, message
    result = Signal(object)
    error = Signal(str, str)
    finished = Signal()

class BaseWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

class TaskQueue:
    def __init__(self):
        self.pool = QThreadPool.globalInstance()
        self._active_workers = set()

    def submit(self, worker: BaseWorker):
        self._active_workers.add(worker)
        
        def _on_finish():
            self._active_workers.discard(worker)
            
        worker.signals.finished.connect(_on_finish)
        self.pool.start(worker)

task_queue = TaskQueue()
