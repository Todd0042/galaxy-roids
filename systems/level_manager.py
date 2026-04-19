import random
import pygame

# NEW modular enemy system
from enemies.regular_enemy import RegularEnemy
from enemies.blob_enemy import BlobEnemy
from enemies.bomber_enemy import BomberEnemy
from enemies.stinger_enemy import StingerEnemy

# Asteroids still live in entities/
from entities.asteroid import Asteroid

from settings import (
    ASTEROID_START_COUNT,
    ASTEROID_SCALING,
    ASTEROID_MAX_COUNT
)


def start_level(level, width, height,
                all_sprites, enemies, asteroids,
                enemy_speed, enemies_per_side,
                debugger=None):
    """
    Spawns enemies + asteroids for the given level.
    Called at game start AND after each boss is defeated.
    """

    # ==========================
    #   CLEAN UP OLD ENTITIES
    # ==========================
    for e in enemies.copy():
        e.kill()
    for a in asteroids.copy():
        a.kill()

    enemies.empty()
    asteroids.empty()

    # ==========================
    #       ASTEROID FIELD
    # ==========================
    # Base + scaling, but capped
    asteroid_count = ASTEROID_START_COUNT + (level - 1) * ASTEROID_SCALING
    asteroid_count = min(asteroid_count, ASTEROID_MAX_COUNT)

    for _ in range(asteroid_count):
        a = Asteroid(width, height)
        asteroids.add(a)
        all_sprites.add(a)

    if debugger:
        debugger.add_log(f"[LEVEL {level}] Spawned {asteroid_count} asteroids")

    # ==========================
    #       ENEMY FORMATION
    # ==========================
    # Mix of bug enemies + glob enemies
    for _ in range(enemies_per_side):

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

        # Pick a random enemy type
        EnemyClass = random.choice(enemy_pool)

        # LEFT SIDE spawn
        e1 = EnemyClass(
            pos=(60, random.randint(100, height - 100)),
            width=width,
            height=height,
            speed=enemy_speed,
            level=level
        )

        # RIGHT SIDE spawn
        e2 = EnemyClass(
            pos=(width - 60, random.randint(100, height - 100)),
            width=width,
            height=height,
            speed=enemy_speed,
            level=level
        )

        enemies.add(e1, e2)
        all_sprites.add(e1, e2)



        # RIGHT SIDE
        enemy_pool = []

        if level >= 1:
            enemy_pool.append(RegularEnemy)

        if level >= 4:
            enemy_pool.append(BlobEnemy)

        if level >= 7:
            enemy_pool.append(BomberEnemy)

        if level >= 10:
            enemy_pool.append(StingerEnemy)

        EnemyClass = random.choice(enemy_pool)

        e2 = EnemyClass(
            pos=(width - 60, random.randint(100, height - 100)),
            width=width,
            height=height,
            speed=enemy_speed,
            level=level
        )

        enemies.add(e2)
        all_sprites.add(e2)



    if debugger:
        debugger.add_log(f"[LEVEL {level}] Spawned {enemies_per_side * 2} enemies")

    # ==========================
    #       LEVEL MUSIC
    # ==========================
    try:
        from systems.audio import play_music
        track = f"level{((level - 1) % 5) + 1}.midi"
        play_music(track)
        if debugger:
            debugger.add_log(f"[LEVEL {level}] Music: {track}")
    except Exception as e:
        if debugger:
            debugger.add_log(f"Music load failed: {e}")

    if debugger:
        debugger.add_log(f"Level {level} initialized successfully")
