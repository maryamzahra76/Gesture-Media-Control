"""Har mode isi class se inherit karega. Interface FIX hai, change karna ho to teeno se baat karke."""
from typing import List, Optional


class BaseMode:
    name = "base"                 # "cursor" / "media" / "presentation"
    voice_commands: List[str] = []  # is mode ki extra voice commands (Vosk grammar mein add hongi)

    def __init__(self, screen_w: int, screen_h: int):
        self.sw, self.sh = screen_w, screen_h

    def process(self, lm, w: int, h: int) -> str:
        """Har frame jab hand mile. lm = hand_landmarks.landmark.
        Short status text return karo (status circle / preview mein dikhega)."""
        return "TRACKING"

    def handle_voice(self, text: str) -> Optional[str]:
        """Recognised voice text aaye to. Status text return karo, ya None agar is mode ka nahi."""
        return None

    def reset(self) -> None:
        """Hand gum / mode change / pause par call hota hai. Drag release, state clear yahan karo."""
        pass
