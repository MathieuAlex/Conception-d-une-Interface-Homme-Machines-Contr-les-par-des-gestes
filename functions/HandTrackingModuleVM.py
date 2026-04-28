# =============================================================================
# Projet  : Souris Virtuelle
# Auteur  : Alex Mathieu
# Fichier : HandTrackingModuleVM.py — Module de détection des mains (MediaPipe)
# =============================================================================

import math
import cv2 
import mediapipe as mp 
import time 


class HandDetector():
    def __init__(self, mode=False, maxHands=2, detectConf=0.5, trackConf=0.5):
        self.mode = mode 
        self.maxHands = maxHands
        self.detectConf = detectConf
        self.trackConf = trackConf
            
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectConf,
                                        min_tracking_confidence=self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
    
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        results = self.results
        
        # Check if the cam detect a hand
        if results.multi_hand_landmarks:
            # for hand landmark in results
            for handLms in results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)    
        return img
    
    def findPosition(self, img, handNum=0, draw=True):
        xList = []
        yList = []
        bbox = []
        # landmark list
        self.lmList = []
        lmList = self.lmList
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNum]
            for id, lm in enumerate(myHand.landmark):
                # height, width, chanels
                h, w, c = img.shape
                # center x & y
                cx, cy = int(lm.x*w), int(lm.y*h)
                xList.append(cx)
                yList.append(cy)
                lmList.append([id, cx, cy])
                if draw:
                    # custom RGB, size etc
                    cv2.circle(img, (cx, cy), 6, (50, 50, 240), cv2.FILLED)
                    
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), 
                              (0, 255, 0), 2)
                    
        return lmList, bbox
    
    def fingersUp(self):
        fingers = []
        tipIds = self.tipIds
        lmList = self.lmList
        
        # Thumb
        if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else: 
                fingers.append(0)
        return fingers
    
    def findDistance(self, p1, p2, img, draw=True, r=12, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw: 
            cv2.line(img, (x1, y1), (x2, y2), (50, 50, 50), t)
            cv2.circle(img, (x1, y1), r, (50, 50, 50), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (50, 50, 50), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (50, 50, 50), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
    
    def fps(self, img, pTime, displayFPS=True):
        if displayFPS:
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, f'{int(fps)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 210, 0), 3)
        return img, pTime
    