import random
import pygame

from settings import (
    POWERUP_SPAWN_CHANCE,
    BOSS_SPAWN_TIME,
)

from entities.powerups import Powerup
from entities.asteroid import Asteroid

# NEW: Modular boss imports
from entities.bosses import Boss1, Boss2, Boss3 #, Boss4, Boss5

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

        p = Powerup(spawn_x, spawn_y)
        groups["powerups"].add(p)
        groups["all_sprites"].add(p)



# ==========================
#   BOSS ROTATION SYSTEM
# ==========================

# Bosses assigned in 2‑level pairs:
# 1–2 → Boss1
# 3–4 → Boss2
# 5–6 → Boss3 (if exists, else fallback)
# 7–8 → Boss4 (if exists, else fallback)
# etc.
BOSS_LIST = [
    Boss1,  # levels 1–2
    Boss2,  # levels 3–4
    Boss3,  # levels 5–6
    # Boss4,  # levels 7–8
    # Boss5,  # levels 9–10
]


def get_boss_for_level(level):
    pair_index = (level - 1) // 2

    # If we have a boss for this pair, use it
    if pair_index < len(BOSS_LIST):
        return BOSS_LIST[pair_index]

    # Fallback logic:
    # Even pair_index → Boss1
    # Odd pair_index  → Boss2
    if pair_index % 2 == 0:
        return Boss1
    else:
        return Boss2


# ==========================
#        BOSS SPAWN
# ==========================

def spawn_boss_if_ready(state, groups, play_music):
    if not state["game_active"]:
        return

    if state["boss_spawned"]:
        return

    ticks = pygame.time.get_ticks()
    if ticks - state["level_start_time"] < BOSS_SPAWN_TIME:
        return

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]
    level = state["level"]
    speed = state["current_boss_speed"]

    # NEW: Modular boss selection
    boss_class = get_boss_for_level(level)
    boss = boss_class(WIDTH, HEIGHT, level, speed=speed)

    groups["boss_group"].add(boss)
    groups["all_sprites"].add(boss)

    state["boss_spawned"] = True

    # Play boss music
    play_music(f"boss{((level - 1) % 5) + 1}.midi")


# ==========================
#   PERIODIC ENEMY WAVES
# ==========================

def spawn_periodic_enemy_waves(state, groups):
    if not state["game_active"]:
        return

    if state["boss_spawned"]:
        return

    ticks = pygame.time.get_ticks()
    if ticks - state["last_periodic_spawn"] <= 5000:
        return

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]
    level = state["level"]
    speed = state["current_enemy_speed"]

    enemy_pool = []

    if level >= 1:
        enemy_pool.append(RegularEnemy)
    if level >= 4:
        enemy_pool.append(BlobEnemy)
    if level >= 7:
        enemy_pool.append(BomberEnemy)
    if level >= 10:
        enemy_pool.append(StingerEnemy)

    for _ in range(5):
        EnemyClass = random.choice(enemy_pool)

        e1 = EnemyClass(
            pos=(60, random.randint(100, HEIGHT - 100)),
            width=WIDTH,
            height=HEIGHT,
            speed=speed,
            level=level
        )

        e2 = EnemyClass(
            pos=(WIDTH - 60, random.randint(100, HEIGHT - 100)),
            width=WIDTH,
            height=HEIGHT,
            speed=speed,
            level=level
        )

        groups["enemies"].add(e1, e2)
        groups["all_sprites"].add(e1, e2)

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
