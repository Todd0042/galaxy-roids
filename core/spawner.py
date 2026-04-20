import random
import math
import pygame


from settings import (
    POWERUP_SPAWN_CHANCE,
    BOSS_SPAWN_TIME,
)

from entities.powerups import Powerup
from entities.asteroid import Asteroid

# NEW: Modular boss imports
from entities.bosses import Boss1, Boss2, Boss3  # , Boss4, Boss5

# Correct enemy imports
from entities.enemies.regular_enemy import RegularEnemy
from entities.enemies.blob_enemy import BlobEnemy
from entities.enemies.bomber_enemy import BomberEnemy
from entities.enemies.stinger_enemy import StingerEnemy

# Needed for shrapnel explosion
from entities.projectiles import Bullet


# ==========================
#   SHRAPNEL EXPLOSION
# ==========================

def spawn_shrapnel_explosion(center, all_sprites, bullets_group):
    SHARP_SPEED = 8
    NUM_FRAGMENTS = 12

    for i in range(NUM_FRAGMENTS):
        angle = (360 / NUM_FRAGMENTS) * i
        direction = pygame.math.Vector2(1, 0).rotate(angle)
        vx = direction.x * SHARP_SPEED
        vy = direction.y * SHARP_SPEED

        frag = Bullet(
            pos=center,
            angle=angle,
            screen_w=9999,
            screen_h=9999,
            color=(255, 200, 0),
            size=4,
            is_bomber_fragment=True
        )
        frag.vel = pygame.Vector2(vx, vy)

        bullets_group.add(frag)
        all_sprites.add(frag)


# ==========================
#   RANDOM POWERUPS
# ==========================

def spawn_random_powerups(state, groups):
    if not state["game_active"]:
        return

    if random.random() < POWERUP_SPAWN_CHANCE:
        WIDTH = state["WIDTH"]
        HEIGHT = state["HEIGHT"]

        spawn_x = random.randint(0, WIDTH)
        spawn_y = random.randint(0, HEIGHT)

        p = Powerup(spawn_x, spawn_y, sfx=state["sfx"])
        groups["powerups"].add(p)
        groups["all_sprites"].add(p)


# ==========================
#   BOSS ROTATION SYSTEM
# ==========================

BOSS_LIST = [
    Boss1,  # levels 1–2
    Boss2,  # levels 3–4
    Boss3,  # levels 5–6
]


def get_boss_for_level(level):
    pair_index = (level - 1) // 2

    if pair_index < len(BOSS_LIST):
        return BOSS_LIST[pair_index]

    return Boss1 if pair_index % 2 == 0 else Boss2


# ==========================
#        BOSS SPAWN
# ==========================

def spawn_boss_if_ready(state, groups):
    if not state["game_active"]:
        return

    if state["boss_spawned"]:
        return

    ticks = pygame.time.get_ticks()
    boss_time = state.get("boss_spawn_time", BOSS_SPAWN_TIME)

    if ticks - state["level_start_time"] < boss_time:
        return

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]
    level = state["level"]
    speed = state["current_boss_speed"]

    boss_class = get_boss_for_level(level)
    boss = boss_class(WIDTH, HEIGHT, level, speed=speed)

    groups["boss_group"].add(boss)
    groups["all_sprites"].add(boss)

    state["boss_spawned"] = True

    # Guarantee boss theme
    sfx = state.get("sfx")
    if sfx and sfx.get("play_music"):
        try:
            sfx["play_music"]("boss_theme.ogg", fade_ms=800)
        except Exception:
            pass

# ==========================
#   SAFE RANDOM SPAWN POS (WRAP-AWARE)
# ==========================

DEFAULT_MIN_DIST = 1000
DANGEROUS_MIN_DIST = 1000

def wrapped_distance(a, b, WIDTH, HEIGHT):
    """
    Computes the shortest distance between two points on a toroidal (wrap-around) map.
    """
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)

    dx = min(dx, WIDTH - dx)
    dy = min(dy, HEIGHT - dy)

    return math.hypot(dx, dy)


