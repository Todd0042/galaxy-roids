import os
import wave
import struct
import math

SAMPLE_RATE = 44100
AMPLITUDE = 32767

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_ROOT = os.path.join(SCRIPT_DIR, "assets", "music")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_wav(path, samples):
    ensure_dir(os.path.dirname(path))
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)          # mono
        wav.setsampwidth(2)          # 16-bit
        wav.setframerate(SAMPLE_RATE)
        for s in samples:
            s_clamped = max(-1.0, min(1.0, s))
            wav.writeframes(struct.pack("<h", int(s_clamped * AMPLITUDE)))


def sq(freq, t):
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0


def tri(freq, t):
    return 2.0 * abs(2.0 * ((t * freq) - math.floor(t * freq + 0.5))) - 1.0


def noise(t):
    # simple hash-based pseudo noise
    x = int(t * 1234567) & 0xFFFFFFFF
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= (x >> 17)
    x ^= (x << 5) & 0xFFFFFFFF
    return ((x & 0xFFFF) / 32768.0) - 1.0


def note_freq(semitones_from_a4):
    return 440.0 * (2.0 ** (semitones_from_a4 / 12.0))


def build_pattern(notes, beat_len, bpm, total_beats):
    """
    notes: list of semitone offsets from A4 or None for rest
    beat_len: beats per note step (e.g. 1, 0.5)
    bpm: tempo
    total_beats: total beats to render
    """
    seconds_per_beat = 60.0 / bpm
    total_seconds = total_beats * seconds_per_beat
    total_samples = int(total_seconds * SAMPLE_RATE)
    samples = []

    steps = int(total_beats / beat_len)
    step_samples = int(beat_len * seconds_per_beat * SAMPLE_RATE)

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        step_index = min(i // step_samples, steps - 1)
        note = notes[step_index % len(notes)]
        if note is None:
            samples.append(0.0)
            continue
        f = note_freq(note)
        samples.append(sq(f, t))
    return samples


# -------------------------
# MENU THEME (warm, simple)
# -------------------------

def gen_menu_theme():
    bpm = 96
    total_beats = 64  # ~40s
    # A minor-ish: A3, C4, E4, G4 (relative to A4)
    bass_notes = [-12, -9, -5, -2]  # A3, C4, E4, G4
    bass_pattern = []
    for n in bass_notes:
        bass_pattern.extend([n] * 4)  # 4 beats each

    lead_notes = [-5, -2, -9, -7, -5, -2, -9, -12]  # simple motif
    lead_pattern = []
    for n in lead_notes:
        lead_pattern.extend([n] * 2)  # 2 beats each

    bass = build_pattern(bass_pattern, beat_len=1.0, bpm=bpm, total_beats=total_beats)
    lead = build_pattern(lead_pattern, beat_len=0.5, bpm=bpm, total_beats=total_beats)

    samples = []
    for i in range(len(bass)):
        t = i / SAMPLE_RATE
        b = tri(note_freq(bass_pattern[i // int((60/bpm)*SAMPLE_RATE)]), t) * 0.25 if i < len(bass) else 0.0
        l = lead[i] * 0.25 if i < len(lead) else 0.0
        pad = tri(2.0, t) * 0.05
        samples.append(b + l + pad)

    path = os.path.join(MUSIC_ROOT, "menu_theme.wav")
    write_wav(path, samples)


# -------------------------
# LEVEL THEME 1 (adventure)
# -------------------------

def gen_level_theme_1():
    bpm = 110
    total_beats = 80  # ~44s
    # D dorian-ish: D3, F3, G3, A3
    bass_notes = [-14, -11, -10, -9]  # D3, F3, G3, A3
    bass_pattern = []
    for n in bass_notes:
        bass_pattern.extend([n] * 4)

    lead_notes = [-2, -4, -5, -7, -5, -4, -2, -9]  # simple climbing/descending
    lead_pattern = []
    for n in lead_notes:
        lead_pattern.extend([n] * 2)

    bass = build_pattern(bass_pattern, beat_len=1.0, bpm=bpm, total_beats=total_beats)
    lead = build_pattern(lead_pattern, beat_len=0.5, bpm=bpm, total_beats=total_beats)

    samples = []
    for i in range(len(bass)):
        t = i / SAMPLE_RATE
        b = sq(note_freq(bass_pattern[i // int((60/bpm)*SAMPLE_RATE)]), t) * 0.22 if i < len(bass) else 0.0
        l = tri(note_freq(lead_pattern[i // int((30/bpm)*SAMPLE_RATE)]), t) * 0.22 if i < len(lead) else 0.0
        hat = noise(t) * (0.03 if (i // int((15/bpm)*SAMPLE_RATE)) % 2 == 0 else 0.0)
        samples.append(b + l + hat)

    path = os.path.join(MUSIC_ROOT, "level_theme_1.wav")
    write_wav(path, samples)


# -------------------------
# BOSS THEME (menacing)
# -------------------------

def gen_boss_theme():
    bpm = 120
    total_beats = 96  # ~48s
    # Darker: low power chord movement
    bass_notes = [-19, -17, -16, -14]  # low, tense
    bass_pattern = []
    for n in bass_notes:
        bass_pattern.extend([n] * 4)

    # Menacing ostinato
    ostinato_notes = [-7, -6, -7, -9, -7, -6, -7, -12]
    ostinato_pattern = []
    for n in ostinato_notes:
        ostinato_pattern.extend([n] * 2)

    bass = build_pattern(bass_pattern, beat_len=1.0, bpm=bpm, total_beats=total_beats)
    ost = build_pattern(ostinato_pattern, beat_len=0.5, bpm=bpm, total_beats=total_beats)

    samples = []
    for i in range(len(bass)):
        t = i / SAMPLE_RATE
        b = sq(note_freq(bass_pattern[i // int((60/bpm)*SAMPLE_RATE)]), t) * 0.3 if i < len(bass) else 0.0
        o = sq(note_freq(ostinato_pattern[i // int((30/bpm)*SAMPLE_RATE)]), t) * 0.22 if i < len(ost) else 0.0
        sub = tri(40.0, t) * 0.15
        hat = noise(t) * (0.02 if (i // int((15/bpm)*SAMPLE_RATE)) % 2 == 0 else 0.0)
        samples.append(b + o + sub + hat)

    path = os.path.join(MUSIC_ROOT, "boss_theme.wav")
    write_wav(path, samples)


# -------------------------
# VICTORY THEME
# -------------------------

def gen_victory_theme():
    bpm = 120
    total_beats = 32  # ~16s, but loopable
    # Bright: C major-ish
    bass_notes = [-12, -7, -5, -3]  # A3-ish upward
    bass_pattern = []
    for n in bass_notes:
        bass_pattern.extend([n] * 2)

    lead_notes = [-3, -5, -7, -8, -7, -5, -3, -12]
    lead_pattern = []
    for n in lead_notes:
        lead_pattern.extend([n] * 1)

    bass = build_pattern(bass_pattern, beat_len=1.0, bpm=bpm, total_beats=total_beats)
    lead = build_pattern(lead_pattern, beat_len=0.5, bpm=bpm, total_beats=total_beats)

    samples = []
    for i in range(len(bass)):
        t = i / SAMPLE_RATE
        b = tri(note_freq(bass_pattern[i // int((60/bpm)*SAMPLE_RATE)]), t) * 0.22 if i < len(bass) else 0.0
        l = sq(note_freq(lead_pattern[i // int((30/bpm)*SAMPLE_RATE)]), t) * 0.25 if i < len(lead) else 0.0
        pad = tri(3.0, t) * 0.06
        samples.append(b + l + pad)

    path = os.path.join(MUSIC_ROOT, "victory_theme.wav")
    write_wav(path, samples)


# -------------------------
# GAME OVER THEME
# -------------------------

def gen_game_over_theme():
    bpm = 80
    total_beats = 24  # ~18s
    # Descending, somber
    bass_notes = [-12, -14, -15, -17]
    bass_pattern = []
    for n in bass_notes:
        bass_pattern.extend([n] * 3)

    lead_notes = [-5, -7, -8, -10, -12, -14, -15, -17]
    lead_pattern = []
    for n in lead_notes:
        lead_pattern.extend([n] * 1)

    bass = build_pattern(bass_pattern, beat_len=1.0, bpm=bpm, total_beats=total_beats)
    lead = build_pattern(lead_pattern, beat_len=0.5, bpm=bpm, total_beats=total_beats)

    samples = []
    for i in range(len(bass)):
        t = i / SAMPLE_RATE
        b = tri(note_freq(bass_pattern[i // int((60/bpm)*SAMPLE_RATE)]), t) * 0.22 if i < len(bass) else 0.0
        l = tri(note_freq(lead_pattern[i // int((30/bpm)*SAMPLE_RATE)]), t) * 0.18 if i < len(lead) else 0.0
        noise_tail = noise(t) * 0.02
        samples.append(b + l + noise_tail)

    path = os.path.join(MUSIC_ROOT, "game_over_theme.wav")
    write_wav(path, samples)


def generate_all_music():
    print("Generating music loops...")
    gen_menu_theme()
    gen_level_theme_1()
    gen_boss_theme()
    gen_victory_theme()
    gen_game_over_theme()
    print("Done! Music written under:", MUSIC_ROOT)


if __name__ == "__main__":
    generate_all_music()
