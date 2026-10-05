import sys
from PySide6.QtWidgets import QApplication


def _unhandled_exception(exc_type, exc_value, exc_tb):
    """Top-level exception handler so crashes are logged instead of silently lost."""
    from loguru import logger
    logger.opt(exception=(exc_type, exc_value, exc_tb)).critical(
        "Unhandled exception"
    )


def main():
    import os
    from legends_labs.core.logger import setup_logging

    setup_logging()

    sys.excepthook = _unhandled_exception

    # Add local bin folder to PATH so ffmpeg and ffprobe are available to sub-processes
    bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    if os.path.exists(bin_path):
        os.environ["PATH"] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"
        
    # Generate a secure random token for the local inference server
    import secrets
    import subprocess
    import atexit
    
    # Generate a random secure token for this session
    server_token = secrets.token_hex(32)
    os.environ["LL_API_TOKEN"] = server_token
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    
    # Kill any orphaned ghost server on port 54321
    try:
        import psutil
        for conn in psutil.net_connections():
            if conn.laddr.port == 54321:
                try:
                    p = psutil.Process(conn.pid)
                    p.terminate()
                    p.wait(timeout=2)
                except:
                    pass
    except Exception as e:
        print(f"Warning: Could not kill orphaned server: {e}")
        
    # Spawn the inference server and route its logs to a file to prevent pipe blockage
    server_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tmp")
    os.makedirs(server_log_dir, exist_ok=True)
    server_log = open(os.path.join(server_log_dir, "server.log"), "w")
    
    # Find project root by traversing upwards until we find the parent containing 'venv_ml' or 'vendors'
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = None
    while True:
        if os.path.exists(os.path.join(curr_dir, "venv_ml")) or os.path.exists(os.path.join(curr_dir, "vendors")):
            project_root = curr_dir
            break
        parent = os.path.dirname(curr_dir)
        if parent == curr_dir:  # reached root of filesystem without finding it
            break
        curr_dir = parent
        
    if not project_root:
        # Fallback to 3 levels if not found dynamically
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Windows path for venv_ml python
    venv_ml_python = os.path.join(project_root, "venv_ml", "Scripts", "python.exe")
    # Unix path fallback just in case
    if not os.path.exists(venv_ml_python):
        venv_ml_python = os.path.join(project_root, "venv_ml", "bin", "python")
        
    server_python = venv_ml_python if os.path.exists(venv_ml_python) else sys.executable
    print(f"Spawning backend server using: {server_python}")
    
    env_copy = os.environ.copy()
    env_copy["PYTHONUNBUFFERED"] = "1"
    
    # Adjust PATH to prefer venv_ml's Scripts folder if using it, so dependencies load cleanly
    if server_python == venv_ml_python:
        venv_ml_scripts = os.path.dirname(venv_ml_python)
        env_copy["PATH"] = f"{venv_ml_scripts}{os.pathsep}{env_copy.get('PATH', '')}"
        # Prevent inheriting parent's venv path variables
        env_copy.pop("PYTHONPATH", None)
        env_copy.pop("PYTHONHOME", None)
    
    server_process = subprocess.Popen(
        [server_python, "-m", "legends_labs.server.main"],
        env=env_copy,
        stdout=server_log,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    # Ensure server shuts down when the UI exits
    atexit.register(lambda: (server_process.terminate(), server_log.close()))
    
    # Setup App
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(server_process.terminate)
    
    # Load Theme
    try:
        from legends_labs.ui.theme import load_theme
        load_theme(app)
    except ImportError as e:
        print(f"Warning: Could not load theme: {e}")

    # Show Splash
    try:
        from legends_labs.ui.splash_screen import AnimatedSplashScreen
        splash = AnimatedSplashScreen()
        splash.show()
        app.processEvents()
        
        splash.showMessage("Loading AI Engine...")
        app.processEvents()
        
        splash.showMessage("Initializing UI...")
        app.processEvents()
    except ImportError:
        splash = None

    # Load Main Window
    from legends_labs.ui.main_window import MainWindow
    window = MainWindow()
    
    if splash:
        splash.finish(window)
        
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
