import pygame
import os


def load_sfx(path):
    """Safely load a sound effect, returning None if missing."""
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError):
        return None


def load_sounds():
    """
    Returns a dict of all sound effects.
    Matches the API expected by game_init.py and main.py.
    """
    base = "assets/sfx"

    return {
        "pew":   load_sfx(os.path.join(base, "pew.wav")),
        "boom":  load_sfx(os.path.join(base, "boom.wav")),
        "poof":  load_sfx(os.path.join(base, "poof.wav")),
        "splat": load_sfx(os.path.join(base, "splat.wav")),
        "tada":  load_sfx(os.path.join(base, "tada.wav")),
    }


def play_music(filename):
    """
    Plays looping background music from assets/music/.
    Safe if file doesn't exist.
    """
    try:
        path = os.path.join("assets/music", filename)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError):
        pass
