import random
import pygame

from settings import (
    POWERUP_SPAWN_CHANCE,
    BOSS_SPAWN_TIME,
)

from entities.powerups import Powerup
from entities.asteroid import Asteroid
from entities.boss import Boss, Boss2

# Enemy classes
from enemies.regular_enemy import RegularEnemy
from enemies.blob_enemy import BlobEnemy
from enemies.bomber_enemy import BomberEnemy
from enemies.stinger_enemy import StingerEnemy


# ==========================
#     RANDOM POWERUPS
# ==========================

def spawn_random_powerups(state, groups):
    if not state["game_active"]:
        return

    if random.random() < POWERUP_SPAWN_CHANCE:
        WIDTH = state["WIDTH"]
        HEIGHT = state["HEIGHT"]

        p = Powerup(WIDTH, HEIGHT)
        groups["powerups"].add(p)
        groups["all_sprites"].add(p)


# ==========================
#        BOSS SPAWN
# ==========================

def spawn_boss_if_ready(state, groups, play_music):
    """
    Spawns the boss once the timer passes BOSS_SPAWN_TIME.
    """

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

    # Choose boss type
    if 4 <= level <= 6:
        boss = Boss2(WIDTH, HEIGHT, level, speed=speed)
    else:
        boss = Boss(WIDTH, HEIGHT, level, speed=speed)

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

    # Build enemy pool based on level
    enemy_pool = []

    if level >= 1:
        enemy_pool.append(RegularEnemy)
    if level >= 4:
        enemy_pool.append(BlobEnemy)
    if level >= 7:
        enemy_pool.append(BomberEnemy)
    if level >= 10:
        enemy_pool.append(StingerEnemy)

    # Spawn 5 pairs (left + right)
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

    # Every ~7 seconds (ticks % 7000 < 20)
    if ticks % 7000 < 20:
        WIDTH = state["WIDTH"]
        HEIGHT = state["HEIGHT"]

        for _ in range(3):
            a = Asteroid(WIDTH, HEIGHT)
            groups["asteroids"].add(a)
            groups["all_sprites"].add(a)
