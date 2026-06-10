import pyautogui
import numpy as np
import sys
import ctypes

class MouseController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        pyautogui.FAILSAFE = True
        self.is_dragging = False
        self.is_windows = sys.platform == 'win32'

    def move(self, x, y):
        if self.is_windows:
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
        else:
            try:
                pyautogui.moveTo(x, y)
            except pyautogui.FailSafeException:
                pass

    def click(self):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0) # MOUSEEVENTF_LEFTDOWN
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # MOUSEEVENTF_LEFTUP
        else:
            pyautogui.click()
            
    def right_click(self):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0) # MOUSEEVENTF_RIGHTDOWN
            ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0) # MOUSEEVENTF_RIGHTUP
        else:
            pyautogui.rightClick()
            
    def middle_click(self):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x0020, 0, 0, 0, 0) # MOUSEEVENTF_MIDDLEDOWN
            ctypes.windll.user32.mouse_event(0x0040, 0, 0, 0, 0) # MOUSEEVENTF_MIDDLEUP
        else:
            pyautogui.middleClick()

    def double_click(self):
        if self.is_windows:
            self.click()
            import time
            time.sleep(0.05)
            self.click()
        else:
            pyautogui.doubleClick()
        
    def start_drag(self):
        if not self.is_dragging:
            if self.is_windows:
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0) # MOUSEEVENTF_LEFTDOWN
            else:
                pyautogui.mouseDown()
            self.is_dragging = True
            
    def stop_drag(self):
        if self.is_dragging:
            if self.is_windows:
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # MOUSEEVENTF_LEFTUP
            else:
                pyautogui.mouseUp()
            self.is_dragging = False
            
    def start_middle_drag(self):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x0020, 0, 0, 0, 0) # MOUSEEVENTF_MIDDLEDOWN
        else:
            pyautogui.mouseDown(button='middle')

    def stop_middle_drag(self):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x0040, 0, 0, 0, 0) # MOUSEEVENTF_MIDDLEUP
        else:
            pyautogui.mouseUp(button='middle')

    def scroll(self, amount):
        if self.is_windows:
            # Multiplier for scrolling. Standard is 120 per click, but we scale it as appropriate.
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, int(amount * 24), 0) # MOUSEEVENTF_WHEEL
        else:
            pyautogui.scroll(amount)
            
    def scroll_horizontal(self, amount):
        if self.is_windows:
            ctypes.windll.user32.mouse_event(0x1000, 0, 0, int(amount * 24), 0) # MOUSEEVENTF_HWHEEL
        else:
            try:
                pyautogui.hscroll(amount)
            except AttributeError:
                pass
        
    def map_to_screen(self, cam_x, cam_y, cam_w, cam_h, roi_margin_x=80, roi_margin_y=60):
        # We use a ROI (Region of Interest) inside the camera view so the user doesn't have to reach the edges of the frame.
        
        # Clamp camera coordinates to ROI
        roi_x = max(roi_margin_x, min(cam_x, cam_w - roi_margin_x))
        roi_y = max(roi_margin_y, min(cam_y, cam_h - roi_margin_y))
        
        # Interpolate
        screen_x = np.interp(roi_x, (roi_margin_x, cam_w - roi_margin_x), (0, self.screen_w))
        screen_y = np.interp(roi_y, (roi_margin_y, cam_h - roi_margin_y), (0, self.screen_h))
        
        return int(screen_x), int(screen_y)

