import time
import pygame
from collections import defaultdict

class MusicPlayer:
    def __init__(self, mapping):
        pygame.mixer.init()
        self.sounds = {}
        for gesture, path in mapping.items():
            try:
                self.sounds[gesture] = pygame.mixer.Sound(str(path))
            except pygame.error as e:
                print(f"[ERROR] Could not load {path}: {e}")
        self.last_played = defaultdict(lambda: 0.0)

    def play(self, gesture):
        # Remove time throttling to allow play on demand
        if gesture in self.sounds:
            self.sounds[gesture].play()

    def stop_all(self):
        for sound in self.sounds.values():
            sound.stop()

    def close(self):
        pygame.mixer.quit()
