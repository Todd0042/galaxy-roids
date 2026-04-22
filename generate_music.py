import os
import wave
import struct
import math
import random

SAMPLE_RATE = 22050
AMPLITUDE = 32767

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_ROOT_16 = os.path.join(SCRIPT_DIR, "assets", "music", "16bit")
MUSIC_ROOT_8 = os.path.join(SCRIPT_DIR, "assets", "music", "8bit")


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


# -------- Waveforms --------

def sq(freq, t):
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0


def tri(freq, t):
    return 2.0 * abs(2.0 * ((t * freq) - math.floor(t * freq + 0.5))) - 1.0


def noise():
    return random.uniform(-1.0, 1.0)


def note_freq(semi):
    return 440.0 * (2.0 ** (semi / 12.0))


# -------- Melody Sequencer (safe, loops) --------

def sequence_melody(notes, durations, total_seconds, waveform, volume=0.35):
    samples = []
    t = 0.0
    i = 0

    while t < total_seconds:
        note = notes[i % len(notes)]
        dur = durations[i % len(durations)]
        frames = int(dur * SAMPLE_RATE)

        for _ in range(frames):
            tt = len(samples) / SAMPLE_RATE
            if note is None:
                samples.append(0.0)
            else:
                freq = note_freq(note)
                samples.append(waveform(freq, tt) * volume)
        t += dur
        i += 1

    return samples


# --- ENVELOPES ---

def env_decay(t, length):
    """Fast exponential decay envelope."""
    return math.exp(-t * (8.0 / length))


def env_short(t, length):
    """Very short percussive envelope."""
    return math.exp(-t * (25.0 / length))


# --- DRUM VOICES (SNAPPY) ---

def drum_kick(t):
    """
    NES-style kick: pitched triangle + fast decay.
    """
    freq = 80 - (t * 60)  # pitch drop
    return tri(freq, t) * env_decay(t, 0.12)


def drum_snare(t):
    """
    NES-style snare: shaped noise + short envelope.
    """
    n = noise()
    shaped = n - (tri(40, t) * 0.2)  # remove low rumble
    return shaped * env_short(t, 0.08)


def drum_hat(t):
    """
    NES-style hi-hat: very short noise tick.
    """
    return noise() * env_short(t, 0.03)


# --- DRUM SEQUENCER ---

