"""
hand_detector.py — MediaPipe Hands wrapper.

Wraps the MediaPipe Hands solution and exposes a simple API:
  - find_hands(img)       : detect hand landmarks and optionally draw them
  - find_positions(img)   : return pixel coordinates for each of the 21 landmarks
  - hands_detected()      : quick boolean check

Author: Alex Mathieu
"""

import cv2
import mediapipe as mp


class HandDetector:
    """Detects and tracks a hand using MediaPipe Hands (21 landmarks)."""

    def __init__(
        self,
        max_hands: int = 1,
        detection_conf: float = 0.7,
        tracking_conf: float = 0.7,
    ) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self._mp_draw = mp.solutions.drawing_utils
        self._results = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_hands(self, img, draw: bool = True):
        """
        Run MediaPipe detection on *img* (BGR).

        Parameters
        ----------
        img : numpy.ndarray
            BGR frame from OpenCV.
        draw : bool
            When True, draw the skeleton on *img* in place.

        Returns
        -------
        numpy.ndarray
            The (possibly annotated) frame.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self._results = self._hands.process(img_rgb)

        if self._results.multi_hand_landmarks and draw:
            for hand_lm in self._results.multi_hand_landmarks:
                self._mp_draw.draw_landmarks(
                    img, hand_lm, self._mp_hands.HAND_CONNECTIONS
                )

        return img

    def find_positions(self, img, hand_no: int = 0) -> list:
        """
        Return pixel coordinates for each landmark of *hand_no*.

        Returns
        -------
        list of [id, cx, cy]
            Empty list when no hand is detected.
        """
        landmark_list: list = []

        if not (self._results and self._results.multi_hand_landmarks):
            return landmark_list

        if hand_no >= len(self._results.multi_hand_landmarks):
            return landmark_list

        h, w = img.shape[:2]
        hand = self._results.multi_hand_landmarks[hand_no]

        for idx, lm in enumerate(hand.landmark):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            landmark_list.append([idx, cx, cy])

        return landmark_list

    def hands_detected(self) -> bool:
        """Return *True* when at least one hand was found in the last frame."""
        return bool(self._results and self._results.multi_hand_landmarks)
