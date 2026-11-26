import json
import queue
import threading


class VoiceListener:
    def __init__(self, model_path, phrases, device=None):
        self.model_path = model_path
        self.phrases = sorted(set(phrases))
        self.device = device
        self.out = queue.Queue()          # recognised text yahan aata hai
        self._audio = queue.Queue()
        self._stop = threading.Event()
        self.active = False               # dashboard toggle (voice on/off)
        self.error = None
        self.listening = False

    def start(self) -> bool:
        try:
            from vosk import Model, KaldiRecognizer
            import sounddevice as sd
            model = Model(self.model_path)
            # grammar = sirf known commands -> accuracy zyada, SRS FR-2.2 / SEC-3
            grammar = json.dumps(self.phrases + ["[unk]"])
            self._rec = KaldiRecognizer(model, 16000, grammar)
            self._stream = sd.RawInputStream(
                samplerate=16000, blocksize=4000, dtype="int16",
                channels=1, device=self.device, callback=self._on_audio)
            self._stream.start()
        except Exception as e:            # HI-1: mic/model na mile to gestures chalte rahen
            self.error = str(e)
            return False
        threading.Thread(target=self._run, daemon=True).start()
        self.active = True
        return True

    def _on_audio(self, indata, frames, time_info, status):
        if self.active:
            self._audio.put(bytes(indata))

    def _run(self):
        while not self._stop.is_set():
            try:
                data = self._audio.get(timeout=0.2)
            except queue.Empty:
                continue
            self.listening = True
            if self._rec.AcceptWaveform(data):
                text = json.loads(self._rec.Result()).get("text", "").strip()
                self.listening = False
                if text and text != "[unk]":
                    self.out.put(text)
                elif text == "[unk]":
                    self.out.put("")      # "Command not recognised" dikhane ke liye

    def stop(self):
        self._stop.set()
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass
