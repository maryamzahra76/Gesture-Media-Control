# Media Mode (Gesture Control)

Media Mode for the Hands-Free Computing FYP. Controls media playback in VLC, YouTube
using hand gestures captured through the webcam.

## Gestures

| Action | Gesture |
|---|---|
| Play / Pause | Open palm |
| Volume up | Thumbs up (hold) |
| Volume down | Thumbs down (hold) |
| Next track | Index finger pointing, move right |
| Previous track | Index finger pointing, move left |

## Requirements

- Python 3.12
- Webcam

Install the libraries:

    pip install -r requirements.txt

## Project structure

    handsfree/
        modes/
            __init__.py
            base.py          shared mode interface
            media_mode.py    Media Mode (this module)
    test_media_mode.py       standalone test runner for Media Mode
    requirements.txt

## Run the test

From the project root:

    python test_media_mode.py

Press `q` in the camera window to quit.

## Integration

`MediaMode` follows the shared `BaseMode` interface:

- `process(lm, w, h)` handles gestures for each frame and returns a status text
- `handle_voice(text)` is not implemented yet, voice will be added later
- `reset()` clears gesture and swipe state

Camera and MediaPipe are handled by the shared `main.py`, this module only
reads the landmarks.