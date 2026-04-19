#!/usr/bin/env python3
import os
import sys
import importlib
import pygame

print("=== GalaxyRoids Sanity Check ===")

# -----------------------------------
# 1. Basic pygame + mixer test
# -----------------------------------
print("\n[1] Testing pygame initialization...")
try:
    pygame.init()
    pygame.mixer.init()
    print("✓ pygame + mixer initialized")
except Exception as e:
    print("✗ pygame failed:", e)


# -----------------------------------
# 2. Required package folders
# -----------------------------------
required_dirs = [
    "core",
    "systems",
    "entities",
    "entities/enemies",
    "collisions",
    "ui",
]

print("\n[2] Checking required directories...")
for d in required_dirs:
    if os.path.isdir(d):
        print(f"✓ {d}/ exists")
    else:
        print(f"✗ MISSING DIRECTORY: {d}/")


# -----------------------------------
# 3. Required __init__.py files
# -----------------------------------
print("\n[3] Checking __init__.py files...")
for d in required_dirs:
    init_path = os.path.join(d, "__init__.py")
    if os.path.isfile(init_path):
        print(f"✓ {init_path}")
    else:
        print(f"✗ MISSING: {init_path}")


# -----------------------------------
# 4. Module import test
# -----------------------------------
modules = [
    "core.game_init",
    "core.renderer",
    "core.combat",
    "core.collision_manager",
    "core.level_flow",
    "core.player_state",
    "core.spawner",
    "core.updater",
    "core.input_handler",
    "systems.audio",
    "systems.debugger",
    "systems.level_manager",
    "entities.player",
    "entities.asteroid",
    "entities.boss",
    "entities.powerups",
    "entities.projectiles",
    "entities.enemies.base_enemy",
    "entities.enemies.regular_enemy",
    "entities.enemies.blob_enemy",
    "entities.enemies.bomber_enemy",
    "entities.enemies.stinger_enemy",
    "collisions.collision_boss",
    "collisions.collision_misc",
    "collisions.collision_enemy_player",
    "collisions.collision_player_enemy",
    "ui.hud",
    "ui.countdown",
    "ui.level_select",
    "ui.popups",
    "ui.game_over",
]

print("\n[4] Importing modules...")
for m in modules:
    try:
        importlib.import_module(m)
        print(f"✓ {m}")
    except Exception as e:
        print(f"✗ FAILED: {m} — {e}")


# -----------------------------------
# 5. Check audio API
# -----------------------------------
print("\n[5] Checking audio API...")
try:
    audio = importlib.import_module("systems.audio")
    if hasattr(audio, "load_sounds") and hasattr(audio, "play_music"):
        print("✓ load_sounds() and play_music() found")
    else:
        print("✗ audio.py missing required functions")
except Exception as e:
    print("✗ audio import failed:", e)


# -----------------------------------
# 6. Check initialize_game()
# -----------------------------------
print("\n[6] Checking initialize_game()...")
try:
    gi = importlib.import_module("core.game_init")
    if hasattr(gi, "initialize_game"):
        print("✓ initialize_game() found")
    else:
        print("✗ initialize_game() missing")
except Exception as e:
    print("✗ game_init import failed:", e)


print("\n=== Sanity Check Complete ===")
