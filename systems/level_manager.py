import random
import pygame

# Correct modular enemy imports
from entities.enemies.regular_enemy import RegularEnemy
from entities.enemies.blob_enemy import BlobEnemy
from entities.enemies.bomber_enemy import BomberEnemy
from entities.enemies.stinger_enemy import StingerEnemy

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
                debugger=None, state=None):
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

    if debugger:
        debugger.add_log(f"[LEVEL {level}] Spawned {enemies_per_side * 2} enemies")

    # ==========================
    #   LEVEL MUSIC (FADE-IN)
    # ==========================
    if state and "sfx" in state:
        sfx = state["sfx"]

        # Reset boss music fade flag for this level
        state["boss_music_started"] = False

        # Choose track based on level number
        track = f"assets/music/level{level}.ogg"

        # ⭐ MUSIC: fade in level theme
        if sfx.get("play_music"):
            try:
                sfx["play_music"](track, fade_ms=1200)
                if debugger:
                    debugger.add_log(f"[LEVEL {level}] Music: {track}")
            except Exception as e:
                if debugger:
                    debugger.add_log(f"Music load failed: {e}")

    if debugger:
        debugger.add_log(f"Level {level} initialized successfully")
