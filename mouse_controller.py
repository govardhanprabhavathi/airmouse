import pyautogui
import numpy as np

class MouseController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        pyautogui.FAILSAFE = True
        self.is_dragging = False

    def move(self, x, y):
        try:
            pyautogui.moveTo(x, y)
        except pyautogui.FailSafeException:
            pass

    def click(self):
        pyautogui.click()
        
    def start_drag(self):
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True
            
    def stop_drag(self):
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

    def scroll(self, amount):
        pyautogui.scroll(amount)
        
    def map_to_screen(self, cam_x, cam_y, cam_w, cam_h, roi_margin=100):
        # We use a ROI (Region of Interest) inside the camera view so the user doesn't have to reach the edges of the frame.
        
        # Clamp camera coordinates to ROI
        roi_x = max(roi_margin, min(cam_x, cam_w - roi_margin))
        roi_y = max(roi_margin, min(cam_y, cam_h - roi_margin))
        
        # Interpolate
        screen_x = np.interp(roi_x, (roi_margin, cam_w - roi_margin), (0, self.screen_w))
        screen_y = np.interp(roi_y, (roi_margin, cam_h - roi_margin), (0, self.screen_h))
        
        return int(screen_x), int(screen_y)
