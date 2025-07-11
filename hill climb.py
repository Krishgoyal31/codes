import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller
import time

# --- Setup ---
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # Detect only one hand for simpler control
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# Initialize keyboard controller
keyboard = Controller()

# Webcam setup
cap = cv2.VideoCapture(0)  # 0 for default webcam

if not cap.isOpened():
    print("Error: Could not open webcam. Please ensure it's connected and not in use.")
    exit()

# Get frame dimensions for display
SCREEN_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
SCREEN_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# --- Gesture Detection Parameters (Adjust these for best performance) ---

# Finger extension/curl threshold (normalized Y-coordinate difference)
# This determines if a finger is considered extended or curled
FINGER_EXTENDED_THRESHOLD = 0.05  # Y-tip < Y-mcp - threshold for extended
FINGER_CURLED_THRESHOLD = 0.03  # Y-tip > Y-mcp + threshold for curled

# Cooldown to prevent rapid key toggling (e.g., from slight hand jitters)
ACTION_COOLDOWN = 0.1  # seconds to wait before changing action

# --- State Variables ---
current_action = "Neutral"
last_action_time = time.time()


# --- Helper Functions for Hand State ---

def is_finger_extended(landmark_list, tip_id, mcp_id, threshold=FINGER_EXTENDED_THRESHOLD):
    """Checks if a finger is extended based on tip and MCP joint Y-coordinates."""
    tip_y = landmark_list.landmark[tip_id].y
    mcp_y = landmark_list.landmark[mcp_id].y
    # Y-coordinates increase downwards, so tip_y should be less than mcp_y for extended finger
    return tip_y < mcp_y - threshold


def is_finger_curled(landmark_list, tip_id, mcp_id, threshold=FINGER_CURLED_THRESHOLD):
    """Checks if a finger is curled based on tip and MCP joint Y-coordinates."""
    tip_y = landmark_list.landmark[tip_id].y
    mcp_y = landmark_list.landmark[mcp_id].y
    # Y-coordinates increase downwards, so tip_y should be greater than mcp_y for curled finger
    return tip_y > mcp_y + threshold


def is_hand_open(landmark_list):
    """Checks if the hand is generally open (most fingers extended)."""
    # Check index, middle, ring, pinky fingers
    extended_fingers = 0
    if is_finger_extended(landmark_list, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                          mp_hands.HandLandmark.INDEX_FINGER_MCP):
        extended_fingers += 1
    if is_finger_extended(landmark_list, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                          mp_hands.HandLandmark.MIDDLE_FINGER_MCP):
        extended_fingers += 1
    if is_finger_extended(landmark_list, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP):
        extended_fingers += 1
    if is_finger_extended(landmark_list, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP):
        extended_fingers += 1

    # Consider hand open if at least 3 fingers are extended (excluding thumb for simplicity)
    return extended_fingers >= 3


def is_hand_closed(landmark_list):
    """Checks if the hand is generally closed (most fingers curled)."""
    curled_fingers = 0
    if is_finger_curled(landmark_list, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP):
        curled_fingers += 1
    if is_finger_curled(landmark_list, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        mp_hands.HandLandmark.MIDDLE_FINGER_MCP):
        curled_fingers += 1
    if is_finger_curled(landmark_list, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP):
        curled_fingers += 1
    if is_finger_curled(landmark_list, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP):
        curled_fingers += 1

    # Consider hand closed if at least 3 fingers are curled
    return curled_fingers >= 3


# --- Main Loop ---
print("Starting hand gesture control for Hill Climb Racing...")
print("Make sure the Hill Climb Racing game window is active.")
print("\n--- Hand Controls ---")
print("  - Accelerate: Keep your hand OPEN (fingers extended).")
print("  - Brake/Reverse: Make a CLOSED FIST.")
print("\nPress 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip the frame horizontally for a mirror effect (optional, but good for user)
    frame = cv2.flip(frame, 1)
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    new_action = "Neutral"
    key_to_press = None

    # Text color for display (B, G, R)
    text_color = (0, 255, 0)  # Green for neutral/info
    active_action_color = (255, 0, 0)  # Red for active action

    # --- Draw Visual Guides ---
    # No specific lines needed for open/close, but we can draw a circle around the hand
    # if a hand is detected, to show it's being tracked.
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),  # Red dots
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)  # Green lines
            )
            # Draw a circle around the wrist to indicate tracking
            wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            cx, cy = int(wrist_landmark.x * SCREEN_WIDTH), int(wrist_landmark.y * SCREEN_HEIGHT)
            cv2.circle(frame, (cx, cy), 20, (255, 0, 255), 2)  # Magenta circle

            # --- Action Detection Logic ---
            is_open = is_hand_open(hand_landmarks)
            is_closed = is_hand_closed(hand_landmarks)

            if is_open:
                new_action = "Accelerate"
                key_to_press = Key.right  # Or 'd' if your emulator uses that
            elif is_closed:
                new_action = "Brake/Reverse"
                key_to_press = Key.left  # Or 'a' if your emulator uses that
            # If neither open nor closed, it remains Neutral

    # --- Key Press Logic with Cooldown ---
    current_time = time.time()

    # Only change action if it's different AND cooldown has passed
    if new_action != current_action and (current_time - last_action_time > ACTION_COOLDOWN):
        # Release the previous key if it was being held
        if current_action == "Accelerate":
            keyboard.release(Key.right)
        elif current_action == "Brake/Reverse":
            keyboard.release(Key.left)

        # Press the new key
        if key_to_press:
            keyboard.press(key_to_press)
            print(f"Action: {new_action}, Key: {key_to_press.name} Pressed")
        else:  # If new_action is Neutral and no key to press
            print(f"Action: {new_action}")

        current_action = new_action
        last_action_time = current_time
    elif new_action == current_action and key_to_press:
        # If the same action is still active, ensure the key remains pressed.
        # This handles continuous holding of accelerate/brake.
        keyboard.press(key_to_press)
    elif new_action == "Neutral" and current_action != "Neutral":
        # If hand is no longer detected or in neutral zone, release the last held key
        if current_action == "Accelerate":
            keyboard.release(Key.right)
        elif current_action == "Brake/Reverse":
            keyboard.release(Key.left)
        print("Action: Neutral, Keys Released")
        current_action = "Neutral"
        last_action_time = current_time

    # Display current action on the frame
    display_color = active_action_color if current_action != "Neutral" else text_color
    cv2.putText(frame, f"Action: {current_action}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Hill Climb Racing Hand Control', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
print("Hill Climb Racing control stopped.")
