"""
ui.py — Tkinter graphical interface for the Virtual Mouse application.

Layout
------
  ┌──────────────────────────────────────────┐
  │  🖱 Virtual Mouse          [🌙 Night]    │
  ├──────────────────────────────────────────┤
  │            webcam feed (640×480)         │
  ├──────────────────────────────────────────┤
  │  FPS: 30   │  Clicks: 5   │  00:42       │
  ├──────────────────────────────────────────┤
  │  [▶ Start]   Gesture: MOVE               │
  ├──────────────────────────────────────────┤
  │  Gesture guide                           │
  └──────────────────────────────────────────┘

Author: Alex Mathieu
"""

from __future__ import annotations

import threading
import time

import tkinter as tk

import cv2
from PIL import Image, ImageTk

from gesture_engine import Gesture
from virtual_mouse import VirtualMouse


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------
_THEMES: dict[str, dict[str, str]] = {
    "day": {
        "bg":        "#F4F4F8",
        "fg":        "#1A1A2E",
        "card_bg":   "#FFFFFF",
        "card_fg":   "#1A1A2E",
        "accent":    "#4A90D9",
        "btn_bg":    "#4A90D9",
        "btn_fg":    "#FFFFFF",
        "border":    "#D0D0DA",
        "guide_bg":  "#EAEAF2",
    },
    "night": {
        "bg":        "#1E1E2E",
        "fg":        "#CDD6F4",
        "card_bg":   "#313244",
        "card_fg":   "#CDD6F4",
        "accent":    "#89B4FA",
        "btn_bg":    "#89B4FA",
        "btn_fg":    "#1E1E2E",
        "border":    "#45475A",
        "guide_bg":  "#292C3C",
    },
}

_GESTURE_GUIDE = [
    ("☝",  "Index up",                    "Move cursor"),
    ("✌",  "Index + middle (close)",       "Left click"),
    ("🤙", "Index + pinky",               "Right click"),
    ("🖖", "Index + middle + ring",        "Scroll (move up/down)"),
]


