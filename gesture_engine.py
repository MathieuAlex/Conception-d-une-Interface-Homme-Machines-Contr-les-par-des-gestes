"""
gesture_engine.py — Gesture classification from MediaPipe landmarks.

Maps 21 hand landmarks to high-level gestures used by the virtual mouse:

  Gesture   | Fingers extended       | Extra condition
  --------- | ---------------------- | ---------------
  MOVE      | index only             | —
  LEFT_CLICK| index + middle         | tips distance < threshold
  RIGHT_CLICK| index + pinky         | —
  SCROLL    | index + middle + ring  | —
  NEUTRAL   | (anything else)        | —

Author: Alex Mathieu
"""

from __future__ import annotations

import math
from enum import Enum, auto


class Gesture(Enum):
    NEUTRAL = auto()
    MOVE = auto()
    LEFT_CLICK = auto()
    RIGHT_CLICK = auto()
    SCROLL = auto()


# MediaPipe landmark indices used for finger-state detection
_TIP_IDS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky tips
_PIP_IDS = [3, 6, 10, 14, 18]   # corresponding PIP / IP joints


class GestureEngine:
    """Converts a list of landmark coordinates to a :class:`Gesture`."""

    def __init__(self, click_distance: int = 40) -> None:
        """
        Parameters
        ----------
        click_distance : int
            Maximum pixel distance between two fingertips to register a click.
        """
        self.click_distance = click_distance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_gesture(self, landmarks: list) -> Gesture:
        """
        Classify the current hand posture.

        Parameters
        ----------
        landmarks : list of [id, cx, cy]
            Output of :meth:`HandDetector.find_positions`.

        Returns
        -------
        Gesture
        """
        if not landmarks or len(landmarks) < 21:
            return Gesture.NEUTRAL

        index_up = self._finger_up(landmarks, 8, 6)
        middle_up = self._finger_up(landmarks, 12, 10)
        ring_up = self._finger_up(landmarks, 16, 14)
        pinky_up = self._finger_up(landmarks, 20, 18)

        # MOVE — only index finger extended
        if index_up and not middle_up and not ring_up and not pinky_up:
            return Gesture.MOVE

        # RIGHT_CLICK — index + pinky (devil-horns, unambiguous)
        if index_up and not middle_up and not ring_up and pinky_up:
            return Gesture.RIGHT_CLICK

        # LEFT_CLICK / fine MOVE — index + middle extended
        if index_up and middle_up and not ring_up and not pinky_up:
            dist = self._distance(landmarks[8], landmarks[12])
            if dist < self.click_distance:
                return Gesture.LEFT_CLICK
            return Gesture.MOVE  # two fingers spread = fine cursor control

        # SCROLL — index + middle + ring extended
        if index_up and middle_up and ring_up:
            return Gesture.SCROLL

        return Gesture.NEUTRAL

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _finger_up(landmarks: list, tip_id: int, pip_id: int) -> bool:
        """Return *True* when a finger is extended (tip above PIP in image y)."""
        return landmarks[tip_id][2] < landmarks[pip_id][2]

    @staticmethod
    def _distance(p1: list, p2: list) -> float:
        """Euclidean distance between two [id, cx, cy] landmarks."""
        return math.hypot(p2[1] - p1[1], p2[2] - p1[2])
