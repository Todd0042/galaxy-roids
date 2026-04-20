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
    Returns a dict of all sound effects used in the game.
    Organized by category for clarity and future expansion.
    """
    base = "assets/sfx"

    return {

        # --------------------------
        # PLAYER WEAPONS
        # --------------------------
        "weapon_pew":          load_sfx(os.path.join(base, "weapon_pew.wav")),
        "weapon_laser":        load_sfx(os.path.join(base, "weapon_laser.wav")),
        "weapon_missile":      load_sfx(os.path.join(base, "weapon_missile.wav")),
        "weapon_beam_charge":  load_sfx(os.path.join(base, "weapon_beam_charge.wav")),
        "weapon_beam_fire":    load_sfx(os.path.join(base, "weapon_beam_fire.wav")),

        # --------------------------
        # BUG ENEMIES
        # --------------------------
        "bug_small_death":     load_sfx(os.path.join(base, "bug_small_death.wav")),
        "bug_big_death":       load_sfx(os.path.join(base, "bug_big_death.wav")),
        "bug_spit":            load_sfx(os.path.join(base, "bug_spit.wav")),
        "bug_hit":             load_sfx(os.path.join(base, "bug_hit.wav")),

        # --------------------------
        # BOSSES
        # --------------------------
        "boss_roar":           load_sfx(os.path.join(base, "boss_roar.wav")),
        "boss_laser":          load_sfx(os.path.join(base, "boss_laser.wav")),
        "boss_missile":        load_sfx(os.path.join(base, "boss_missile.wav")),
        "boss_phase":          load_sfx(os.path.join(base, "boss_phase.wav")),
        "boss_death":          load_sfx(os.path.join(base, "boss_death.wav")),

        # --------------------------
        # GENERIC / SHARED
        # --------------------------
        "explosion_small":     load_sfx(os.path.join(base, "explosion_small.wav")),
        "explosion_big":       load_sfx(os.path.join(base, "explosion_big.wav")),
        "ui_click":            load_sfx(os.path.join(base, "ui_click.wav")),
        "ui_error":            load_sfx(os.path.join(base, "ui_error.wav")),
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