def random_spawn_pos(player_pos, WIDTH, HEIGHT, min_dist=None):
    """
    Returns a random position that is at least `min_dist` away from the player,
    using wrap-aware distance so enemies cannot appear near the player after wrapping.
    """
    if min_dist is None:
        min_dist = DEFAULT_MIN_DIST

    while True:
        x = random.randint(40, WIDTH - 40)
        y = random.randint(40, HEIGHT - 40)
        pos = pygame.Vector2(x, y)

        # ⭐ wrap-aware distance check
        if wrapped_distance(pos, player_pos, WIDTH, HEIGHT) >= min_dist:
            return pos



# ==========================
#   PERIODIC ENEMY WAVES
# ==========================

def spawn_periodic_enemy_waves(state, groups):
    if not state["game_active"]:
        return

    if state["boss_spawned"]:
        return

    ticks = pygame.time.get_ticks()
    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]
    level = state["level"]
    speed = state["current_enemy_speed"]
    player = state["player"]

    # ==========================================================
    #   DYNAMIC SCALING FACTORS
    # ==========================================================
    elapsed = ticks - state["level_start_time"]

    base_interval = 2000  # ms

    level_factor = max(0.35, 1 - (level * 0.05))
    power_factor = max(0.45, 1 - (player.powerup_hits * 0.07))
    time_factor = max(0.5, 1.0 - (elapsed / 60000))

    spawn_interval = int(base_interval * level_factor * power_factor * time_factor)

    # First wave: spawn immediately at level start
    if state["last_periodic_spawn"] != 0:
        if ticks - state["last_periodic_spawn"] < spawn_interval:
            return

    # ==========================================================
    #   ENEMY COUNT SCALING
    # ==========================================================
    base_count = 2
    level_bonus = level // 3
    power_bonus = player.powerup_hits // 2
    time_bonus = min(4, elapsed // 15000)

    enemy_count = base_count + level_bonus + power_bonus + time_bonus

    # ==========================================================
    #   ENEMY TYPE POOL
    # ==========================================================
    enemy_pool = []

    if level >= 1:
        enemy_pool.append(RegularEnemy)
    if level >= 4:
        enemy_pool.append(BlobEnemy)
    if level >= 7:
        enemy_pool.append(BomberEnemy)
    if level >= 10:
        enemy_pool.append(StingerEnemy)

    # ==========================================================
    #   PER-TYPE MAXIMUMS
    # ==========================================================
    MAX_REGULAR = 16
    MAX_BLOB = 8
    MAX_BOMBER = 4
    MAX_STINGER = 4

    enemies = groups["enemies"]

    def count_type(cls):
        return sum(1 for e in enemies if isinstance(e, cls))

    # ==========================================================
    #   SPAWN WAVE WITH LIMITS
    # ==========================================================
    for _ in range(enemy_count):
        EnemyClass = random.choice(enemy_pool)

        # --- Check per-type caps ---
        if EnemyClass is RegularEnemy and count_type(RegularEnemy) >= MAX_REGULAR:
            continue
        if EnemyClass is BlobEnemy and count_type(BlobEnemy) >= MAX_BLOB:
            continue
        if EnemyClass is BomberEnemy and count_type(BomberEnemy) >= MAX_BOMBER:
            continue
        if EnemyClass is StingerEnemy and count_type(StingerEnemy) >= MAX_STINGER:
            continue

        # ⭐ Larger minimum distance for dangerous enemies
        if EnemyClass in (BomberEnemy, StingerEnemy):
            min_dist = 480
        else:
            min_dist = 220

        spawn_pos = random_spawn_pos(player.pos, WIDTH, HEIGHT, min_dist=min_dist)

        enemy = EnemyClass(
            pos=(spawn_pos.x, spawn_pos.y),
            width=WIDTH,
            height=HEIGHT,
            speed=speed,
            level=level
        )

        groups["enemies"].add(enemy)
        groups["all_sprites"].add(enemy)

    state["last_periodic_spawn"] = ticks



# ==========================
#   PERIODIC ASTEROIDS
# ==========================

def spawn_periodic_asteroids(state, groups):
    if not state["game_active"]:
        return

    ticks = pygame.time.get_ticks()

    if ticks % 7000 < 20:
        WIDTH = state["WIDTH"]
        HEIGHT = state["HEIGHT"]

        for _ in range(3):
            a = Asteroid(WIDTH, HEIGHT)
            groups["asteroids"].add(a)
            groups["all_sprites"].add(a)
