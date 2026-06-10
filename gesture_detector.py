import math

class GestureDetector:
    def __init__(self):
        # Indices for landmarks
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.WRIST = 0
        
    def _get_distance(self, p1, p2):
        return math.hypot(p2[1] - p1[1], p2[2] - p1[2])

    def get_palm_length(self, landmarks):
        if len(landmarks) == 0:
            return 1.0
        # Distance between WRIST (0) and MIDDLE_MCP (9)
        return max(self._get_distance(landmarks[self.WRIST], landmarks[9]), 1.0)

    def is_pinch_index(self, landmarks, threshold_ratio=0.25):
        if len(landmarks) == 0:
            return False
        distance = self._get_distance(landmarks[self.THUMB_TIP], landmarks[self.INDEX_TIP])
        palm_len = self.get_palm_length(landmarks)
        return (distance / palm_len) < threshold_ratio

    def is_pinch_middle(self, landmarks, threshold_ratio=0.25):
        if len(landmarks) == 0:
            return False
        distance = self._get_distance(landmarks[self.THUMB_TIP], landmarks[self.MIDDLE_TIP])
        palm_len = self.get_palm_length(landmarks)
        return (distance / palm_len) < threshold_ratio

    def is_pinch_ring(self, landmarks, threshold_ratio=0.25):
        if len(landmarks) == 0:
            return False
        distance = self._get_distance(landmarks[self.THUMB_TIP], landmarks[self.RING_TIP])
        palm_len = self.get_palm_length(landmarks)
        return (distance / palm_len) < threshold_ratio

    def is_thumbs_up(self, landmarks):
        if len(landmarks) == 0:
            return False
        folded = (landmarks[8][2] > landmarks[6][2] and
                  landmarks[12][2] > landmarks[10][2] and
                  landmarks[16][2] > landmarks[14][2] and
                  landmarks[20][2] > landmarks[18][2])
        thumb_up = (landmarks[4][2] < landmarks[3][2] and
                    landmarks[4][2] < landmarks[2][2])
        thumb_high = landmarks[4][2] < landmarks[5][2]
        return folded and thumb_up and thumb_high

    def is_peace_sign(self, landmarks):
        if len(landmarks) == 0:
            return False
        index_extended = landmarks[8][2] < landmarks[6][2]
        middle_extended = landmarks[12][2] < landmarks[10][2]
        ring_folded = landmarks[16][2] > landmarks[14][2]
        pinky_folded = landmarks[20][2] > landmarks[18][2]
        palm_len = self.get_palm_length(landmarks)
        dist = self._get_distance(landmarks[8], landmarks[12])
        wide = (dist / palm_len) > 0.4
        return index_extended and middle_extended and ring_folded and pinky_folded and wide

    def is_fist(self, landmarks):
        if len(landmarks) == 0:
            return False
        folded = (landmarks[8][2] > landmarks[6][2] and
                  landmarks[12][2] > landmarks[10][2] and
                  landmarks[16][2] > landmarks[14][2] and
                  landmarks[20][2] > landmarks[18][2])
        palm_len = self.get_palm_length(landmarks)
        thumb_folded = self._get_distance(landmarks[4], landmarks[5]) < 0.6 * palm_len
        return folded and thumb_folded

    def get_wrist_angle(self, landmarks):
        if len(landmarks) == 0:
            return 0.0
        dx = landmarks[9][1] - landmarks[0][1]
        dy = landmarks[9][2] - landmarks[0][2]
        angle = math.degrees(math.atan2(dx, -dy))
        return angle

    def get_active_gesture(self, landmarks):
        if len(landmarks) == 0:
            return "None"
            
        if self.is_peace_sign(landmarks):
            return "Peace Sign"
        elif self.is_fist(landmarks):
            return "Fist"
            
        is_index = self.is_pinch_index(landmarks)
        is_middle = self.is_pinch_middle(landmarks)
        is_ring = self.is_pinch_ring(landmarks)
        
        if is_index and is_middle:
            return "Two-Finger Pinch"
        elif is_index:
            return "Pinch"
        elif is_middle:
            return "Pinch Middle"
        elif is_ring:
            return "Pinch Ring"
            
        return "Pointer" # Default state
