# =============================================================================
# Projet  : Souris Virtuelle
# Auteur  : Alex Mathieu
# Fichier : virtual_mouse.py — Moteur de contrôle gestuel & métriques de session
# =============================================================================

import cv2
import numpy as np
import time
import pyautogui
from functions.HandTrackingModuleVM import HandDetector

class VirtualMouseMetrics:
    def __init__(self):
        self.clicks = 0
        self.right_clicks = 0
        self.scrolls = 0
        self.average_fps = 0
        self.hand_detection_times = []
        self.last_action_time = time.time()
        self.action_cooldown = 0.5  # Temps de refroidissement entre les actions en secondes

    def log_click(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.action_cooldown:
            self.clicks += 1
            self.last_action_time = current_time

    def log_right_click(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.action_cooldown:
            self.right_clicks += 1
            self.last_action_time = current_time

    def log_scroll(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.action_cooldown:
            self.scrolls += 1
            self.last_action_time = current_time

    def log_fps(self, fps):
        self.average_fps = (self.average_fps + fps) / 2 if self.average_fps else fps

    def log_hand_detection_time(self, detection_time):
        self.hand_detection_times.append(detection_time)

    def get_metrics(self):
        return {
            'clicks': self.clicks,
            'right_clicks': self.right_clicks,
            'scrolls': self.scrolls,
            'average_fps': self.average_fps,
            'average_hand_detection_time': np.mean(self.hand_detection_times) if self.hand_detection_times else 0,
            'uptime': sum(self.hand_detection_times),
        }

def virtual_mouse(num_cam, width_cam, height_cam, fps=True):
    wCam, hCam = width_cam, height_cam
    frameR = 80
    smoothening = 3
    pyautogui.FAILSAFE = False

    cap = cv2.VideoCapture(num_cam)
    cap.set(3, wCam)
    cap.set(4, hCam)
    wScreen, hScreen = pyautogui.size()

    detector = HandDetector(maxHands=1)
    pTime = time.time()
    plocX, plocY = 0, 0
    currX, currY = 0, 0

    metrics = VirtualMouseMetrics()

    while True:
        start_time = time.time()
        success, img = cap.read()
        img = cv2.flip(img, 1)

        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]  # Index finger tip
            x2, y2 = lmList[12][1:]  # Middle finger tip
            x4, y4 = lmList[4][1:]  # Thumb tip
            x5, y5 = lmList[20][1:]  # Pinky tip

            fingers = detector.fingersUp()
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (40, 250, 0), 2)

            # Mouse movement (index finger)
            if fingers[1] == 1 and fingers[2] == 0:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScreen))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScreen))

                currX = plocX + (x3 - plocX) / smoothening
                currY = plocY + (y3 - plocY) / smoothening

                pyautogui.moveTo(currX, currY)
                cv2.circle(img, (x1, y1), 9, (0, 0, 255), cv2.FILLED)
                plocX, plocY = currX, currY

            # Left click (index and middle fingers close)
            if fingers[1] == 1 and fingers[2] == 1:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 40:  # Ajusté pour une meilleure détection
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 9, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
                    metrics.log_click()

            # Right click (index and pinky fingers up)
            if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0 and fingers[3] == 0:
                cv2.circle(img, (x5, y5), 9, (0, 255, 0), cv2.FILLED)
                pyautogui.rightClick()
                metrics.log_right_click()

            # Scroll (thumb and index finger distance)
            if fingers[0] == 1 and fingers[1] == 1:
                length, img, lineInfo = detector.findDistance(4, 8, img)
                if length < 20:
                    pyautogui.scroll(-50)
                    metrics.log_scroll()
                elif 20 < length < 40:
                    pyautogui.scroll(50)
                    metrics.log_scroll()

        end_time = time.time()
        metrics.log_hand_detection_time(end_time - start_time)

        if fps:
            current_fps = 1 / (end_time - pTime) if (end_time - pTime) > 0 else 1
            img, pTime = detector.fps(img, pTime, displayFPS=True)
            metrics.log_fps(current_fps)
        else:
            img, pTime = detector.fps(img, pTime, displayFPS=False)

        cv2.imshow("Virtual Mouse (press space to exit)", img)
        if cv2.waitKey(1) == 32:
            cap.release()
            cv2.destroyAllWindows()
            break

    return metrics.get_metrics()