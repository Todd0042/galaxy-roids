import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100
AMPLITUDE = 32767

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SFX_ROOT = os.path.join(SCRIPT_DIR, "assets", "sfx")


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


def env_linear(samples, start=1.0, end=0.0):
    n = len(samples)
    if n == 0:
        return samples
    out = []
    for i, s in enumerate(samples):
        t = i / (n - 1)
        a = start + (end - start) * t
        out.append(s * a)
    return out


def noise_sample():
    return random.uniform(-1.0, 1.0)


# ============================
# PLAYER SFX
# ============================

def gen_player_engine():
    duration = 1.5
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        base = math.sin(2 * math.pi * 110 * t) * 0.4
        shimmer = math.sin(2 * math.pi * (110 + 2 * math.sin(2 * math.pi * 0.5 * t)) * t) * 0.2
        airy = math.sin(2 * math.pi * 880 * t) * 0.05
        samples.append(base + shimmer + airy)
    path = os.path.join(SFX_ROOT, "player", "player_engine.wav")
    write_wav(path, samples)


def gen_player_hit():
    duration = 0.18
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 600 - (t * 1200)
        zap = math.sin(2 * math.pi * freq * t) * (1 - t)
        noise = math.sin(2 * math.pi * 4000 * t) * 0.2 * (1 - t)
        samples.append(zap + noise)
    path = os.path.join(SFX_ROOT, "player", "player_hit.wav")
    write_wav(path, samples)


def gen_player_low_health():
    duration = 1.2
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        pulse = math.sin(2 * math.pi * 2 * t)
        tone = math.sin(2 * math.pi * 440 * t) * (0.4 + 0.3 * pulse)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "player", "player_low_health.wav")
    write_wav(path, samples)


def gen_player_power_reset():
    duration = 0.35
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 400 + (t * 1200)
        tone = math.sin(2 * math.pi * freq * t) * (1 - (t * 0.5))
        sparkle = math.sin(2 * math.pi * (freq * 2) * t) * 0.2
        samples.append(tone + sparkle)
    path = os.path.join(SFX_ROOT, "player", "player_power_reset.wav")
    write_wav(path, samples)


def generate_player_sfx():
    gen_player_engine()
    gen_player_hit()
    gen_player_low_health()
    gen_player_power_reset()


# ============================
# WEAPONS
# ============================

def gen_weapon_pew():
    duration = 0.12
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 900 - (t * 600)
        tone = math.sin(2 * math.pi * freq * t) * (1 - t)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "weapons", "weapon_pew.wav")
    write_wav(path, samples)


def gen_weapon_spread():
    duration = 0.18
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        base = math.sin(2 * math.pi * (700 - t * 500) * t) * (1 - t)
        second = math.sin(2 * math.pi * (900 - t * 700) * t) * 0.4 * (1 - t)
        samples.append(base + second)
    path = os.path.join(SFX_ROOT, "weapons", "weapon_spread.wav")
    write_wav(path, samples)


def gen_weapon_laser_charge():
    duration = 0.6
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 200 + (t * 1800)
        tone = math.sin(2 * math.pi * freq * t) * (0.3 + 0.7 * t)
        shimmer = math.sin(2 * math.pi * freq * 2 * t) * 0.1
        samples.append(tone + shimmer)
    path = os.path.join(SFX_ROOT, "weapons", "weapon_laser_charge.wav")
    write_wav(path, samples)


def gen_weapon_missile():
    duration = 0.35
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        thump = math.sin(2 * math.pi * 80 * t) * (1 - t * 2)
        whoosh = math.sin(2 * math.pi * (200 + t * 800) * t) * 0.3
        samples.append(thump + whoosh)
    path = os.path.join(SFX_ROOT, "weapons", "weapon_missile.wav")
    write_wav(path, samples)


def generate_weapon_sfx():
    gen_weapon_pew()
    gen_weapon_spread()
    gen_weapon_laser_charge()
    gen_weapon_missile()


# ============================
# POWERUPS
# ============================

def gen_powerup_spawn():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 300 + t * 900
        tone = math.sin(2 * math.pi * freq * t) * (0.6 - 0.4 * t)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "powerups", "powerup_spawn.wav")
    write_wav(path, samples)


