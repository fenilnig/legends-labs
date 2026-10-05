from PySide6.QtCore import QObject, Signal

# We don't import torch at the top level anymore to avoid 5-10 second boot times.
# We will import it lazily inside the functions that actually need it.


class VRAMManager(QObject):
    vram_updated = Signal(int, int) # used, total

    def __init__(self):
        super().__init__()
        self.total_vram = self._get_total_vram()
        self.used_vram = 0
        self.loaded_models = {}

    def _get_total_vram(self) -> int:
        """Return total GPU VRAM in MiB, or 0 if no GPU is available."""
        try:
            import torch
            if torch.cuda.is_available():
                return int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
        except Exception:
            pass

        # Fallback: try nvidia-smi
        try:
            import subprocess, re
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                total = int(result.stdout.strip().splitlines()[0])
                return total
        except Exception:
            pass

        return 0  # Unknown — no GPU detected

    def _get_used_vram(self) -> int:
        """Return currently used GPU VRAM in MiB, or 0 if unavailable."""
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            if result.returncode == 0:
                val = int(result.stdout.strip().splitlines()[0])
                with open(r"H:\legends-labs\tmp\vram_debug.log", "a") as f:
                    f.write(f"VRAM returned: {val}\n")
                return val
            else:
                with open(r"H:\legends-labs\tmp\vram_debug.log", "a") as f:
                    f.write(f"VRAM used error code: {result.returncode}, stderr: {result.stderr}\n")
        except Exception as e:
            with open(r"H:\legends-labs\tmp\vram_debug.log", "a") as f:
                f.write(f"VRAM used exception: {e}\n")
            pass

        return 0

    def update_vram(self):
        """Query actual GPU VRAM usage and emit the updated signal."""
        self.used_vram = self._get_used_vram()
        self.total_vram = self._get_total_vram()
        self.vram_updated.emit(self.used_vram, self.total_vram)
        try:
            from legends_labs.core.signals import signal_bus
            signal_bus.vram_updated.emit(self.used_vram, self.total_vram)
        except Exception:
            pass


_vram_manager_instance: VRAMManager | None = None


def get_vram_manager() -> VRAMManager:
    """Return the application-wide ``VRAMManager`` singleton (created on first call)."""
    global _vram_manager_instance  # noqa: PLW0603
    if _vram_manager_instance is None:
        _vram_manager_instance = VRAMManager()
    return _vram_manager_instance
