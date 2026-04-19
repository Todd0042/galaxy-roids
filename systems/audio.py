import pygame


def load_sfx(filename):
    try:
        return pygame.mixer.Sound(filename)
    except (pygame.error, FileNotFoundError):
        return None


def init_sfx():
    return {
        "pew": load_sfx("pew.wav"),
        "boom": load_sfx("boom.wav"),
        "poof": load_sfx("poof.wav"),
        "splat": load_sfx("splat.wav"),
        "tada": load_sfx("tada.wav"),
    }


def play_music(filename):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError):
        pass
