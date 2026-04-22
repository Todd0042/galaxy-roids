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
PLAYER_MAX_HEALTH = 100
INITIAL_LIVES = 15
PLAYER_SCALE = 0.25
PLAYER_HITBOX_RADIUS = 4.5
PLAYER_INVULN_TIME = 60
PLAYER_STUN_TIME = 10
PLAYER_SIZE = 30

# Movement
PLAYER_ROT_SPEED = 5
PLAYER_THRUST = 0.2
PLAYER_FRICTION = 0.98
PLAYER_REVERSE_THRUST = 0.03
PLAYER_BRAKE_FRICTION = 0.95
# Rotation speed (degrees per frame)
PLAYER_ROT_SPEED = 4

# --- Combat ---
PLAYER_FIRE_RATE = 10
PLAYER_COLLISION_DAMAGE = 5
SHRAPNEL_COOLDOWN_MAX = 120
SPREAD_HITS_REVERT = 1
# ==========================
#   PLAYER WEAPON TIMING
# ==========================

LASER_FIRE_COOLDOWN = 10        # frames between laser shots
HOMING_FIRE_COOLDOWN = 20      # frames between missile shots


# Rapid-fire toggle
ENABLE_RAPID_FIRE = True
RAPID_FIRE_COOLDOWN = 20
RAPID_FIRE_REQUIRED_POWERUPS = 2

# Status Effects
BLOB_STUN_TIME = 30  # frames

# ==========================
#   DAMAGE VALUES
# ==========================
HAZARD_DAMAGE = 5
BLOB_DAMAGE = 5
BOMBER_DAMAGE = 3
BOSS_DAMAGE = 15
BULLET_DAMAGE = 1
SHRAPNEL_DAMAGE = 10

# ==========================
#   ENEMY SETTINGS
# ==========================
ENEMY_SIZE = 25
ENEMY_HEALTH = 3
ENEMY_SPEED = 3 * DIFFICULTY_MULTIPLIER
ENEMY_DIVE_CHANCE = 0.04 * DIFFICULTY_MULTIPLIER

# ==========================
#   BOSS SETTINGS
# ==========================
ENEMY_WAVE_DELAY = 10
BOSS_SPAWN_TIME = 60000  ## IMPORTANT!! Bott Time in stage!!

BOSS_SPEED_BASE = 1.5 * DIFFICULTY_MULTIPLIER
BOSS_SPEED_SCALE = 1.15

# Laser
BOSS_LASER_COOLDOWN = 600
BOSS_LASER_DURATION = 180
BOSS_LASER_WARNING = 90

# ============================
#   BOSS HEALTH SETTINGS
# ============================
BOSS_HEALTH_BASE = 350 * DIFFICULTY_MULTIPLIER
MAX_BOSS_HEALTH = 2000   # hard cap for all bosses


# ==========================
#   PROJECTILES & HAZARDS
# ==========================
BULLET_SPEED = 10
BULLET_LIFESPAN = 1500

# ==========================
#   VENOM ORB & HAZARD POOL
# ==========================

# Venom Orb physics
VENOM_ORB_GRAVITY = 0.18
VENOM_ORB_BOUNCE_FACTOR = -0.45
VENOM_ORB_SPREAD = ( -0.6, 0, 0.6 )   # firing angles
VENOM_ORB_SPEED_X = 2.0
VENOM_ORB_SPEED_Y = 1.5

# Hazard Pool visuals & lifetime
HAZARD_POOL_DURATION = 240          # frames (~4 seconds)
HAZARD_POOL_BASE_WIDTH = 90
HAZARD_POOL_BASE_HEIGHT = 32
HAZARD_POOL_PULSE_SPEED = 0.01      # pulsing animation speed

# Hazard Pool gameplay effects
HAZARD_DAMAGE = 2                   # DOT damage per tick
HAZARD_DOT_INTERVAL = 12            # frames between DOT ticks (~0.2s)
HAZARD_SLOW_MULT = 0.5              # speed while inside pool
HAZARD_LINGER_MULT = 0.7            # speed after leaving
HAZARD_LINGER_TIME = 60             # frames (1 second)

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
POWERUP_SPAWN_CHANCE = 0.01
