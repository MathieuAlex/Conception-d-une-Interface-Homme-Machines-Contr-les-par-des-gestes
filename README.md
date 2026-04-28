# Virtual Mouse — Gesture-Controlled HCI

Real-time, touchless cursor control using hand gesture recognition via webcam.  
No physical mouse or keyboard required — control your computer with just your hand.

## Stack

| Component        | Library / Tool                         |
|------------------|----------------------------------------|
| Computer vision  | OpenCV 4.8                             |
| Hand tracking    | MediaPipe Hands (21 landmarks)         |
| OS cursor control| PyAutoGUI                              |
| GUI              | Tkinter + Pillow                       |
| Numerical ops    | NumPy                                  |
| Packaging        | cx_Freeze (→ standalone `.exe`)        |

## Features

- **Cursor movement** — index finger pointing controls cursor position
- **Left click** — index + middle fingers pinched together
- **Right click** — index + pinky extended (devil-horns gesture)
- **Scroll** — index + middle + ring fingers extended; move hand up/down
- **Session metrics** — live FPS counter, total click count, session uptime
- **Day / Night theme** — toggle between light and dark colour schemes
- **Standalone executable** — packaged with cx_Freeze (`python setup.py build`)

## Gesture Reference

| Gesture              | Fingers extended                | Action        |
|----------------------|---------------------------------|---------------|
| ☝ Point              | Index only                      | Move cursor   |
| ✌ V-sign (close)    | Index + middle (tips together)  | Left click    |
| 🤙 Devil horns       | Index + pinky                   | Right click   |
| 🖖 Three fingers     | Index + middle + ring           | Scroll        |

## Architecture

```
HandDetector (MediaPipe wrapper)
        │  21 landmark coordinates
        ▼
GestureEngine
        │  Gesture enum value
        ▼
VirtualMouse (PyAutoGUI)
        │  moveTo / click / rightClick / scroll
        ▼
Operating System cursor
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Click **▶ Start** in the window to activate the webcam.  
A purple rectangle shows the active tracking zone.

## Build standalone executable

```bash
python setup.py build
```

The executable is written to the `build/` directory.

## Project structure

```
├── main.py               # Entry point
├── hand_detector.py      # MediaPipe Hands wrapper
├── gesture_engine.py     # Gesture classification
├── virtual_mouse.py      # Core engine (frame processing + OS actions)
├── ui.py                 # Tkinter GUI
├── setup.py              # cx_Freeze packaging
├── requirements.txt      # Python dependencies
└── test_gesture_engine.py# Unit tests
```

## Running tests

```bash
python -m pytest test_gesture_engine.py -v
```

## Author

Alex Mathieu

