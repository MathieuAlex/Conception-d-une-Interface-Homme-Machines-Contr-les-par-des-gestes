"""
virtual_mouse.py — Core virtual-mouse engine.

Ties together:
  HandDetector → GestureEngine → PyAutoGUI (OS cursor control)

Also accumulates session metrics (FPS, total clicks, uptime) that the UI
reads as plain attributes.

Author: Alex Mathieu
"""

from __future__ import annotations

import time

import cv2
import numpy as np
import pyautogui

from gesture_engine import Gesture, GestureEngine
from hand_detector import HandDetector

# Disable PyAutoGUI's built-in failsafe and artificial delay so the
# cursor responds instantly.
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0


class VirtualMouse:
    """
    Process a single webcam frame, decide what gesture was made and
    translate it into an OS-level cursor action.

    Parameters
    ----------
    cam_width, cam_height : int
        Expected capture resolution (used for coordinate mapping).
    frame_reduction : int
        Pixel margin on each edge of the frame that is excluded from the
        active tracking zone.  Gives the user comfortable room to reach
        screen edges.
    smoothing : int
        Number of frames over which cursor movement is interpolated.
        Higher values are smoother but slightly more laggy.
    click_cooldown_frames : int
        Minimum number of frames between two successive click events to
        avoid accidental double-clicks.
    """

    def __init__(
        self,
        cam_width: int = 640,
        cam_height: int = 480,
        frame_reduction: int = 80,
        smoothing: int = 7,
        click_cooldown_frames: int = 18,
    ) -> None:
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.frame_reduction = frame_reduction
        self.smoothing = smoothing
        self.click_cooldown_frames = click_cooldown_frames

        self.screen_width, self.screen_height = pyautogui.size()

        self._hand_detector = HandDetector()
        self._gesture_engine = GestureEngine()

        # Smoothed cursor position
        self._prev_x: float = 0.0
        self._prev_y: float = 0.0

        # Scroll state
        self._scroll_prev_y: int | None = None

        # Click debounce
        self._click_cooldown: int = 0

        # ── Session metrics ──────────────────────────────────────────
        self._session_start = time.time()
        self._fps_prev_time = time.time()

        #: Current frames-per-second (updated on every call to process_frame)
        self.fps: int = 0
        #: Cumulative click count since session start
        self.total_clicks: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self, frame) -> tuple:
        """
        Detect hand, classify gesture, execute OS action.

        Parameters
        ----------
        frame : numpy.ndarray
            Raw BGR frame from :class:`cv2.VideoCapture`.

        Returns
        -------
        annotated_frame : numpy.ndarray
            Frame with landmarks and active-zone rectangle drawn on it.
        gesture : Gesture
            Gesture that was detected in this frame.
        """
        frame = cv2.flip(frame, 1)

        frame = self._hand_detector.find_hands(frame)
        landmarks = self._hand_detector.find_positions(frame)

        gesture = self._gesture_engine.get_gesture(landmarks)

        if landmarks:
            self._execute(gesture, landmarks, frame)
        else:
            self._scroll_prev_y = None

        # Decrement click cooldown
        if self._click_cooldown > 0:
            self._click_cooldown -= 1

        # Draw active tracking rectangle
        h, w = frame.shape[:2]
        fr = self.frame_reduction
        cv2.rectangle(
            frame,
            (fr, fr),
            (w - fr, h - fr),
            (255, 0, 255),
            2,
        )

        # Update FPS
        now = time.time()
        elapsed = now - self._fps_prev_time
        self.fps = int(1.0 / elapsed) if elapsed > 0 else 0
        self._fps_prev_time = now

        return frame, gesture

    @property
    def uptime(self) -> str:
        """Session uptime formatted as MM:SS."""
        elapsed = int(time.time() - self._session_start)
        mins, secs = divmod(elapsed, 60)
        return f"{mins:02d}:{secs:02d}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute(self, gesture: Gesture, landmarks: list, frame) -> None:
        """Translate a gesture into cursor movement and/or OS events."""
        h, w = frame.shape[:2]
        fr = self.frame_reduction

        # ── Cursor movement ──────────────────────────────────────────
        if gesture in (Gesture.MOVE, Gesture.LEFT_CLICK):
            ix, iy = landmarks[8][1], landmarks[8][2]  # index fingertip

            # Map webcam active zone → full screen
            screen_x = np.interp(ix, (fr, w - fr), (0, self.screen_width))
            screen_y = np.interp(iy, (fr, h - fr), (0, self.screen_height))

            # Exponential smoothing
            smooth_x = self._prev_x + (screen_x - self._prev_x) / self.smoothing
            smooth_y = self._prev_y + (screen_y - self._prev_y) / self.smoothing

            pyautogui.moveTo(smooth_x, smooth_y)
            self._prev_x, self._prev_y = smooth_x, smooth_y

            # Highlight index tip
            cv2.circle(frame, (ix, iy), 10, (255, 0, 255), cv2.FILLED)

        # ── Left click ───────────────────────────────────────────────
        if gesture == Gesture.LEFT_CLICK and self._click_cooldown == 0:
            pyautogui.click()
            self.total_clicks += 1
            self._click_cooldown = self.click_cooldown_frames
            # Visual feedback: highlight middle tip too
            mx, my = landmarks[12][1], landmarks[12][2]
            cv2.circle(frame, (mx, my), 10, (0, 255, 0), cv2.FILLED)

        # ── Right click ──────────────────────────────────────────────
        if gesture == Gesture.RIGHT_CLICK and self._click_cooldown == 0:
            pyautogui.rightClick()
            self.total_clicks += 1
            self._click_cooldown = self.click_cooldown_frames

        # ── Scroll ───────────────────────────────────────────────────
        if gesture == Gesture.SCROLL:
            iy = landmarks[8][2]  # track index tip vertical position
            if self._scroll_prev_y is not None:
                dy = self._scroll_prev_y - iy
                if abs(dy) > 5:
                    pyautogui.scroll(int(dy / 8))
            self._scroll_prev_y = iy
        else:
            self._scroll_prev_y = None
