import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100
AMPLITUDE = 32767

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_ROOT = os.path.join(SCRIPT_DIR, "assets", "music")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_wav(path, samples):
    ensure_dir(os.path.dirname(path))
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            wav.writeframes(struct.pack("<h", int(s * AMPLITUDE)))


# --- Basic waveforms (authentic 16-bit style) ---

def sq(freq, t):
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0

def tri(freq, t):
    return 2.0 * abs(2.0 * ((t * freq) - math.floor(t * freq + 0.5))) - 1.0

def noise():
    return random.uniform(-1.0, 1.0)

def note_freq(semi):
    return 440.0 * (2.0 ** (semi / 12.0))


# --- Simple sequencer (safe, loops forever) ---

def sequence(notes, durations, total_seconds):
    """
    notes: list of semitone offsets (or None for rest)
    durations: list of seconds per note
    total_seconds: total track length
    """
    samples = []
    t = 0.0
    i = 0

    while t < total_seconds:
        note = notes[i % len(notes)]
        dur = durations[i % len(durations)]
        frames = int(dur * SAMPLE_RATE)

        for f in range(frames):
            tt = (len(samples) / SAMPLE_RATE)
            if note is None:
                samples.append(0.0)
            else:
                freq = note_freq(note)
                samples.append(sq(freq, tt) * 0.35)
        t += dur
        i += 1

    return samples


# --- Track generators ---

def gen_menu_theme():
    notes = [-12, -9, -5, -2]  # A minor arpeggio
    durations = [0.5, 0.5, 0.5, 0.5]
    base = sequence(notes, durations, 45)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        pad = tri(2.0, t) * 0.05
        samples.append(s * 0.6 + pad)
    write_wav(os.path.join(MUSIC_ROOT, "menu_theme.wav"), samples)


def gen_level_theme_1():
    notes = [-14, -10, -7, -5, -7, -10]  # D dorian-ish
    durations = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
    base = sequence(notes, durations, 50)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        hat = noise() * (0.03 if (i // 5000) % 2 == 0 else 0.0)
        samples.append(s * 0.55 + hat)
    write_wav(os.path.join(MUSIC_ROOT, "level_theme_1.wav"), samples)


def gen_boss_theme():
    # Dark, menacing, low intervals
    notes = [-24, -22, -21, -19, -24, -22, -21, -17]
    durations = [0.35] * len(notes)
    base = sequence(notes, durations, 55)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        sub = tri(40, t) * 0.2
        buzz = sq(120 + 20 * math.sin(t * 2), t) * 0.15
        samples.append(s * 0.5 + sub + buzz)
    write_wav(os.path.join(MUSIC_ROOT, "boss_theme.wav"), samples)


def gen_victory_theme():
    notes = [-3, -5, -7, -8, -7, -5, -3, -12]  # bright
    durations = [0.3] * len(notes)
    base = sequence(notes, durations, 20)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        pad = tri(3.0, t) * 0.05
        samples.append(s * 0.6 + pad)
    write_wav(os.path.join(MUSIC_ROOT, "victory_theme.wav"), samples)


def gen_game_over_theme():
    notes = [-12, -14, -15, -17, -19, -21]  # descending
    durations = [0.5] * len(notes)
    base = sequence(notes, durations, 25)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        hiss = noise() * 0.02
        samples.append(s * 0.5 + hiss)
    write_wav(os.path.join(MUSIC_ROOT, "game_over_theme.wav"), samples)


def generate_all_music():
    print("Generating 16-bit music loops...")
    gen_menu_theme()
    gen_level_theme_1()
    gen_boss_theme()
    gen_victory_theme()
    gen_game_over_theme()
    print("Done! Music written under:", MUSIC_ROOT)


if __name__ == "__main__":
    generate_all_music()
