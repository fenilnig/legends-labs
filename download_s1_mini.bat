@echo off
echo ============================================
echo  Fish Speech S1 Mini Model Downloader
echo ============================================
echo.

:: Check login
echo Checking HuggingFace authentication...
H:\legends-labs\venv_fish\Scripts\python.exe -c "from huggingface_hub import HfApi; api = HfApi(); print('Logged in as:', api.whoami()['name'])" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Not logged in to HuggingFace.
    echo Please run: H:\legends-labs\venv_fish\Scripts\huggingface-cli.exe login
    echo Then re-run this script.
    pause
    exit /b 1
)

echo.
echo Downloading fishaudio/openaudio-s1-mini (~3.4 GB)...
echo This will take a few minutes depending on your internet speed.
echo.

set PYTHONIOENCODING=utf-8
H:\legends-labs\venv_fish\Scripts\huggingface-cli.exe download fishaudio/openaudio-s1-mini --local-dir H:\legends-labs\checkpoints\openaudio-s1-mini

if errorlevel 1 (
    echo.
    echo ERROR: Download failed. Make sure you have accepted the model license at:
    echo https://huggingface.co/fishaudio/openaudio-s1-mini
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Download complete!
echo  Model saved to: H:\legends-labs\checkpoints\openaudio-s1-mini
echo  Restart the app to use Fish Speech S1 Mini.
echo ============================================
pause
