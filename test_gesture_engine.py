"""
test_gesture_engine.py — Unit tests for GestureEngine.

These tests exercise the gesture classification logic without requiring
a webcam, MediaPipe, or a display.

Run with:
    python -m pytest test_gesture_engine.py -v
"""

import pytest
from gesture_engine import Gesture, GestureEngine


# ---------------------------------------------------------------------------
# Helpers — build fake landmark lists
# ---------------------------------------------------------------------------

def _make_landmarks(
    index_up: bool = False,
    middle_up: bool = False,
    ring_up: bool = False,
    pinky_up: bool = False,
    index_middle_dist: int = 80,
) -> list:
    """
    Build a minimal 21-landmark list where only the relevant landmarks are
    set to values that make _finger_up() / _distance() return the desired result.

    Layout (only geometry-sensitive landmarks need sensible values):
      - Wrist at (320, 400)
      - PIP joints fixed at y=300 (pixel row 300)
      - Tip y < 300  ↔  finger UP   (because image y increases downward)
      - Tip y > 300  ↔  finger DOWN

    For index-middle distance: tips placed at known x positions so that
    hypot(dx, dy) equals index_middle_dist.
    """
    BASE_Y = 400
    PIP_Y  = 300
    UP_Y   = 200   # tip above PIP
    DOWN_Y = 380   # tip below PIP (finger curled)

    # Initialise all 21 landmarks with a neutral position
    lm = [[i, 320, BASE_Y] for i in range(21)]

    # Wrist
    lm[0] = [0, 320, 400]

    # PIP joints (joints we compare against)
    lm[6]  = [6,  320, PIP_Y]   # index PIP
    lm[10] = [10, 320, PIP_Y]   # middle PIP
    lm[14] = [14, 320, PIP_Y]   # ring PIP
    lm[18] = [18, 320, PIP_Y]   # pinky PIP

    # Finger tips
    lm[8]  = [8,  320, UP_Y if index_up  else DOWN_Y]
    lm[12] = [12, 320, UP_Y if middle_up else DOWN_Y]
    lm[16] = [16, 320, UP_Y if ring_up   else DOWN_Y]
    lm[20] = [20, 320, UP_Y if pinky_up  else DOWN_Y]

    # Adjust index-middle x-positions so that their distance equals
    # `index_middle_dist` (only relevant when both fingers are up).
    half = index_middle_dist // 2
    lm[8][1]  = 320 - half
    lm[12][1] = 320 + half

    return lm


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGestureEngine:

    def setup_method(self):
        self.engine = GestureEngine(click_distance=40)

    # ── Empty / incomplete input ─────────────────────────────────────

    def test_neutral_on_empty_landmarks(self):
        assert self.engine.get_gesture([]) == Gesture.NEUTRAL

    def test_neutral_on_partial_landmarks(self):
        # Fewer than 21 landmarks must not raise and must return NEUTRAL
        partial = [[i, 100, 100] for i in range(10)]
        assert self.engine.get_gesture(partial) == Gesture.NEUTRAL

    # ── MOVE gesture ────────────────────────────────────────────────

    def test_move_only_index_up(self):
        lm = _make_landmarks(index_up=True)
        assert self.engine.get_gesture(lm) == Gesture.MOVE

    # ── LEFT_CLICK gesture ──────────────────────────────────────────

    def test_left_click_when_tips_close(self):
        # index + middle up, tips 20px apart (< threshold 40)
        lm = _make_landmarks(index_up=True, middle_up=True, index_middle_dist=20)
        assert self.engine.get_gesture(lm) == Gesture.LEFT_CLICK

    def test_move_when_index_middle_up_but_far(self):
        # index + middle up, tips 100px apart (> threshold 40)
        lm = _make_landmarks(index_up=True, middle_up=True, index_middle_dist=100)
        assert self.engine.get_gesture(lm) == Gesture.MOVE

    # ── RIGHT_CLICK gesture ─────────────────────────────────────────

    def test_right_click_index_and_pinky(self):
        lm = _make_landmarks(index_up=True, pinky_up=True)
        assert self.engine.get_gesture(lm) == Gesture.RIGHT_CLICK

    # ── SCROLL gesture ──────────────────────────────────────────────

    def test_scroll_three_fingers(self):
        lm = _make_landmarks(index_up=True, middle_up=True, ring_up=True)
        assert self.engine.get_gesture(lm) == Gesture.SCROLL

    def test_scroll_four_fingers(self):
        lm = _make_landmarks(
            index_up=True, middle_up=True, ring_up=True, pinky_up=True
        )
        assert self.engine.get_gesture(lm) == Gesture.SCROLL

    # ── NEUTRAL gesture ─────────────────────────────────────────────

    def test_neutral_all_fingers_down(self):
        lm = _make_landmarks()
        assert self.engine.get_gesture(lm) == Gesture.NEUTRAL

    def test_neutral_only_ring_up(self):
        lm = _make_landmarks(ring_up=True)
        assert self.engine.get_gesture(lm) == Gesture.NEUTRAL

    def test_neutral_only_pinky_up(self):
        lm = _make_landmarks(pinky_up=True)
        assert self.engine.get_gesture(lm) == Gesture.NEUTRAL

    # ── _distance helper ────────────────────────────────────────────

    def test_distance_zero(self):
        p = [0, 100, 200]
        assert GestureEngine._distance(p, p) == pytest.approx(0.0)

    def test_distance_known_value(self):
        p1 = [0, 0, 0]
        p2 = [1, 30, 40]
        assert GestureEngine._distance(p1, p2) == pytest.approx(50.0)

    # ── click_distance boundary ─────────────────────────────────────

    def test_click_at_exact_threshold_minus_one(self):
        engine = GestureEngine(click_distance=50)
        lm = _make_landmarks(index_up=True, middle_up=True, index_middle_dist=49)
        assert engine.get_gesture(lm) == Gesture.LEFT_CLICK

    def test_no_click_at_exact_threshold(self):
        engine = GestureEngine(click_distance=50)
        lm = _make_landmarks(index_up=True, middle_up=True, index_middle_dist=50)
        # Distance equals threshold, NOT less than — should be MOVE
        assert engine.get_gesture(lm) == Gesture.MOVE
