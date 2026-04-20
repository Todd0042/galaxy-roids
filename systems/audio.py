import pygame
import os


def load_sfx(path):
    """Safely load a sound effect, returning None if missing."""
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError):
        print(f"[AUDIO] Missing or invalid SFX: {path}")
        return None


def load_sounds(sound_map: dict):
    """
    Loads sound effects from a {name: path} dictionary.
    This matches the API expected by game_init.py.
    """
    loaded = {}

    for key, path in sound_map.items():
        if not os.path.exists(path):
            print(f"[AUDIO] Missing file: {path}")
            continue

        try:
            loaded[key] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"[AUDIO] Failed to load {path}: {e}")

    return loaded


def play_music(filename, volume=0.6, loop=-1, fade_ms=0):
    """
    Plays looping background music from assets/music/.
    Safe if file doesn't exist.
    Supports optional fade-in.
    """
    path = os.path.join("assets/music", filename)

    if not os.path.exists(path):
        print(f"[AUDIO] Missing music file: {path}")
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop, fade_ms=fade_ms)
    except (pygame.error, FileNotFoundError) as e:
        print(f"[AUDIO] Failed to play music {path}: {e}")

