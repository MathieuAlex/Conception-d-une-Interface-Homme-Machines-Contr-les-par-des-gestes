"""
setup.py — cx_Freeze packaging configuration.

Build a standalone executable with:

    python setup.py build

The resulting executable will be placed in the build/ directory.

Author: Alex Mathieu
"""

import sys
from cx_Freeze import setup, Executable

# ---------------------------------------------------------------------------
# Build options
# ---------------------------------------------------------------------------
build_options = {
    "packages": [
        "cv2",
        "mediapipe",
        "pyautogui",
        "tkinter",
        "numpy",
        "PIL",
        "hand_detector",
        "gesture_engine",
        "virtual_mouse",
        "ui",
    ],
    "excludes": ["unittest", "email", "http", "xml", "pydoc"],
    "include_files": [],
    "optimize": 1,
}

# On Windows use the GUI base so no console window appears.
base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="VirtualMouse",
        shortcut_name="Virtual Mouse",
    )
]

setup(
    name="VirtualMouse",
    version="1.0.0",
    description="Virtual Mouse — Touchless cursor control via hand gestures",
    author="Alex Mathieu",
    options={"build_exe": build_options},
    executables=executables,
)
