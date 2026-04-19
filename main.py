import cv2
import time
import pyautogui
import numpy as np
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from mouse_controller import MouseController
from utils.smoothing import smooth_coordinates

def main():
    # Setup Camera
    cam_w, cam_h = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Reduces frame buffer to ensure we process the latest frame instead of lagging behind
    cap.set(3, cam_w)
    cap.set(4, cam_h)
    
    # Get Screen Resolution
    screen_w, screen_h = pyautogui.size()
    
    # Initialize Modules
    pyautogui.PAUSE = 0 # Crucial to remove the massive 100ms artificial delay
    tracker = HandTracker(max_hands=1, detection_con=0.7)
    detector = GestureDetector()
    mouse = MouseController(screen_w, screen_h)
    
    # Configuration
    roi_margin = 150 # DPI SENSITIVITY: Higher value = higher DPI. Creates a smaller required movement box so you don't have to stretch to reach corners.
    smoothing_factor = 0.2 # Reduced from 0.8 to 0.2. A lower factor provides heavy stabilization to completely eliminate the raw tracking jitter.
    prev_x, prev_y = None, None
    scroll_prev_y = None
    
    # FPS variables
    pTime = 0
    
    # Gesture Confirmation Delay Variables
    pinch_start_time = 0
    pinch_delay = 0.15 # 150ms delay to distinguish click from drag
    is_pinching = False
    
    print("AirMouse Started. Press 'q' in the camera window to quit.")
    
    while True:
        success, img = cap.read()
        if not success:
            break
            
        # Flip image horizontally for a selfie-view display
        img = cv2.flip(img, 1)
        
        # Draw ROI Rectangle
        cv2.rectangle(img, (roi_margin, roi_margin), (cam_w - roi_margin, cam_h - roi_margin), (255, 0, 255), 2)
            
        img = tracker.find_hands(img)
        landmarks = tracker.get_landmark_positions(img, hand_no=0)
        
        if len(landmarks) != 0:
            gesture = detector.get_active_gesture(landmarks)
            
            # Gesture text logic moved to UI rendering block
            
            # Pointer mode (Move cursor continuously unless making a Fist or Scrolling)
            if gesture != "Fist" and gesture != "Scroll":
                # Get index finger tip coordinates
                x1, y1 = landmarks[detector.INDEX_TIP][1:]
                
                # Convert coordinates to screen space
                screen_x, screen_y = mouse.map_to_screen(x1, y1, cam_w, cam_h, roi_margin)
                
                # Smooth coordinates
                smooth_x, smooth_y = smooth_coordinates(prev_x, prev_y, screen_x, screen_y, smoothing_factor)
                
                # Move mouse
                mouse.move(smooth_x, smooth_y)
                prev_x, prev_y = smooth_x, smooth_y
                scroll_prev_y = None
                
                # Handle Pinch (Click vs Drag)
                if gesture == "Pinch":
                    if not is_pinching:
                        is_pinching = True
                        pinch_start_time = time.time()
                    else:
                        # If pinched for longer than delay, it's a drag
                        if time.time() - pinch_start_time > pinch_delay:
                            mouse.start_drag()
                            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                else:
                    if is_pinching:
                        # Released pinch
                        is_pinching = False
                        if time.time() - pinch_start_time <= pinch_delay:
                            # It was a short pinch -> click
                            mouse.click()
                        else:
                            # It was a long pinch -> stop dragging
                            mouse.stop_drag()
                            
            elif gesture == "Scroll":
                # Extract y-coordinates of index and middle finger tips
                y1 = landmarks[detector.INDEX_TIP][2]
                y2 = landmarks[detector.MIDDLE_TIP][2]
                avg_y = (y1 + y2) / 2
                
                if scroll_prev_y is not None:
                    diff = scroll_prev_y - avg_y
                    if abs(diff) > 2: # Add small deadzone to prevent jittery scrolling
                        mouse.scroll(int(diff * 5)) # Speed multiplier
                scroll_prev_y = avg_y
                
            else: # Fist gesture
                # Pause / Idle
                # Reset previous coordinates to avoid jump when returning to Pointer
                prev_x, prev_y = None, None 
                scroll_prev_y = None
                
        else:
             # Reset previous coordinates when no hands are detected
             prev_x, prev_y = None, None
        
        # Calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if pTime > 0 else 0
        pTime = cTime
        
        # -----------------------------
        # Render Custom UI Layout
        # -----------------------------
        canvas_h, canvas_w = 550, 1000
        bg = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 255
        
        # Draw Title
        title_text = "Air Mouse"
        title_size = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 2, 3)[0]
        title_x = (canvas_w - title_size[0]) // 2
        cv2.putText(bg, title_text, (title_x, 60), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (0, 0, 0), 3)
        
        # Place Camera Feed
        cam_draw_w, cam_draw_h = 426, 320 # Scaled down feed
        img_resized = cv2.resize(img, (cam_draw_w, cam_draw_h))
        cam_x, cam_y = 50, 120
        bg[cam_y:cam_y+cam_draw_h, cam_x:cam_x+cam_draw_w] = img_resized
        
        # Draw Right Side Text
        text_x = cam_x + cam_draw_w + 60
        text_y_start = cam_y + 50
        
        display_gesture = gesture if len(landmarks) != 0 else "None"
        
        # Gesture Name (Green)
        cv2.putText(bg, display_gesture, (text_x, text_y_start), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (50, 205, 50), 4)
        
        # FPS (Orange/Red)
        cv2.putText(bg, f'FPS : {int(fps)}', (text_x, text_y_start + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 80, 255), 4)
        
        # Controls Guide (Black)
        guide_y = text_y_start + 150
        cv2.putText(bg, "Controls Guide:", (text_x, guide_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        
        guide_text = [
            "  * Any Hand : Move Cursor",
            "  * Pinch : Click (Hold to Drag)",
            "  * 2 Fingers : Scroll Up/Down",
            "  * Fist : Pause/Idle Tracking"
        ]
        for i, text in enumerate(guide_text):
            cv2.putText(bg, text, (text_x, guide_y + 40 + (i * 35)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        cv2.imshow("AirMouse", bg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
