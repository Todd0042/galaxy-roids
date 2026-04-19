import pygame
import math
import random
from .base_enemy import BaseEnemy

# Stinger constants
STINGER_DASH_SPEED = 8.5
STINGER_CIRCLE_SPEED = 3.0
STINGER_CIRCLE_RADIUS = 90
STINGER_RECOVERY_TIME = 350   # ms after overshoot
STINGER_DAMAGE = 20


class StingerEnemy(BaseEnemy):
    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__(pos, width, height, speed, level)
        self.type = "STINGER"

        # Stinger states
        self.state = "CIRCLING"  # CIRCLING → DASHING → RECOVERY → CIRCLING
        self.circle_angle = random.uniform(0, math.tau)
        self.recovery_start = 0

        # Target point for dash
        self.dash_target = pygame.Vector2(pos)

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
    #   MOVEMENT LOGIC — dash loop behavior
    # -----------------------------------------------------------
    def movement_update(self, player_pos):
        now = pygame.time.get_ticks()

        # -------------------------------
        #   CIRCLING (prep for next dash)
        # -------------------------------
        if self.state == "CIRCLING":
            if player_pos is None:
                return

            # Orbit around player
            self.circle_angle += 0.04
            offset = pygame.Vector2(
                math.cos(self.circle_angle),
                math.sin(self.circle_angle)
            ) * STINGER_CIRCLE_RADIUS

            self.pos = player_pos + offset

            # ⭐ WRAP during circling
            self.pos.x %= self.width
            self.pos.y %= self.height

            # Randomly decide to dash
            if random.random() < 0.02:
                self.state = "DASHING"
                self.dash_target = pygame.Vector2(player_pos)  # last known position
            return

        # -------------------------------
        #   DASHING (straight-line attack)
        # -------------------------------
        if self.state == "DASHING":
            direction = (self.dash_target - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()

            self.pos += direction * STINGER_DASH_SPEED

            # ⭐ WRAP during dash
            self.pos.x %= self.width
            self.pos.y %= self.height

            # Overshoot check
            if self.pos.distance_to(self.dash_target) < 12:
                self.state = "RECOVERY"
                self.recovery_start = now
            return

        # -------------------------------
        #   RECOVERY (curve back around)
        # -------------------------------
        if self.state == "RECOVERY":
            # ⭐ WRAP during recovery
            self.pos.x %= self.width
            self.pos.y %= self.height

            if now - self.recovery_start > STINGER_RECOVERY_TIME:
                self.state = "CIRCLING"
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
        """
        Called when the stinger hits the player during a dash.
        """
        player.apply_damage(STINGER_DAMAGE)