def gen_powerup_pickup():
    duration = 0.2
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq1 = 800 + t * 400
        freq2 = 1200 + t * 600
        tone = math.sin(2 * math.pi * freq1 * t) * 0.6 + math.sin(2 * math.pi * freq2 * t) * 0.3
        samples.append(tone * (1 - t * 0.5))
    path = os.path.join(SFX_ROOT, "powerups", "powerup_pickup.wav")
    write_wav(path, samples)


def generate_powerup_sfx():
    gen_powerup_spawn()
    gen_powerup_pickup()


# ============================
# ASTEROIDS
# ============================

def gen_asteroid_break():
    duration = 0.3
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        low = math.sin(2 * math.pi * 120 * t) * 0.4 * (1 - t)
        samples.append(n * 0.6 + low)
    path = os.path.join(SFX_ROOT, "asteroids", "asteroid_break.wav")
    write_wav(path, samples)


def gen_asteroid_destroy():
    duration = 0.4
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        boom = math.sin(2 * math.pi * 80 * t) * (1 - t * 2)
        samples.append(n * 0.7 + boom * 0.8)
    path = os.path.join(SFX_ROOT, "asteroids", "asteroid_destroy.wav")
    write_wav(path, samples)


def generate_asteroid_sfx():
    gen_asteroid_break()
    gen_asteroid_destroy()


# ============================
# BOSSES (GENERIC)
# ============================

def gen_boss_defeated():
    duration = 0.8
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 400 - t * 300
        tone = math.sin(2 * math.pi * freq * t) * (1 - t)
        sub = math.sin(2 * math.pi * 80 * t) * (1 - t)
        samples.append(tone * 0.6 + sub * 0.6)
    path = os.path.join(SFX_ROOT, "bosses", "boss_defeated.wav")
    write_wav(path, samples)


def gen_boss_hit():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        mid = math.sin(2 * math.pi * 200 * t) * 0.5 * (1 - t)
        samples.append(n * 0.7 + mid)
    path = os.path.join(SFX_ROOT, "bosses", "boss_hit.wav")
    write_wav(path, samples)


def gen_boss_death():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 60 * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(boom * 0.8 + n * 0.6)
    path = os.path.join(SFX_ROOT, "bosses", "boss_death.wav")
    write_wav(path, samples)


def gen_boss_laser_warning():
    duration = 0.6
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        pulse = math.sin(2 * math.pi * 4 * t)
        tone = math.sin(2 * math.pi * 700 * t) * (0.4 + 0.4 * pulse)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "bosses", "boss_laser_warning.wav")
    write_wav(path, samples)


def gen_boss_laser():
    duration = 0.7
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        tone = math.sin(2 * math.pi * 900 * t) * 0.6
        buzz = math.sin(2 * math.pi * 1800 * t) * 0.2
        samples.append(tone + buzz)
    path = os.path.join(SFX_ROOT, "bosses", "boss_laser.wav")
    write_wav(path, samples)


def generate_boss_generic_sfx():
    gen_boss_defeated()
    gen_boss_hit()
    gen_boss_death()
    gen_boss_laser_warning()
    gen_boss_laser()


# ============================
# BOSS 1
# ============================

def gen_boss1_entry():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        sweep = math.sin(2 * math.pi * (100 + t * 300) * t) * (1 - t * 0.5)
        sub = math.sin(2 * math.pi * 60 * t) * 0.5
        samples.append(sweep + sub)
    path = os.path.join(SFX_ROOT, "bosses", "boss1", "boss1_entry.wav")
    write_wav(path, samples)


def gen_boss1_hit():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        mid = math.sin(2 * math.pi * 250 * t) * 0.5 * (1 - t)
        samples.append(n * 0.6 + mid)
    path = os.path.join(SFX_ROOT, "bosses", "boss1", "boss1_hit.wav")
    write_wav(path, samples)


def gen_boss1_death():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 55 * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(boom * 0.9 + n * 0.5)
    path = os.path.join(SFX_ROOT, "bosses", "boss1", "boss1_death.wav")
    write_wav(path, samples)


def gen_boss1_laser_warning():
    duration = 0.6
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        pulse = math.sin(2 * math.pi * 3 * t)
        tone = math.sin(2 * math.pi * 650 * t) * (0.4 + 0.4 * pulse)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "bosses", "boss1", "boss1_laser_warning.wav")
    write_wav(path, samples)


