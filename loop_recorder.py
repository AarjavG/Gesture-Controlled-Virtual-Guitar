import time
from collections import deque
from pathlib import Path
import threading

class LoopRecorder:
    def __init__(self, bpm=120):
        self.bpm = bpm
        self.reset()
        self.playing = False
        self._play_thread = None

    def reset(self):
        self.recording = False
        self.start_time = 0.0
        self.events = deque()

    def toggle_recording(self):
        if not self.recording:
            print("[INFO] Recording started…")
            self.reset()
            self.recording = True
            self.start_time = time.time()
        else:
            self.recording = False
            print(f"[INFO] Recording stopped – {len(self.events)} events captured")

    def quantise(self, t):
        beat_len = 60 / self.bpm
        return round(t / beat_len) * beat_len

    def add_event(self, gesture):
        if self.recording:
            t = time.time() - self.start_time
            self.events.append((self.quantise(t), gesture))

    def _play_loop(self, player):
        if not self.events:
            print("[WARN] No events recorded")
            self.playing = False
            return

        print("[INFO] Loop playback started")
        loop_len = max(t for t, _ in self.events)
        start_play = time.time()
        idx = 0
        events = sorted(self.events)

        while self.playing:
            now = time.time() - start_play
            while idx < len(events) and now >= events[idx][0]:
                player.play(events[idx][1])
                idx += 1
            if now > loop_len:
                idx = 0
                start_play = time.time()
            time.sleep(0.001)  # tiny sleep to avoid busy loop

        print("[INFO] Loop playback stopped")

    def play(self, player):
        if self.playing:
            print("[INFO] Already playing loop")
            return

        self.playing = True
        self._play_thread = threading.Thread(target=self._play_loop, args=(player,), daemon=True)
        self._play_thread.start()

    def stop(self):
        if self.playing:
            self.playing = False
            if self._play_thread:
                self._play_thread.join()
                self._play_thread = None

    def save(self, path: Path):
        with open(path, "w") as f:
            for t, g in self.events:
                f.write(f"{t:.3f},{g}\n")
        print(f"[INFO] Loop saved to {path}")
