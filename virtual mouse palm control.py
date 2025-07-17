import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize webcam
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
mp_draw = mp.solutions.drawing_utils

# Cooldown timer
last_click_time = 0
click_cooldown = 1.0  # seconds

def fingers_up(hand_landmarks):
    """Return a list indicating which fingers are up."""
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    num_palms = 0
    index_pos = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if this hand is a palm (all fingers up)
            fingers = fingers_up(hand_landmarks)
            if sum(fingers) >= 4:  # Treat as palm if 4+ fingers are up
                num_palms += 1

                # Use this hand for movement if it's the first detected palm
                if not index_pos:
                    index_tip = hand_landmarks.landmark[8]
                    index_pos = (
                        int(index_tip.x * screen_width),
                        int(index_tip.y * screen_height)
                    )

    # Move cursor if one palm detected
    if num_palms == 1 and index_pos:
        pyautogui.moveTo(index_pos[0], index_pos[1], duration=0.01)

    # Click if both palms are shown (with cooldown)
    current_time = time.time()
    if num_palms == 2 and (current_time - last_click_time > click_cooldown):
        last_click_time = current_time
        pyautogui.click()
        cv2.putText(frame, "CLICK", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    # Display
    cv2.imshow("Palm-Controlled Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
