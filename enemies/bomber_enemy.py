import pygame
import math
import random
from .base_enemy import BaseEnemy

# Bomber constants
BOMBER_CHARGE_TIME = 400        # ms before dash (glow-up)
BOMBER_DASH_SPEED = 9.0         # very fast
BOMBER_EXPLOSION_RADIUS = 60
BOMBER_DAMAGE = 25


class BomberEnemy(BaseEnemy):
    def __init__(self, pos, width, height, speed=2.0, level=1):
        super().__init__(pos, width, height, speed, level)
        self.type = "BOMBER"

        # Bomber states
        self.state = "CHARGING"  # CHARGING → DASHING → EXPLODING
        self.charge_start = pygame.time.get_ticks()

        # Target point (locked at dash start)
        self.locked_target = pygame.Vector2(pos)

        # Explosion animation timer
        self.explode_timer = 0
        self.explode_duration = 300  # ms

        # Disable wings for bombers
        self.wing_speed = 999999

    # -----------------------------------------------------------
    #   VISUAL OVERRIDES — glowing bomber
    # -----------------------------------------------------------
    def draw_body(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)

        # Glow pulse
        t = pygame.time.get_ticks() * 0.006
        glow = int(120 + math.sin(t) * 80)

        # Core body
        pygame.draw.circle(surf, (255, 80, 40), (24, 24), 14)

        # Glow aura
        pygame.draw.circle(surf, (255, 120, 80, glow), (24, 24), 20)

        return surf

    def draw_wings(self, open_state=True):
        """Bombers have no wings."""
        return pygame.Surface((48, 48), pygame.SRCALPHA)

    # -----------------------------------------------------------
    #   MOVEMENT LOGIC
    # -----------------------------------------------------------
    def movement_update(self, player_pos):
        now = pygame.time.get_ticks()

        # -------------------------------
        #   CHARGING (glow-up)
        # -------------------------------
        if self.state == "CHARGING":
            if now - self.charge_start >= BOMBER_CHARGE_TIME:
                self.state = "DASHING"
                # Lock onto player's position *once*
                if player_pos is not None:
                    self.locked_target = pygame.Vector2(player_pos)
            return

        # -------------------------------
        #   DASHING (no course correction)
        # -------------------------------
        if self.state == "DASHING":
            direction = (self.locked_target - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()

            self.pos += direction * BOMBER_DASH_SPEED

            # Check if bomber reached its target zone
            if self.pos.distance_to(self.locked_target) < 12:
                self.state = "EXPLODING"
                self.explode_timer = now
            return

        # -------------------------------
        #   EXPLODING (stationary)
        # -------------------------------
        if self.state == "EXPLODING":
            # Explosion handled in attack_update()
            return

    # -----------------------------------------------------------
    #   ATTACK LOGIC — explosion damage
    # -----------------------------------------------------------
    def attack_update(self, player_pos):
        if self.state != "EXPLODING":
            return

        now = pygame.time.get_ticks()

        # Explosion lasts briefly
        if now - self.explode_timer > self.explode_duration:
            self.kill()
            return

        # Explosion visual (handled in draw_body override if needed)
        # Damage is handled via collision_effect()

    # -----------------------------------------------------------
    #   COLLISION EFFECT — explosion damage
    # -----------------------------------------------------------
    def collision_effect(self, player):
        """
        Called when the bomber explodes near the player.
        The main loop should check distance and apply damage.
        """
        player.apply_explosion(BOMBER_DAMAGE)