def apply_drums(samples, bpm, kick_pattern, snare_pattern, hat_pattern):
    beat_seconds = 60.0 / bpm
    beat_samples = int(beat_seconds * SAMPLE_RATE)

    out = samples[:]  # copy

    for i in range(len(samples)):
        t = i / SAMPLE_RATE
        beat_index = (i // beat_samples) % len(kick_pattern)

        # Time within the beat (for envelopes)
        t_in_beat = (i % beat_samples) / SAMPLE_RATE

        if kick_pattern[beat_index]:
            out[i] += drum_kick(t_in_beat) * 0.9

        if snare_pattern[beat_index]:
            out[i] += drum_snare(t_in_beat) * 0.7

        if hat_pattern[beat_index]:
            out[i] += drum_hat(t_in_beat) * 0.5

    return out



# =========================================================
# 16‑BIT TRACKS (warmer, hybrid retro, SNES‑ish with drums)
# =========================================================

def gen_menu_16():
    bpm = 96
    notes = [-12, -9, -5, -2]  # A minor arpeggio
    durations = [0.5] * len(notes)
    base = sequence_melody(notes, durations, 45, sq, volume=0.35)

    # Soft pad
    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        pad = tri(2.0, t) * 0.05
        samples.append(s * 0.7 + pad)


    write_wav(os.path.join(MUSIC_ROOT_16, "menu_theme.wav"), samples)


def gen_level_16():
    bpm = 110
    notes = [-14, -10, -7, -5, -7, -10]  # D dorian-ish
    durations = [0.4] * len(notes)
    base = sequence_melody(notes, durations, 50, sq, volume=0.35)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        pad = tri(3.0, t) * 0.04
        samples.append(s * 0.7 + pad)


    write_wav(os.path.join(MUSIC_ROOT_16, "level_theme_1.wav"), samples)


def gen_boss_16():
    bpm = 120
    notes = [-24, -22, -21, -19, -24, -22, -21, -17]  # dark, tense
    durations = [0.35] * len(notes)
    base = sequence_melody(notes, durations, 55, sq, volume=0.4)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        sub = tri(40.0, t) * 0.2
        buzz = sq(120 + 20 * math.sin(t * 2), t) * 0.15
        samples.append(s * 0.6 + sub + buzz)


    write_wav(os.path.join(MUSIC_ROOT_16, "boss_theme.wav"), samples)


def gen_victory_16():
    bpm = 120
    notes = [-3, -5, -7, -8, -7, -5, -3, -12]
    durations = [0.3] * len(notes)
    base = sequence_melody(notes, durations, 20, sq, volume=0.4)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        pad = tri(4.0, t) * 0.05
        samples.append(s * 0.7 + pad)

    write_wav(os.path.join(MUSIC_ROOT_16, "victory_theme.wav"), samples)


def gen_game_over_16():
    bpm = 80
    notes = [-12, -14, -15, -17, -19, -21]  # descending
    durations = [0.5] * len(notes)
    base = sequence_melody(notes, durations, 25, tri, volume=0.35)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        hiss = noise() * 0.02
        samples.append(s * 0.7 + hiss)


    write_wav(os.path.join(MUSIC_ROOT_16, "game_over_theme.wav"), samples)


# =========================================================
# 8‑BIT TRACKS (NES‑style, SMB‑ish, with drums)
# =========================================================

def gen_menu_8():
    bpm = 96
    notes = [-12, -9, -5, -2]
    durations = [0.25] * len(notes)
    samples = sequence_melody(notes, durations, 40, sq, volume=0.35)

    write_wav(os.path.join(MUSIC_ROOT_8, "menu_theme.wav"), samples)


def gen_level_8():
    bpm = 110
    notes = [-14, -10, -7, -5, -7, -10]
    durations = [0.2] * len(notes)
    samples = sequence_melody(notes, durations, 45, sq, volume=0.35)


    write_wav(os.path.join(MUSIC_ROOT_8, "level_theme_1.wav"), samples)


def gen_boss_8():
    bpm = 120
    notes = [-24, -22, -21, -19, -24, -22, -21, -17]
    durations = [0.18] * len(notes)
    base = sequence_melody(notes, durations, 50, sq, volume=0.4)

    samples = []
    for i, s in enumerate(base):
        t = i / SAMPLE_RATE
        sub = tri(40.0, t) * 0.2
        samples.append(s * 0.7 + sub)


    write_wav(os.path.join(MUSIC_ROOT_8, "boss_theme.wav"), samples)


def gen_victory_8():
    bpm = 120
    notes = [-3, -5, -7, -8, -7, -5, -3, -12]
    durations = [0.2] * len(notes)
    samples = sequence_melody(notes, durations, 15, sq, volume=0.4)


    write_wav(os.path.join(MUSIC_ROOT_8, "victory_theme.wav"), samples)


def gen_game_over_8():
    bpm = 40
    notes = [-12, -14, -15, -17, -19, -21]
    durations = [0.3] * len(notes)
    samples = sequence_melody(notes, durations, 20, tri, volume=0.35)


    write_wav(os.path.join(MUSIC_ROOT_8, "game_over_theme.wav"), samples)


# -------- Master --------

def generate_all_music():
    print("Generating 16‑bit music...")
    gen_menu_16()
    gen_level_16()
    gen_boss_16()
    gen_victory_16()
    gen_game_over_16()

    print("Generating 8‑bit music...")
    gen_menu_8()
    gen_level_8()
    gen_boss_8()
    gen_victory_8()
    gen_game_over_8()

    print("Done! Music written under:")
    print("  ", MUSIC_ROOT_16)
    print("  ", MUSIC_ROOT_8)


if __name__ == "__main__":
    generate_all_music()