def gen_boss1_laser():
    duration = 0.7
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        tone = math.sin(2 * math.pi * 850 * t) * 0.6
        buzz = math.sin(2 * math.pi * 1700 * t) * 0.2
        samples.append(tone + buzz)
    path = os.path.join(SFX_ROOT, "bosses", "boss1", "boss1_laser.wav")
    write_wav(path, samples)


def generate_boss1_sfx():
    gen_boss1_entry()
    gen_boss1_hit()
    gen_boss1_death()
    gen_boss1_laser_warning()
    gen_boss1_laser()


# ============================
# BOSS 2
# ============================

def gen_boss2_entry():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        sweep = math.sin(2 * math.pi * (90 + t * 250) * t) * (1 - t * 0.5)
        sub = math.sin(2 * math.pi * 50 * t) * 0.6
        samples.append(sweep + sub)
    path = os.path.join(SFX_ROOT, "bosses", "boss2", "boss2_entry.wav")
    write_wav(path, samples)


def gen_boss2_hit():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        mid = math.sin(2 * math.pi * 220 * t) * 0.5 * (1 - t)
        samples.append(n * 0.7 + mid)
    path = os.path.join(SFX_ROOT, "bosses", "boss2", "boss2_hit.wav")
    write_wav(path, samples)


def gen_boss2_death():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 50 * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(boom * 0.9 + n * 0.6)
    path = os.path.join(SFX_ROOT, "bosses", "boss2", "boss2_death.wav")
    write_wav(path, samples)


def gen_boss2_bomb_launch():
    duration = 0.4
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        whoosh = math.sin(2 * math.pi * (150 + t * 500) * t) * 0.6
        samples.append(whoosh * (1 - t * 0.5))
    path = os.path.join(SFX_ROOT, "bosses", "boss2", "boss2_bomb_launch.wav")
    write_wav(path, samples)


def gen_boss2_bomb_explode():
    duration = 0.5
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 70 * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(boom * 0.8 + n * 0.7)
    path = os.path.join(SFX_ROOT, "bosses", "boss2", "boss2_bomb_explode.wav")
    write_wav(path, samples)


def generate_boss2_sfx():
    gen_boss2_entry()
    gen_boss2_hit()
    gen_boss2_death()
    gen_boss2_bomb_launch()
    gen_boss2_bomb_explode()


# ============================
# BOSS 3
# ============================

def gen_boss3_entry():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        sweep = math.sin(2 * math.pi * (110 + t * 280) * t) * (1 - t * 0.5)
        sub = math.sin(2 * math.pi * 55 * t) * 0.6
        samples.append(sweep + sub)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_entry.wav")
    write_wav(path, samples)


def gen_boss3_hit():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        mid = math.sin(2 * math.pi * 230 * t) * 0.5 * (1 - t)
        samples.append(n * 0.7 + mid)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_hit.wav")
    write_wav(path, samples)


def gen_boss3_death():
    duration = 1.0
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 52 * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(boom * 0.9 + n * 0.6)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_death.wav")
    write_wav(path, samples)


def gen_boss3_tail_warning():
    duration = 0.4
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        pulse = math.sin(2 * math.pi * 5 * t)
        tone = math.sin(2 * math.pi * 500 * t) * (0.4 + 0.4 * pulse)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_tail_warning.wav")
    write_wav(path, samples)


def gen_boss3_tail_strike():
    duration = 0.3
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 600 - t * 400
        tone = math.sin(2 * math.pi * freq * t) * (1 - t)
        n = noise_sample() * (1 - t)
        samples.append(tone * 0.7 + n * 0.5)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_tail_strike.wav")
    write_wav(path, samples)


def gen_boss3_venom_launch():
    duration = 0.35
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 300 + t * 500
        tone = math.sin(2 * math.pi * freq * t) * 0.6
        samples.append(tone * (1 - t * 0.5))
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_venom_launch.wav")
    write_wav(path, samples)


def gen_boss3_venom_burst():
    duration = 0.35
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        n = noise_sample() * (1 - t)
        mid = math.sin(2 * math.pi * 260 * t) * 0.5 * (1 - t)
        samples.append(n * 0.8 + mid)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_venom_burst.wav")
    write_wav(path, samples)


def gen_boss3_dash():
    duration = 0.3
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 400 + t * 800
        tone = math.sin(2 * math.pi * freq * t) * (1 - t * 0.5)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_dash.wav")
    write_wav(path, samples)


