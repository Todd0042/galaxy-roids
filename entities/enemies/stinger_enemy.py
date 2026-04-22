import pygame
import math
import random
import os
import sys
from .base_enemy import BaseEnemy

# ============================================================
#   RESOURCE PATH (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


# Stinger constants
STINGER_DASH_SPEED = 8.5
STINGER_ROAM_SPEED = 2.2
STINGER_RECOVERY_TIME = 350   # ms after overshoot
STINGER_DAMAGE = 20


class StingerEnemy(BaseEnemy):
    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__(pos, width, height, speed, level)
        self.type = "STINGER"
        self.contact_damage = 5

        # ⭐ NEW: freeze movement for 2 seconds after spawning
        self.spawn_delay = 2000  # ms
        self.last_update_time = pygame.time.get_ticks()

        # Stinger states
        self.state = "ROAMING"  # ROAMING → DASHING → RECOVERY → ROAMING
        self.recovery_start = 0

        # Dash target
        self.dash_target = pygame.Vector2(pos)

        # ⭐ Random roaming direction
        angle = random.uniform(0, math.tau)
        self.roam_dir = pygame.Vector2(math.cos(angle), math.sin(angle))

        # Faster wing animation (optional)
        self.wing_speed = 60

    # -----------------------------------------------------------
    #   VISUAL OVERRIDES — sleek, sharp stinger
    # -----------------------------------------------------------
    def draw_body(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)

        # Sharp, needle-like body
        pygame.draw.polygon(
            surf,
            (200, 40, 40),
            [(24, 6), (16, 24), (24, 42), (32, 24)]
        )

        # Highlight
        pygame.draw.polygon(
            surf,
            (255, 120, 120, 180),
            [(24, 10), (20, 24), (24, 38), (28, 24)]
        )

        return surf

    # -----------------------------------------------------------
    #   MOVEMENT LOGIC — roam → dash → recover
    # -----------------------------------------------------------
    def movement_update(self, player_pos):
        now = pygame.time.get_ticks()
        dt = now - self.last_update_time
        self.last_update_time = now

        # ⭐ NEW: freeze all movement for 2 seconds after spawning
        if self.spawn_delay > 0:
            self.spawn_delay -= dt
            return

        # -------------------------------
        #   ROAMING (random wandering)
        # -------------------------------
        if self.state == "ROAMING":
            # Move in current direction
            self.pos += self.roam_dir * STINGER_ROAM_SPEED

            # Wrap
            self.pos.x %= self.width
            self.pos.y %= self.height

            # Occasionally change direction
            if random.random() < 0.02:
                angle = random.uniform(0, math.tau)
                self.roam_dir = pygame.Vector2(math.cos(angle), math.sin(angle))

            # Occasionally dash at player
            if player_pos is not None and random.random() < 0.015:
                self.state = "DASHING"
                self.dash_target = pygame.Vector2(player_pos)
            return

        # -------------------------------
        #   DASHING (straight-line attack)
        # -------------------------------
        if self.state == "DASHING":
            direction = (self.dash_target - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()

            self.pos += direction * STINGER_DASH_SPEED

            # Wrap
            self.pos.x %= self.width
            self.pos.y %= self.height

            # Overshoot check
            if self.pos.distance_to(self.dash_target) < 12:
                self.state = "RECOVERY"
                self.recovery_start = now
            return

        # -------------------------------
        #   RECOVERY (pause after dash)
        # -------------------------------
        if self.state == "RECOVERY":
            if now - self.recovery_start > STINGER_RECOVERY_TIME:
                self.state = "ROAMING"
            return

    # -----------------------------------------------------------
    #   ATTACK LOGIC — stingers don't shoot
    # -----------------------------------------------------------
    def attack_update(self, player_pos):
        pass

    # -----------------------------------------------------------
    #   COLLISION EFFECT — high dash damage
    # -----------------------------------------------------------
    def collision_effect(self, player):
        player.apply_damage(STINGER_DAMAGE)
