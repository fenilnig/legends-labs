$ErrorActionPreference = "Stop"
$venv = "H:\legends-labs\venv_ml\Scripts\python.exe"

Write-Host "1/3 Installing PyTorch with CUDA..."
& $venv -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Write-Host "2/3 Installing TTS (XTTS)..."
& $venv -m pip install TTS

Write-Host "3/3 Installing additional dependencies..."
& $venv -m pip install edge-tts librosa soundfile PySide6

Write-Host "Installation Complete!"