def gen_boss3_weakspot_hit():
    duration = 0.25
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 900 - t * 500
        tone = math.sin(2 * math.pi * freq * t) * (1 - t)
        samples.append(tone)
    path = os.path.join(SFX_ROOT, "bosses", "boss3", "boss3_weakspot_hit.wav")
    write_wav(path, samples)


def generate_boss3_sfx():
    gen_boss3_entry()
    gen_boss3_hit()
    gen_boss3_death()
    gen_boss3_tail_warning()
    gen_boss3_tail_strike()
    gen_boss3_venom_launch()
    gen_boss3_venom_burst()
    gen_boss3_dash()
    gen_boss3_weakspot_hit()


def generate_all_boss_sfx():
    generate_boss_generic_sfx()
    generate_boss1_sfx()
    generate_boss2_sfx()
    generate_boss3_sfx()


# ============================
# UI
# ============================

def gen_ui_click():
    duration = 0.08
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 1200
        tone = math.sin(2 * math.pi * freq * t)
        samples.append(tone)
    samples = env_linear(samples, 1.0, 0.0)
    path = os.path.join(SFX_ROOT, "ui", "ui_click.wav")
    write_wav(path, samples)


def gen_ui_hover():
    duration = 0.12
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 900 + t * 200
        tone = math.sin(2 * math.pi * freq * t)
        samples.append(tone)
    samples = env_linear(samples, 0.8, 0.0)
    path = os.path.join(SFX_ROOT, "ui", "ui_hover.wav")
    write_wav(path, samples)


def gen_ui_popup_open():
    duration = 0.18
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq1 = 600 + t * 400
        freq2 = 900 + t * 600
        tone = math.sin(2 * math.pi * freq1 * t) * 0.6 + math.sin(2 * math.pi * freq2 * t) * 0.3
        samples.append(tone)
    samples = env_linear(samples, 1.0, 0.0)
    path = os.path.join(SFX_ROOT, "ui", "ui_popup_open.wav")
    write_wav(path, samples)


def gen_ui_confirm():
    duration = 0.18
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq1 = 700
        freq2 = 1000
        tone = math.sin(2 * math.pi * freq1 * t) * 0.7 + math.sin(2 * math.pi * freq2 * t) * 0.4
        samples.append(tone)
    samples = env_linear(samples, 1.0, 0.0)
    path = os.path.join(SFX_ROOT, "ui", "ui_confirm.wav")
    write_wav(path, samples)


def gen_ui_select_harder():
    duration = 0.22
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 500 + t * 700
        tone = math.sin(2 * math.pi * freq * t)
        samples.append(tone)
    samples = env_linear(samples, 1.0, 0.0)
    path = os.path.join(SFX_ROOT, "ui", "ui_select_harder.wav")
    write_wav(path, samples)


def generate_ui_sfx():
    gen_ui_click()
    gen_ui_hover()
    gen_ui_popup_open()
    gen_ui_confirm()
    gen_ui_select_harder()


# ============================
# LEVEL
# ============================

def gen_level_start():
    duration = 0.7
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq1 = 400 + t * 300
        freq2 = 600 + t * 500
        tone = math.sin(2 * math.pi * freq1 * t) * 0.6 + math.sin(2 * math.pi * freq2 * t) * 0.3
        samples.append(tone * (1 - t * 0.5))
    path = os.path.join(SFX_ROOT, "level", "level_start.wav")
    write_wav(path, samples)


def gen_level_complete():
    duration = 0.9
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq1 = 600 + t * 200
        freq2 = 900 + t * 300
        tone = math.sin(2 * math.pi * freq1 * t) * 0.6 + math.sin(2 * math.pi * freq2 * t) * 0.4
        samples.append(tone * (1 - t * 0.3))
    path = os.path.join(SFX_ROOT, "level", "level_complete.wav")
    write_wav(path, samples)


def generate_level_sfx():
    gen_level_start()
    gen_level_complete()


# ============================
# MASTER GENERATOR
# ============================

def generate_all():
    print("Generating ALL SFX (no music)...")
    generate_player_sfx()
    generate_weapon_sfx()
    generate_powerup_sfx()
    generate_asteroid_sfx()
    generate_all_boss_sfx()
    generate_ui_sfx()
    generate_level_sfx()
    print("Done! SFX written under:", SFX_ROOT)


if __name__ == "__main__":
    generate_all()
