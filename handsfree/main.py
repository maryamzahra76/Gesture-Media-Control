import time
import webbrowser

import cv2
import mediapipe as mp
import pyautogui

from modes import MODE_CLASSES
from voice import VoiceListener
import context

# ---------------- config ----------------
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
AUTO_CONTEXT = False          # context-aware: sab modes ready hon tab True karo
GLOBAL_COMMANDS = ["open browser", "close window"]
CONFIRM_TIMEOUT = 5           # seconds, SAF-1

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False    # kill switch: 'q' / 'p'. SRS SAF-3 update karna hai


def is_thumbs_up(lm):
    up = lm[4].y < lm[3].y < lm[2].y and lm[4].y < lm[5].y
    folded = all(lm[t].y > lm[p].y for t, p in ((8, 6), (12, 10), (16, 14), (20, 18)))
    return up and folded


def main():
    sw, sh = pyautogui.size()
    modes = {name: cls(sw, sh) for name, cls in MODE_CLASSES.items()}
    current = modes["cursor"]

    # voice: sab modes ki commands ek grammar mein
    phrases = list(GLOBAL_COMMANDS)
    for m in modes.values():
        phrases += m.voice_commands
    voice = VoiceListener(VOSK_MODEL_PATH, phrases)
    voice_ok = voice.start()
    if not voice_ok:
        print("Voice off (gestures only):", voice.error)

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, model_complexity=0,
                           min_detection_confidence=0.7, min_tracking_confidence=0.7)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    paused = False
    pending_confirm = None    # (action_name, deadline)
    msg, msg_until = "", 0

    def set_mode(name):
        nonlocal current
        if modes[name] is not current:
            current.reset()
            current = modes[name]

    def say(text, secs=1.5):
        nonlocal msg, msg_until
        msg, msg_until = text, time.time() + secs

    last_ctx_check = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # ---- context-aware (last mein) ----
        if AUTO_CONTEXT and time.time() - last_ctx_check > 0.5:
            set_mode(context.mode_for_active_app())
            last_ctx_check = time.time()

        # ---- voice queue ----
        while not voice.out.empty():
            text = voice.out.get()
            if not text:
                say("Command not recognized")
                continue
            if text == "open browser":
                webbrowser.open("https://www.google.com")
                say("Open Browser")
            elif text == "close window":
                pending_confirm = ("close window", time.time() + CONFIRM_TIMEOUT)
                say("Thumbs up to confirm", CONFIRM_TIMEOUT)
            else:
                try:
                    r = current.handle_voice(text)
                except Exception as e:
                    print("voice error:", e); r = None
                say(r or "Command not recognized")

        # ---- gestures ----
        status = "PAUSED" if paused else "NO HAND DETECTED"
        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.multi_hand_landmarks and not paused:
            hl = res.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            lm = hl.landmark

            if pending_confirm:
                if time.time() > pending_confirm[1]:
                    pending_confirm = None
                    say("Confirmation timed out")
                elif is_thumbs_up(lm):
                    pyautogui.hotkey("alt", "f4")   # TODO: HandsFree apni window par na chale (SAF-1)
                    pending_confirm = None
                    say("Window closed")
                status = "WAITING CONFIRM"
            else:
                try:
                    status = current.process(lm, w, h)
                except Exception as e:             # ek member ka bug poora system na giraye
                    print(f"[{current.name}] error:", e)
                    status = "MODE ERROR"
        else:
            current.reset()                         # hand gum -> drag release, state clear

        # ---- preview ----
        if time.time() < msg_until:
            status = msg
        cv2.putText(frame, f"Mode: {current.name}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(frame, "Voice: " + ("ON" if voice_ok and voice.active else "OFF"),
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        cv2.imshow("HandsFree", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("p"):
            paused = not paused
            current.reset()
        elif key == ord("v") and voice_ok:
            voice.active = not voice.active
        elif key in (ord("1"), ord("2"), ord("3")):
            set_mode(["cursor", "media", "presentation"][key - ord("1")])

    current.reset()
    voice.stop()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
