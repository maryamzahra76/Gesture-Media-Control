import math
import time
from collections import deque

import pyautogui

from .base import BaseMode

COOLDOWN = 2  # play/pause ke beech ka waqt (seconds)
VOLUME_DELAY = 0.5  # volume ke ek step ke beech ka waqt (seconds)
THUMB_STRAIGHT = 150  # is angle se zyada ho to angootha seedha maana jayega
THUMB_SIDE_MIN = 25  # angootha haath ki direction se kam az kam itna tirchha ho
THUMB_SIDE_MAX = 130  # aur is se zyada ulta na ho
STABLE_FRAMES = 4  # gesture itne frames lagataar dikhe tab maana jaye
SWIPE_DISTANCE = 0.12  # itni door jana zaroori hai (0 se 1 ke scale par)
SWIPE_WINDOW = 1.0  # itne seconds ke andar
SWIPE_COOLDOWN = 1.0  # ek swipe ke baad itna waqt agla swipe nahi
REARM_TIME = 0.4  # swipe ke baad ungli itni der ruke tab agla swipe
STILL_LIMIT = 0.03  # itni se kam harkat ko "ruka hua" maana jayega


def is_finger_folded(lm, tip_id, pip_id):
    wrist = lm[0]
    tip, pip = lm[tip_id], lm[pip_id]
    tip_dist = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
    pip_dist = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
    return tip_dist < pip_dist


def is_thumb_open(lm):
    tip, joint, base = lm[4], lm[3], lm[17]
    tip_dist = math.hypot(tip.x - base.x, tip.y - base.y)
    joint_dist = math.hypot(joint.x - base.x, joint.y - base.y)
    return tip_dist > joint_dist


def angle_between(ax, ay, bx, by):
    norm = math.hypot(ax, ay) * math.hypot(bx, by)
    if norm == 0:
        return 0
    cos = max(-1, min(1, (ax * bx + ay * by) / norm))
    return math.degrees(math.acos(cos))


def thumb_angle(lm):
    return angle_between(
        lm[2].x - lm[3].x, lm[2].y - lm[3].y,
        lm[4].x - lm[3].x, lm[4].y - lm[3].y,
    )


def is_thumb_straight(lm):
    return thumb_angle(lm) > THUMB_STRAIGHT


def is_thumb_to_the_side(lm):
    # haath ki direction: kalai (0) se middle ungli ki jad (9)
    # angootha ki direction: uski jad (2) se nok (4)
    angle = angle_between(
        lm[9].x - lm[0].x, lm[9].y - lm[0].y,
        lm[4].x - lm[2].x, lm[4].y - lm[2].y,
    )
    return THUMB_SIDE_MIN < angle < THUMB_SIDE_MAX


def detect_gesture(lm):
    index_folded = is_finger_folded(lm, 8, 6)
    middle_folded = is_finger_folded(lm, 12, 10)
    ring_folded = is_finger_folded(lm, 16, 14)
    pinky_folded = is_finger_folded(lm, 20, 18)

    no_finger_folded = not (
        index_folded or middle_folded or ring_folded or pinky_folded
    )
    if no_finger_folded and is_thumb_open(lm):
        return "Open Palm"

    others_folded = middle_folded and ring_folded and pinky_folded

    if others_folded and not index_folded:
        return "Pointing"

    all_fingers_down = index_folded and others_folded

    thumb_dx = lm[4].x - lm[2].x
    thumb_dy = lm[4].y - lm[2].y
    thumb_vertical = abs(thumb_dy) > abs(thumb_dx)

    if (all_fingers_down and is_thumb_straight(lm)
            and is_thumb_to_the_side(lm) and thumb_vertical):
        if thumb_dy < 0:
            return "Thumbs Up"
        return "Thumbs Down"

    return "None"


class MediaMode(BaseMode):
    name = "media"
    voice_commands = ["play", "pause", "volume up", "volume down"]

    def __init__(self, screen_w, screen_h):
        super().__init__(screen_w, screen_h)
        self.history = deque(maxlen=STABLE_FRAMES)
        self.stable = "None"
        self.last_action_time = 0
        self.last_volume_time = 0
        self.positions = deque()  # (waqt, x) ki list
        self.last_pointing_time = 0
        self.last_swipe_time = 0
        self.swipe_text = ""
        self.armed = True

    def process(self, lm, w, h):
        now = time.time()

        # Gesture tabhi maano jab lagataar STABLE_FRAMES frames same dikhe
        self.history.append(detect_gesture(lm))
        previous = self.stable
        if len(self.history) == STABLE_FRAMES and len(set(self.history)) == 1:
            self.stable = self.history[0]
        gesture = self.stable
        status = f"MEDIA: {gesture}"

        # Play/Pause: sirf jab Open Palm naya shuru ho
        if (gesture == "Open Palm" and previous != "Open Palm"
                and now - self.last_action_time > COOLDOWN):
            pyautogui.press("playpause")
            self.last_action_time = now
            status = "Play/Pause"

        # Volume: jab tak gesture dikhe, har VOLUME_DELAY par ek step
        if now - self.last_volume_time > VOLUME_DELAY:
            if gesture == "Thumbs Up":
                pyautogui.press("volumeup")
                self.last_volume_time = now
                status = "Volume Up"
            elif gesture == "Thumbs Down":
                pyautogui.press("volumedown")
                self.last_volume_time = now
                status = "Volume Down"

        # Swipe: Pointing gesture mein aaram se ek taraf harkat
        if gesture == "Pointing":
            self.last_pointing_time = now
            tip_x = lm[8].x
            self.positions.append((now, tip_x))

            while self.positions and now - self.positions[0][0] > SWIPE_WINDOW:
                self.positions.popleft()

            if not self.armed:
                # swipe ke baad ungli ruke to agla swipe allowed
                recent = [x for t, x in self.positions if now - t <= REARM_TIME]
                if (self.positions[0][0] <= now - REARM_TIME
                        and max(recent) - min(recent) < STILL_LIMIT):
                    self.armed = True
                    self.positions.clear()
            elif now - self.last_swipe_time > SWIPE_COOLDOWN:
                distance = tip_x - self.positions[0][1]
                if abs(distance) > SWIPE_DISTANCE:
                    if distance > 0:
                        pyautogui.press("nexttrack")
                        self.swipe_text = "Next Track"
                    else:
                        pyautogui.press("prevtrack")
                        self.swipe_text = "Previous Track"
                    self.last_swipe_time = now
                    self.armed = False
                    self.positions.clear()
        elif now - self.last_pointing_time > 0.3:
            self.positions.clear()
            self.armed = True

        if now - self.last_swipe_time < SWIPE_COOLDOWN:
            status = self.swipe_text

        return status

    def handle_voice(self, text):
        if text in ("play", "pause"):
            pyautogui.press("playpause")
            return "Play/Pause"
        if text == "volume up":
            pyautogui.press("volumeup")
            return "Volume Up"
        if text == "volume down":
            pyautogui.press("volumedown")
            return "Volume Down"
        return None

    def reset(self):
        self.history.clear()
        self.stable = "None"
        self.positions.clear()
        self.armed = True
