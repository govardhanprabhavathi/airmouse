import cv2
import time
import pyautogui
import numpy as np
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from mouse_controller import MouseController
from utils.smoothing import smooth_coordinates, OneEuroFilter
import threading
import sys
import ctypes
import multiprocessing
from PIL import Image, ImageDraw, ImageFont

def is_media_playing():
    try:
        from pycaw.pycaw import AudioUtilities
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.State == 1: # AudioSessionStateActive
                return True
    except Exception:
        pass
    return True # Fallback to True if pycaw is not installed/loaded

class ThreadedCamera:
    def __init__(self, src=0, width=640, height=480):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(3, width)
        self.cap.set(4, height)
        
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def start(self):
        if self.started:
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            if grabbed:
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            time.sleep(0.005) # Yield thread briefly to prevent high CPU loop

    def read(self):
        with self.read_lock:
            if self.frame is not None:
                return self.grabbed, self.frame.copy()
            return self.grabbed, None

    def release(self):
        self.started = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        self.cap.release()

def render_ui(bg_cv, camera_feed, active_gesture, last_action, fps):
    # Convert OpenCV BGR to Pillow RGB
    bg_pil = Image.fromarray(cv2.cvtColor(bg_cv, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(bg_pil)
    
    # 1. Background Fill with Warm Cream (#f3eee7)
    draw.rectangle([0, 0, bg_pil.width, bg_pil.height], fill=(243, 238, 231))
    
    # Load fonts
    try:
        font_logo = ImageFont.truetype("segoeuib.ttf", 22)
        font_badge = ImageFont.truetype("segoeuib.ttf", 11)
        font_card_title = ImageFont.truetype("segoeuib.ttf", 13)
        font_card_val = ImageFont.truetype("segoeuib.ttf", 24)
        font_status_val = ImageFont.truetype("segoeuib.ttf", 20)
        font_guide_title = ImageFont.truetype("segoeuib.ttf", 16)
        font_guide = ImageFont.truetype("segoeui.ttf", 15)
    except IOError:
        font_logo = font_badge = font_card_title = font_card_val = font_status_val = font_guide_title = font_guide = ImageFont.load_default()
        
    # Draw header divider line
    draw.line([50, 85, 950, 85], fill=(215, 210, 200), width=1)
    
    # Draw Logo: Black circle with a bold white mouse pointer inside
    draw.ellipse([50, 25, 80, 55], fill=(0, 0, 0))
    pointer_points = [
        (58, 32),  # Tip
        (72, 39),  # Right corner of head
        (67, 42),  # Right inner nook
        (72, 49),  # Bottom-right of stem
        (69, 51),  # Bottom-left of stem
        (65, 44),  # Left inner nook
        (58, 46)   # Bottom-left corner of head
    ]
    draw.polygon(pointer_points, fill=(255, 255, 255))
    
    draw.text((90, 28), "airmouse", font=font_logo, fill=(0, 0, 0))
    
    # Draw Top Right Mode Pill Badge
    draw.rounded_rectangle([800, 28, 950, 52], radius=12, fill=(0, 0, 0))
    draw.text((825, 32), "By Govardhan", font=font_badge, fill=(255, 255, 255))
    
    # 3. Camera Feed Container Card (Left Side)
    # Container height is 290px (105 to 395). Resized cam image is 360x270, pasted centered.
    draw.rounded_rectangle([50, 105, 430, 395], radius=16, outline=(210, 205, 195), width=2, fill=(255, 255, 255))
    
    # Draw resized camera preview frame (4:3 aspect ratio)
    cam_resized = cv2.resize(camera_feed, (360, 270))
    cam_rgb = cv2.cvtColor(cam_resized, cv2.COLOR_BGR2RGB)
    cam_pil = Image.fromarray(cam_rgb)
    bg_pil.paste(cam_pil, (60, 115))
    
    # 4. Status Indicator Grid (Right Side)
    # Card 1: Active Gesture
    c1_x, c1_y = 460, 105
    c1_w, c1_h = 230, 130
    draw.rounded_rectangle([c1_x, c1_y, c1_x + c1_w, c1_y + c1_h], radius=12, fill=(255, 255, 255), outline=(210, 205, 195), width=1)
    draw.text((c1_x + 20, c1_y + 20), "Active Gesture", font=font_card_title, fill=(120, 120, 120))
    draw.text((c1_x + 20, c1_y + 55), active_gesture, font=font_card_val, fill=(0, 0, 0))
    
    # Card 2: Last Action
    c2_x, c2_y = 720, 105
    c2_w, c2_h = 230, 130
    draw.rounded_rectangle([c2_x, c2_y, c2_x + c2_w, c2_y + c2_h], radius=12, fill=(255, 255, 255), outline=(210, 205, 195), width=1)
    draw.text((c2_x + 20, c2_y + 20), "Last Action", font=font_card_title, fill=(120, 120, 120))
    draw.text((c2_x + 20, c2_y + 55), last_action, font=font_card_val, fill=(0, 80, 255) if last_action != "None" else (150, 150, 150))
    
    # Card 3: Tracking Status (Double-wide Card) - Matches the camera's bottom edge (395)
    c3_x, c3_y = 460, 255
    c3_w, c3_h = 490, 140
    draw.rounded_rectangle([c3_x, c3_y, c3_x + c3_w, c3_y + c3_h], radius=12, fill=(0, 0, 0))
    draw.text((c3_x + 20, c3_y + 20), "System Status", font=font_card_title, fill=(160, 160, 160))
    draw.text((c3_x + 20, c3_y + 60), f"Performance: {int(fps)} Hz   |   Tracking: Active", font=font_status_val, fill=(255, 255, 255))
    
    # 5. Bottom Instructions Bar (Full-Width Card)
    # Expanded panel height (425 to 605) to fit 4 rows of bulleted columns
    draw.rounded_rectangle([50, 425, 950, 605], radius=12, fill=(250, 245, 238), outline=(210, 205, 195), width=1)
    
    draw.text((70, 445), "Controls Guide:", font=font_guide_title, fill=(0, 0, 0))
    
    col1_x = 70
    col2_x = 380
    col3_x = 680
    
    # Column 1 (Mouse basics)
    draw.text((col1_x, 485), "• Hand Pointer: Move cursor", font=font_guide, fill=(100, 100, 100))
    draw.text((col1_x, 515), "• Index Pinch: Left Click", font=font_guide, fill=(100, 100, 100))
    draw.text((col1_x, 545), "• Double Pinch: Double Click", font=font_guide, fill=(100, 100, 100))
    draw.text((col1_x, 575), "• Pinch & Hold: Click & Drag", font=font_guide, fill=(100, 100, 100))
    
    # Column 2 (Clicks & Scrolls)
    draw.text((col2_x, 485), "• Two-Finger Scroll: Move hand", font=font_guide, fill=(100, 100, 100))
    draw.text((col2_x, 515), "• Middle Pinch: Right Click", font=font_guide, fill=(100, 100, 100))
    draw.text((col2_x, 545), "• Ring Pinch: Middle Click", font=font_guide, fill=(100, 100, 100))
    draw.text((col2_x, 575), "• Ring Pinch & Hold: Precision", font=font_guide, fill=(100, 100, 100))
    
    # Column 3 (Media controls when active)
    draw.text((col3_x, 485), "• Fist: Play / Pause", font=font_guide, fill=(100, 100, 100))
    draw.text((col3_x, 515), "• Swipe L/R: Prev/Next track", font=font_guide, fill=(100, 100, 100))
    draw.text((col3_x, 545), "• Rotate Hand: Volume up/down", font=font_guide, fill=(100, 100, 100))
    draw.text((col3_x, 575), "• Peace: Screenshot", font=font_guide, fill=(100, 100, 100))
    
    # Convert Pillow RGB back to OpenCV BGR
    return cv2.cvtColor(np.array(bg_pil), cv2.COLOR_RGB2BGR)

def main():
    multiprocessing.freeze_support()
    
    # Setup Threaded Camera Capture
    cam_w, cam_h = 640, 480
    cap = ThreadedCamera(0, cam_w, cam_h).start()
    
    # Get Screen Resolution
    screen_w, screen_h = pyautogui.size()
    
    # Initialize Modules
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False
    tracker = HandTracker(max_hands=1, detection_con=0.7)
    detector = GestureDetector()
    mouse = MouseController(screen_w, screen_h)
    
    # Configuration
    roi_margin_x = 80 # Asymmetric margin for wider tracking bounds
    roi_margin_y = 60 # Asymmetric margin for taller tracking bounds
    
    # Initialize One Euro Filters for X and Y coordinates
    filter_x = None
    filter_y = None
    
    prev_x, prev_y = None, None
    
    # Gesture Confirmation Delay Variables
    pinch_start_time = 0
    pinch_delay = 0.20 # 200ms delay to distinguish click from drag
    is_pinching = False
    drag_started = False
    
    # Double pinch / Right / Middle pinch variables
    last_click_time = 0
    is_pinching_middle = False
    is_pinching_ring = False
    ring_pinch_start_time = 0
    ring_drag_started = False
    
    # Scrolling variables
    is_scrolling = False
    scroll_start_x = 0
    scroll_start_y = 0
    
    # Media and Utility gestures state variables
    is_thumbs_up_active = False
    is_peace_active = False
    peace_start_time = 0
    is_fist_active = False
    fist_start_time = 0
    last_volume_time = 0
    last_swipe_time = 0
    wrist_history = []
    gesture_history = []
    
    # UI display metrics
    last_action_str = "None"
    last_action_display_time = 0
    pTime = 0
    
    print("AirMouse Started. Press 'q' in the camera window to quit.")
    
    canvas_h, canvas_w = 640, 1000
    
    while True:
        success, img = cap.read()
        if not success or img is None:
            time.sleep(0.001)
            continue
            
        # Flip image horizontally for a selfie-view display
        img = cv2.flip(img, 1)
        
        # Draw ROI Rectangle using asymmetric margins on preview
        cv2.rectangle(img, (roi_margin_x, roi_margin_y), (cam_w - roi_margin_x, cam_h - roi_margin_y), (255, 0, 255), 2)
            
        img = tracker.find_hands(img)
        landmarks = tracker.get_landmark_positions(img, hand_no=0)
        
        display_gesture = "None"
        if len(landmarks) != 0:
            raw_gesture = detector.get_active_gesture(landmarks)
            gesture_history.append(raw_gesture)
            gesture_history = gesture_history[-5:]
            
            # Find the most common gesture in the rolling history window
            counts = {}
            for g in gesture_history:
                counts[g] = counts.get(g, 0) + 1
            most_common = max(counts, key=counts.get)
            
            # Require at least 3 out of 5 frames to switch/trigger a gesture
            gesture = most_common if counts[most_common] >= 3 else "Pointer"
            display_gesture = gesture
            
            # Pointer cursor movement (disabled during two-finger scrolling to keep cursor locked)
            if gesture != "None" and gesture != "Two-Finger Pinch":
                x1, y1 = landmarks[detector.INDEX_TIP][1:]
                screen_x, screen_y = mouse.map_to_screen(x1, y1, cam_w, cam_h, roi_margin_x, roi_margin_y)
                
                curr_time = time.time()
                if filter_x is None or filter_y is None:
                    filter_x = OneEuroFilter(curr_time, screen_x, mincutoff=1.0, beta=0.015)
                    filter_y = OneEuroFilter(curr_time, screen_y, mincutoff=1.0, beta=0.015)
                    smooth_x, smooth_y = screen_x, screen_y
                else:
                    smooth_x = filter_x(curr_time, screen_x)
                    smooth_y = filter_y(curr_time, screen_y)
                
                mouse.move(smooth_x, smooth_y)
                prev_x, prev_y = smooth_x, smooth_y
                
            if len(landmarks) > detector.INDEX_TIP:
                x1, y1 = landmarks[detector.INDEX_TIP][1:]
                
                # 1. Index Pinch (Left Click / Drag)
                if gesture == "Pinch":
                    if not is_pinching:
                        is_pinching = True
                        pinch_start_time = time.time()
                        drag_started = False
                    else:
                        if time.time() - pinch_start_time > pinch_delay:
                            if not drag_started:
                                mouse.start_drag()
                                drag_started = True
                                last_action_str = "Drag Start"
                                last_action_display_time = time.time()
                            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                else:
                    if is_pinching:
                        is_pinching = False
                        if drag_started:
                            mouse.stop_drag()
                            drag_started = False
                            last_action_str = "Drag Stop"
                            last_action_display_time = time.time()
                        else:
                            now = time.time()
                            if now - last_click_time < 0.35:
                                mouse.double_click()
                                last_action_str = "Double Click"
                            else:
                                mouse.click()
                                last_action_str = "Left Click"
                            last_click_time = now
                            last_action_display_time = time.time()
                            
                # 2. Middle Pinch (Right Click)
                if gesture == "Pinch Middle":
                    if not is_pinching_middle:
                        mouse.right_click()
                        last_action_str = "Right Click"
                        last_action_display_time = time.time()
                        is_pinching_middle = True
                else:
                    is_pinching_middle = False
                    
                # 3. Ring Pinch (Middle Click / Precision Scroll)
                if gesture == "Pinch Ring":
                    if not is_pinching_ring:
                        is_pinching_ring = True
                        ring_pinch_start_time = time.time()
                        ring_drag_started = False
                    else:
                        if time.time() - ring_pinch_start_time > pinch_delay:
                            if not ring_drag_started:
                                mouse.start_middle_drag()
                                ring_drag_started = True
                                last_action_str = "Precision Scroll Start"
                                last_action_display_time = time.time()
                            cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                else:
                    if is_pinching_ring:
                        is_pinching_ring = False
                        if ring_drag_started:
                            mouse.stop_middle_drag()
                            ring_drag_started = False
                            last_action_str = "Precision Scroll Stop"
                            last_action_display_time = time.time()
                        else:
                            mouse.middle_click()
                            last_action_str = "Middle Click"
                            last_action_display_time = time.time()
                            
                # 4. Two-Finger Pinch (Touchpad Scroll)
                if gesture == "Two-Finger Pinch":
                    if not is_scrolling:
                        is_scrolling = True
                        scroll_start_x, scroll_start_y = x1, y1
                    else:
                        dx = x1 - scroll_start_x
                        dy = y1 - scroll_start_y
                        scroll_factor = 0.5
                        
                        # Vertical scroll
                        if abs(dy) > 5:
                            mouse.scroll(-dy * scroll_factor)
                        # Horizontal scroll
                        if abs(dx) > 5:
                            mouse.scroll_horizontal(dx * scroll_factor)
                            
                        scroll_start_x, scroll_start_y = x1, y1
                        last_action_str = "Scroll"
                        last_action_display_time = time.time()
                else:
                    is_scrolling = False

                # 5. Fist (Play / Pause media - 0.2s hold)
                if gesture == "Fist":
                    if fist_start_time == 0:
                        fist_start_time = time.time()
                    if time.time() - fist_start_time >= 0.2:
                        if not is_fist_active:
                            pyautogui.press('playpause')
                            last_action_str = "Play / Pause"
                            last_action_display_time = time.time()
                            is_fist_active = True
                else:
                    is_fist_active = False
                    fist_start_time = 0

                # 6. Peace Sign (Screenshot - 2 Second Hold)
                if gesture == "Peace Sign":
                    if peace_start_time == 0:
                        peace_start_time = time.time()
                    
                    elapsed = time.time() - peace_start_time
                    if elapsed >= 2.0:
                        if not is_peace_active:
                            is_peace_active = True
                            try:
                                # 1. Native Windows Screenshot (flashes screen and saves to Pictures/Screenshots)
                                if sys.platform == 'win32':
                                    pyautogui.hotkey('win', 'printscreen')
                                
                                # 2. Local PIL backup saved to Pictures/Screenshots or Pictures
                                import os
                                user_profile = os.environ.get("USERPROFILE")
                                save_dir = None
                                if user_profile:
                                    p1 = os.path.join(user_profile, "Pictures", "Screenshots")
                                    p2 = os.path.join(user_profile, "Pictures")
                                    if os.path.exists(p1):
                                        save_dir = p1
                                    elif os.path.exists(p2):
                                        save_dir = p2
                                        
                                if not save_dir:
                                    save_dir = "screenshots"
                                    
                                os.makedirs(save_dir, exist_ok=True)
                                fn = os.path.join(save_dir, f"screenshot_{int(time.time())}.png")
                                
                                screenshot = pyautogui.screenshot()
                                screenshot.save(fn)
                                last_action_str = "Screenshot Saved"
                            except Exception:
                                try:
                                    screenshot = pyautogui.screenshot()
                                    os.makedirs("screenshots", exist_ok=True)
                                    screenshot.save(f"screenshots/screenshot_{int(time.time())}.png")
                                    last_action_str = "Screenshot Saved"
                                except Exception:
                                    last_action_str = "Screenshot Error"
                            last_action_display_time = time.time()
                        display_gesture = "Screenshot!"
                    else:
                        remaining = 2.0 - elapsed
                        display_gesture = f"Peace ({remaining:.1f}s)"
                else:
                    is_peace_active = False
                    peace_start_time = 0

                # 8. Wrist Rotation (Volume) & Swipes (Media track control) - Enabled when media is playing
                if is_media_playing():
                    # Wrist Rotation Volume Control
                    angle = detector.get_wrist_angle(landmarks)
                    if angle > 30: # Clockwise
                        if time.time() - last_volume_time > 0.15:
                            pyautogui.press('volumeup')
                            last_action_str = "Volume Up"
                            last_action_display_time = time.time()
                            last_volume_time = time.time()
                    elif angle < -30: # Anti-clockwise
                        if time.time() - last_volume_time > 0.15:
                            pyautogui.press('volumedown')
                            last_action_str = "Volume Down"
                            last_action_display_time = time.time()
                            last_volume_time = time.time()

                    # Swipes tracking
                    # Append wrist position
                    wrist_history.append((time.time(), landmarks[0][1], landmarks[0][2]))
                    # Keep history for max 0.3s
                    wrist_history = [p for p in wrist_history if time.time() - p[0] < 0.3]
                    
                    if len(wrist_history) >= 5:
                        dt = wrist_history[-1][0] - wrist_history[0][0]
                        dx = wrist_history[-1][1] - wrist_history[0][1]
                        dy = wrist_history[-1][2] - wrist_history[0][2]
                        
                        if dt > 0.05 and time.time() - last_swipe_time > 1.0:
                            vx = dx / dt
                            # Large horizontal movement, small vertical movement
                            if abs(dx) > 100 and abs(dx) > 1.5 * abs(dy) and abs(vx) > 800:
                                if vx > 800: # Swipe Right (Next Track)
                                    pyautogui.press('nexttrack')
                                    last_action_str = "Next Track"
                                    last_action_display_time = time.time()
                                    last_swipe_time = time.time()
                                elif vx < -800: # Swipe Left (Prev Track)
                                    pyautogui.press('prevtrack')
                                    last_action_str = "Prev Track"
                                    last_action_display_time = time.time()
                                    last_swipe_time = time.time()
        else:
             prev_x, prev_y = None, None
             filter_x, filter_y = None, None
             wrist_history = []
             gesture_history.clear()
             
             if is_pinching:
                 is_pinching = False
                 mouse.stop_drag()
             if is_pinching_ring:
                 is_pinching_ring = False
                 mouse.stop_middle_drag()
             is_scrolling = False
             is_thumbs_up_active = False
             is_peace_active = False
             peace_start_time = 0
             is_fist_active = False
             fist_start_time = 0

        # Action display timeout helper
        if time.time() - last_action_display_time > 2.0:
            last_action_str = "None"
            
        # Calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if pTime > 0 else 0
        pTime = cTime
        
        # Render the custom Minimalist UI Canvas
        base_canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        rendered_frame = render_ui(
            base_canvas, 
            img, 
            display_gesture, 
            last_action_str, 
            fps
        )
        
        cv2.imshow("AirMouse", rendered_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        # Check if the user closed the window by clicking the 'X' close button
        try:
            if cv2.getWindowProperty("AirMouse", cv2.WND_PROP_VISIBLE) < 1:
                break
        except Exception:
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
