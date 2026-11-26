# Media Mode (Gesture and Voice Control)

Media Mode for the Hands-Free Computing FYP. Controls media playback in VLC
using hand gestures from the webcam and offline voice commands.

## Gestures

| Action | Gesture |
|---|---|
| Play / Pause | Open palm |
| Volume up | Thumbs up (hold) |
| Volume down | Thumbs down (hold) |
| Next track | Index finger pointing, move right |
| Previous track | Index finger pointing, move left |

## Voice commands

| Command | Action |
|---|---|
| play | Play / Pause (toggle) |
| pause | Play / Pause (toggle) |
| volume up | Volume up |
| volume down | Volume down |

Play and pause both send the same media key, so they toggle playback.

## Requirements

- Python 3.12
- Webcam and microphone

Install the libraries:

    pip install -r requirements.txt

For voice, download `vosk-model-small-en-us-0.15` from
https://alphacephei.com/vosk/models and place the extracted folder inside a
`models` folder in the project root.

## Using Media Mode in the HandsFree project

1. Copy `handsfree/modes/media_mode.py` into your `handsfree/modes/` folder.
2. Make sure `MediaMode` is registered in `modes/__init__.py`.
3. Run from the project root:

       python handsfree/main.py

4. Click the camera window and press `2` to select Media Mode.
5. Press `q` in the camera window to quit.

## Files

    handsfree/
        modes/
            base.py          shared mode interface
            media_mode.py    Media Mode
    requirements.txt
