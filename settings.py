import pygame
import random
import math

# ==========================
#   CORE GAME SETTINGS
# ==========================
FPS = 60
DEBUG_MODE_DEFAULT = True
DIFFICULTY_MULTIPLIER = 0.3

# ==========================
#   COLORS
# ==========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GOLDEN_YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)

# ==========================
#   PLAYER SETTINGS
# ==========================
PLAYER_SIZE = 30
PLAYER_MAX_HEALTH = 100
INITIAL_LIVES = 15

# Movement
PLAYER_ROT_SPEED = 5
PLAYER_THRUST = 0.2
PLAYER_FRICTION = 0.98
PLAYER_REVERSE_THRUST = 0.03
PLAYER_BRAKE_FRICTION = 0.95

# --- Combat ---
PLAYER_FIRE_RATE = 10
PLAYER_COLLISION_DAMAGE = 5
SHRAPNEL_COOLDOWN_MAX = 120
SPREAD_HITS_REVERT = 1

# Rapid-fire toggle
ENABLE_RAPID_FIRE = True
RAPID_FIRE_REQUIRED_POWERUPS = 2

# Status Effects
BLOB_STUN_TIME = 30  # frames

# ==========================
#   DAMAGE VALUES
# ==========================
HAZARD_DAMAGE = 5
BLOB_DAMAGE = 5
BOMBER_DAMAGE = 3
BOSS_DAMAGE = 30
BULLET_DAMAGE = 1
SHRAPNEL_DAMAGE = 10

# ==========================
#   ENEMY SETTINGS
# ==========================
ENEMY_SIZE = 25
ENEMY_HEALTH = 1
ENEMY_SPEED = 3 * DIFFICULTY_MULTIPLIER
ENEMY_DIVE_CHANCE = 0.04 * DIFFICULTY_MULTIPLIER

# ==========================
#   BOSS SETTINGS
# ==========================
ENEMY_WAVE_DELAY = 10
BOSS_SPAWN_TIME = 5000

BOSS_HEALTH_BASE = 60 * DIFFICULTY_MULTIPLIER
BOSS_SPEED_BASE = 0.8 * DIFFICULTY_MULTIPLIER
BOSS_SPEED_SCALE = 1.15

# Laser
BOSS_LASER_COOLDOWN = 600
BOSS_LASER_DURATION = 180
BOSS_LASER_WARNING = 90

# ==========================
#   PROJECTILES & HAZARDS
# ==========================
BULLET_SPEED = 10
BULLET_LIFESPAN = 500

# ==========================
#   ASTEROIDS
# ==========================
ASTEROID_START_COUNT = 2
ASTEROID_SCALING = 1
ASTEROID_MAX_COUNT = 8
ASTEROID_SPEED_RANGE = (-1.5, 1.5)

ASTEROID_HEALTH_LARGE = 3
ASTEROID_HEALTH_MEDIUM = 2
ASTEROID_HEALTH_SMALL = 1

# ==========================
#   POWERUPS
# ==========================
POWERUP_SPAWN_CHANCE = 0.005
