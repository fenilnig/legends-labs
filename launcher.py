import sys
import os
import subprocess

if __name__ == '__main__':
    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(project_root, "src")
    
    # Path to the actual python executable inside venv
    python_exe = os.path.join(project_root, "venv", "Scripts", "python.exe")
    main_script = os.path.join(project_root, "src", "legends_labs", "main.py")
    
    # CREATE_NO_WINDOW flag (0x08000000) tells Windows NOT to create a console window
    # for the python.exe process, effectively running it silently in the background
    # while still providing it with valid stdout/stderr handles (unlike pythonw.exe).
    CREATE_NO_WINDOW = 0x08000000
    
    subprocess.Popen(
        [python_exe, main_script],
        env=env,
        cwd=project_root,
        creationflags=CREATE_NO_WINDOW
    )