class VirtualMouseUI:
    """Main application window."""

    def __init__(self, virtual_mouse: VirtualMouse) -> None:
        self._vm = virtual_mouse
        self._theme_name: str = "day"
        self._running: bool = False
        self._cap: cv2.VideoCapture | None = None
        self._photo: ImageTk.PhotoImage | None = None  # keeps reference alive
        self._lock = threading.Lock()

        self.root = tk.Tk()
        self.root.title("Virtual Mouse — Gesture Control")
        self.root.resizable(False, False)

        self._build_ui()
        self._apply_theme()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = self.root

        # ── Outer padding frame ──────────────────────────────────────
        self._outer = tk.Frame(root, padx=12, pady=10)
        self._outer.pack(fill=tk.BOTH, expand=True)

        # ── Title bar ────────────────────────────────────────────────
        title_bar = tk.Frame(self._outer)
        title_bar.pack(fill=tk.X, pady=(0, 8))

        self._title_lbl = tk.Label(
            title_bar,
            text="🖱  Virtual Mouse",
            font=("Helvetica", 16, "bold"),
            anchor="w",
        )
        self._title_lbl.pack(side=tk.LEFT)

        self._theme_btn = tk.Button(
            title_bar,
            text="🌙 Night",
            command=self._toggle_theme,
            width=10,
            relief=tk.FLAT,
            cursor="hand2",
            font=("Helvetica", 10),
        )
        self._theme_btn.pack(side=tk.RIGHT)

        # ── Camera canvas ────────────────────────────────────────────
        self._canvas = tk.Label(self._outer, width=640, height=480, anchor="center")
        self._canvas.pack()

        # ── Metrics bar ──────────────────────────────────────────────
        metrics_bar = tk.Frame(self._outer)
        metrics_bar.pack(fill=tk.X, pady=(8, 0))

        self._fps_var = tk.StringVar(value="0")
        self._clicks_var = tk.StringVar(value="0")
        self._uptime_var = tk.StringVar(value="00:00")

        self._fps_card = self._make_metric_card(
            metrics_bar, "FPS", self._fps_var
        )
        self._fps_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 4))

        self._clicks_card = self._make_metric_card(
            metrics_bar, "Clicks", self._clicks_var
        )
        self._clicks_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

        self._uptime_card = self._make_metric_card(
            metrics_bar, "Uptime", self._uptime_var
        )
        self._uptime_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(4, 0))

        # ── Controls row ─────────────────────────────────────────────
        ctrl_row = tk.Frame(self._outer)
        ctrl_row.pack(fill=tk.X, pady=(8, 0))

        self._start_btn = tk.Button(
            ctrl_row,
            text="▶  Start",
            command=self._toggle_running,
            width=12,
            relief=tk.FLAT,
            cursor="hand2",
            font=("Helvetica", 11, "bold"),
        )
        self._start_btn.pack(side=tk.LEFT, padx=(0, 12))

        self._gesture_var = tk.StringVar(value="Gesture: —")
        self._gesture_lbl = tk.Label(
            ctrl_row,
            textvariable=self._gesture_var,
            font=("Helvetica", 11),
            anchor="w",
        )
        self._gesture_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── Gesture guide ────────────────────────────────────────────
        self._guide_frame = tk.LabelFrame(
            self._outer,
            text="  Gesture Guide  ",
            font=("Helvetica", 9, "bold"),
            padx=8,
            pady=6,
        )
        self._guide_frame.pack(fill=tk.X, pady=(10, 0))

        self._guide_rows: list[tuple[tk.Label, tk.Label]] = []
        for icon, name, action in _GESTURE_GUIDE:
            row = tk.Frame(self._guide_frame)
            row.pack(fill=tk.X, pady=1)
            lbl_name = tk.Label(
                row,
                text=f"{icon}  {name}",
                font=("Helvetica", 9),
                width=30,
                anchor="w",
            )
            lbl_name.pack(side=tk.LEFT)
            lbl_action = tk.Label(
                row,
                text=f"→  {action}",
                font=("Helvetica", 9),
                anchor="w",
            )
            lbl_action.pack(side=tk.LEFT)
            self._guide_rows.append((lbl_name, lbl_action))

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    @staticmethod
    def _make_metric_card(
        parent: tk.Widget, title: str, string_var: tk.StringVar
    ) -> tk.Frame:
        """Return a small card widget displaying a labelled metric value."""
        frame = tk.Frame(parent, relief=tk.FLAT, bd=1)
        tk.Label(frame, text=title, font=("Helvetica", 9)).pack(pady=(6, 0))
        tk.Label(
            frame,
            textvariable=string_var,
            font=("Helvetica", 20, "bold"),
        ).pack(pady=(0, 6))
        return frame

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _toggle_theme(self) -> None:
        self._theme_name = "night" if self._theme_name == "day" else "day"
        self._apply_theme()

    def _apply_theme(self) -> None:
        t = _THEMES[self._theme_name]

        self.root.configure(bg=t["bg"])
        self._outer.configure(bg=t["bg"])

        self._title_lbl.configure(bg=t["bg"], fg=t["fg"])
        self._title_lbl.master.configure(bg=t["bg"])  # title_bar frame

        self._theme_btn.configure(
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            activebackground=t["accent"],
            activeforeground=t["btn_fg"],
            text="☀  Day" if self._theme_name == "night" else "🌙  Night",
        )

        self._canvas.configure(bg=t["card_bg"])

        # Metric cards
        for card in (self._fps_card, self._clicks_card, self._uptime_card):
            card.configure(bg=t["card_bg"], highlightbackground=t["border"])
            for child in card.winfo_children():
                child.configure(bg=t["card_bg"], fg=t["card_fg"])

        # Controls row
        self._start_btn.configure(
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            activebackground=t["accent"],
            activeforeground=t["btn_fg"],
        )
        self._gesture_lbl.configure(bg=t["bg"], fg=t["fg"])
        self._gesture_lbl.master.configure(bg=t["bg"])  # ctrl_row frame

        # Metrics bar parent frame
        for card in (self._fps_card, self._clicks_card, self._uptime_card):
            card.master.configure(bg=t["bg"])

        # Guide
        self._guide_frame.configure(
            bg=t["guide_bg"],
            fg=t["fg"],
        )
        for row_frame in self._guide_frame.winfo_children():
            if isinstance(row_frame, tk.Frame):
                row_frame.configure(bg=t["guide_bg"])
                for lbl in row_frame.winfo_children():
                    lbl.configure(bg=t["guide_bg"], fg=t["fg"])

    # ------------------------------------------------------------------
    # Start / Stop
    # ------------------------------------------------------------------

    def _toggle_running(self) -> None:
        if self._running:
            self._running = False
            self._start_btn.configure(text="▶  Start")
        else:
            self._running = True
            self._start_btn.configure(text="⏹  Stop")
            threading.Thread(target=self._camera_loop, daemon=True).start()

    # ------------------------------------------------------------------
    # Camera thread
    # ------------------------------------------------------------------

    def _camera_loop(self) -> None:
        """Runs in a background thread; feeds frames to the UI via after()."""
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self.root.after(0, self._show_camera_error)
            self._running = False
            return

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._vm.cam_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._vm.cam_height)

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                break

            frame, gesture = self._vm.process_frame(frame)

            # Convert BGR → RGB → PIL → Tk
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=pil_img)

            # Schedule UI update on the main thread
            self.root.after(0, self._update_display, photo, gesture)

        self._cap.release()
        self._cap = None

    def _update_display(
        self, photo: ImageTk.PhotoImage, gesture: Gesture
    ) -> None:
        """Called on the main thread to refresh all UI elements."""
        # Keep a reference so the GC doesn't collect the image
        self._photo = photo
        self._canvas.configure(image=photo)

        self._fps_var.set(str(self._vm.fps))
        self._clicks_var.set(str(self._vm.total_clicks))
        self._uptime_var.set(self._vm.uptime)
        self._gesture_var.set(f"Gesture: {gesture.name}")

    def _show_camera_error(self) -> None:
        self._gesture_var.set("Error: cannot open camera")
        self._start_btn.configure(text="▶  Start")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        self._running = False
        time.sleep(0.15)
        self.root.destroy()

    def run(self) -> None:
        """Start the Tkinter event loop (blocking)."""
        self.root.mainloop()
