import cv2
import mediapipe as mp
import pyautogui

from handsfree.modes.media_mode import MediaMode

GREEN = (0, 255, 0)
RED = (0, 0, 255)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()
mode = MediaMode(screen_w, screen_h)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not found")
    raise SystemExit

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Error: Cannot read frame")
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            status, color = mode.process(hand.landmark, w, h), GREEN
        else:
            mode.reset()
            status, color = "No Hand", RED

        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.imshow("Media Mode Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()