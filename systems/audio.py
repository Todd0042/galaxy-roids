import pygame
import os
import sys
import time

# ============================================================
#   RESOURCE PATH (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


# ---------------------------------------------------------
# GLOBAL MUSIC MODE
# ---------------------------------------------------------
music_mode = "16bit"

# ---------------------------------------------------------
# SFX COOLDOWN SYSTEM
# ---------------------------------------------------------

# Last time each sound was played
sfx_last_played = {}

# Per-sound cooldowns (seconds)
sfx_cooldowns = {}

# ⭐ Default cooldown for ALL sounds (strong anti-spam)
DEFAULT_SFX_COOLDOWN = 0.0

# ⭐ Minimum spacing for rapid-fire weapons (even if cooldown is lower)
RAPID_FIRE_MIN_SPACING = 0.15

# ⭐ Sounds considered rapid-fire
rapid_fire_sounds = {
    "laser",
    "weapon_pew",
    "weapon_spread",
}

# ⭐ Max simultaneous instances (prevents stacking)
MAX_INSTANCES = {
    "laser": 1,
    "weapon_pew": 1,
    "weapon_spread": 1,
    "boss_laser": 1,
}


def set_sfx_cooldown(name, seconds):
    """Set cooldown for a specific sound effect."""
    sfx_cooldowns[name] = seconds


def play_sfx(sfx_dict, name):
    """Play a sound effect with cooldown, spacing, and instance limits."""
    now = time.time()

    # Missing sound?
    if name not in sfx_dict or sfx_dict[name] is None:
        return

    sound = sfx_dict[name]

    # ---------------------------------------------------------
    # 1. Max instance limiter
    # ---------------------------------------------------------
    max_inst = MAX_INSTANCES.get(name)
    if max_inst is not None:
        if sound.get_num_channels() >= max_inst:
            return

    # ---------------------------------------------------------
    # 2. Cooldown check
    # ---------------------------------------------------------
    cd = sfx_cooldowns.get(name, DEFAULT_SFX_COOLDOWN)
    last = sfx_last_played.get(name, 0)

    # Rapid-fire minimum spacing
    if name in rapid_fire_sounds:
        cd = max(cd, RAPID_FIRE_MIN_SPACING)

    if now - last < cd:
        return

    # ---------------------------------------------------------
    # 3. Play sound
    # ---------------------------------------------------------
    try:
        sound.play()
        sfx_last_played[name] = now
    except Exception as e:
        print(f"[AUDIO] Failed to play SFX '{name}': {e}")


# ---------------------------------------------------------
# SOUND EFFECT LOADING
# ---------------------------------------------------------

def load_sfx(path):
    """Safely load a sound effect, returning None if missing."""
    try:
        return pygame.mixer.Sound(resource_path(path))
    except (pygame.error, FileNotFoundError):
        print(f"[AUDIO] Missing or invalid SFX: {path}")
        return None


def load_sounds(sound_map: dict):
    """Loads sound effects from a {name: path} dictionary."""
    loaded = {}

    for key, path in sound_map.items():
        full_path = resource_path(path)

        if not os.path.exists(full_path):
            print(f"[AUDIO] Missing file: {full_path}")
            continue

        try:
            loaded[key] = pygame.mixer.Sound(full_path)
        except Exception as e:
            print(f"[AUDIO] Failed to load {full_path}: {e}")

    return loaded


# ---------------------------------------------------------
# MUSIC PLAYBACK (MODE-AWARE)
# ---------------------------------------------------------

def play_music(track_name, volume=0.6, loop=-1, fade_ms=0):
    """Plays music from assets/music/<mode>/<track>.wav"""
    global music_mode

    rel = os.path.join("assets", "music", music_mode, f"{track_name}.wav")
    path = resource_path(rel)

    if not os.path.exists(path):
        print(f"[AUDIO] Missing music file: {path}")
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop, fade_ms=fade_ms)
        print(f"[AUDIO] Playing music: {path}")
    except (pygame.error, FileNotFoundError) as e:
        print(f"[AUDIO] Failed to play music {path}: {e}")
