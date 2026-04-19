import cv2
import mediapipe as mp
import time

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class HandTracker:
    def __init__(self, mode=False, max_hands=2, detection_con=0.7, track_con=0.5):
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.detection_con,
            min_hand_presence_confidence=self.track_con,
            min_tracking_confidence=self.track_con,
            running_mode=VisionRunningMode.IMAGE
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.results = None
        
        # Connections for manual drawing
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

    def _draw_landmarks(self, frame, hand_landmarks):
        h, w, c = frame.shape
        # Draw points
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), cv2.FILLED)
        # Draw lines
        for connection in self.HAND_CONNECTIONS:
            idx1, idx2 = connection
            p1 = hand_landmarks[idx1]
            p2 = hand_landmarks[idx2]
            cx1, cy1 = int(p1.x * w), int(p1.y * h)
            cx2, cy2 = int(p2.x * w), int(p2.y * h)
            cv2.line(frame, (cx1, cy1), (cx2, cy2), (0, 255, 0), 2)

    def find_hands(self, frame, draw=True):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.results = self.landmarker.detect(mp_image)
        
        if self.results and self.results.hand_landmarks:
            for hand_lms in self.results.hand_landmarks:
                if draw:
                    self._draw_landmarks(frame, hand_lms)
        return frame
        
    def get_landmark_positions(self, frame, hand_no=0):
        lms_list = []
        if self.results and self.results.hand_landmarks:
            if len(self.results.hand_landmarks) > hand_no:
                hand = self.results.hand_landmarks[hand_no]
                h, w, c = frame.shape
                for id, lm in enumerate(hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lms_list.append([id, cx, cy])
        return lms_list
