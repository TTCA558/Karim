"""
Valorant Optimizer - Main Entry Point
=====================================
This is the main file that starts the application.
It checks for administrator privileges and launches the GUI.

Usage: Run this file with Python 3.x on Windows
       python main.py
"""

import os
import sys
import ctypes

def is_admin():
    """
    Check if the current process has administrator privileges.
    Returns True if running as admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """
    Restart the application with administrator privileges.
    Uses Windows ShellExecute with 'runas' verb to trigger UAC prompt.
    """
    try:
        script = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(
            None,           # Parent window handle
            "runas",        # Operation - "runas" triggers UAC elevation
            sys.executable, # Program to run (python.exe)
            f'"{script}"',  # Arguments (our script path)
            None,           # Working directory
            1               # SW_SHOWNORMAL
        )
        sys.exit(0)
    except Exception as e:
        print(f"Failed to get admin privileges: {e}")
        sys.exit(1)

def main():
    """
    Main function - entry point of the application.
    """
    if not is_admin():
        print("Requesting administrator privileges...")
        run_as_admin()
        return
    
    print("Running with administrator privileges ✓")
    
    try:
        from ui.gui import ValorantOptimizerGUI
        app = ValorantOptimizerGUI()
        app.run()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all files are in the correct folders.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()