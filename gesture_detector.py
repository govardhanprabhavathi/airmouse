import math

class GestureDetector:
    def __init__(self):
        # Indices for landmarks
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20
        self.WRIST = 0
        
    def _get_distance(self, p1, p2):
        return math.hypot(p2[1] - p1[1], p2[2] - p1[2])

    def is_pinch(self, landmarks, threshold=30):
        if len(landmarks) == 0:
            return False
            
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        
        distance = self._get_distance(thumb_tip, index_tip)
        return distance < threshold

    def is_fist(self, landmarks, threshold=60):
        if len(landmarks) == 0:
            return False
        
        # Check distance between fingertips and wrist
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        wrist = landmarks[self.WRIST]
        
        d1 = self._get_distance(index_tip, wrist)
        d2 = self._get_distance(middle_tip, wrist)
        
        return d1 < threshold and d2 < threshold

    def is_open_palm(self, landmarks, threshold=150):
        if len(landmarks) == 0:
            return False
            
        index_tip = landmarks[self.INDEX_TIP]
        pinky_tip = landmarks[self.PINKY_TIP]
        wrist = landmarks[self.WRIST]
        
        # Fingers spread out and far from wrist
        d1 = self._get_distance(index_tip, wrist)
        d2 = self._get_distance(pinky_tip, wrist)
        d3 = self._get_distance(index_tip, pinky_tip) # Spread
        
        return d1 > threshold and d2 > threshold and d3 > (threshold * 0.7)

    def is_scroll(self, landmarks):
        if len(landmarks) == 0:
            return False
            
        # Check if Index and Middle are UP
        index_tip = landmarks[self.INDEX_TIP]
        index_pip = landmarks[self.INDEX_TIP - 2]
        middle_tip = landmarks[self.MIDDLE_TIP]
        middle_pip = landmarks[self.MIDDLE_TIP - 2]
        
        # Check if Ring and Pinky are DOWN
        ring_tip = landmarks[self.RING_TIP]
        ring_pip = landmarks[self.RING_TIP - 2]
        pinky_tip = landmarks[self.PINKY_TIP]
        pinky_pip = landmarks[self.PINKY_TIP - 2]
        
        # y increases downwards: tip[2] < pip[2] means finger is UP
        index_up = index_tip[2] < index_pip[2]
        middle_up = middle_tip[2] < middle_pip[2]
        
        ring_down = ring_tip[2] > ring_pip[2]
        pinky_down = pinky_tip[2] > pinky_pip[2]
        
        return index_up and middle_up and ring_down and pinky_down

    def get_active_gesture(self, landmarks):
        if len(landmarks) == 0:
            return "None"
            
        if self.is_fist(landmarks):
            return "Fist"
        elif self.is_scroll(landmarks):
            return "Scroll"
        elif self.is_pinch(landmarks):
            return "Pinch"
        elif self.is_open_palm(landmarks):
            return "Open Palm"
            
        return "Pointer" # Default state
