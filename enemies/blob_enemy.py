import pygame
import math
import random
from .base_enemy import BaseEnemy

# Blob constants (tweak as needed)
BLOB_TRAP_TIME = 500       # milliseconds player is trapped
BLOB_DAMAGE = 5            # tiny damage
BLOB_WOBBLE_AMOUNT = 2.5   # how much the blob jiggles
BLOB_SPEED_MULT = 0.55     # blobs are slow


class BlobEnemy(BaseEnemy):
    def __init__(self, pos, width, height, speed=1.2, level=1):
        super().__init__(pos, width, height, speed, level)
        self.type = "BLOB"

        # Blobs don't flap wings — disable animation if you want
        self.wing_speed = 999999  # effectively stops wing animation

        # Internal wobble timer
        self.wobble_offset = random.uniform(0, 1000)

    # -----------------------------------------------------------
    #   VISUAL OVERRIDES — gooey blob
    # -----------------------------------------------------------
    def draw_body(self):
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)

        # Main goo blob
        pygame.draw.ellipse(surf, (120, 255, 120, 180), (6, 10, 36, 30))

        # Highlight
        pygame.draw.ellipse(surf, (200, 255, 200, 120), (14, 14, 16, 12))

        # Slight outline pulse
        pulse = (math.sin(pygame.time.get_ticks() * 0.004) + 1) * 0.5
        outline_color = (80, 200, 80, int(120 + pulse * 80))
        pygame.draw.ellipse(surf, outline_color, (6, 10, 36, 30), 2)

        return surf

    def draw_wings(self, open_state=True):
        """Blobs have no wings — return empty surface."""
        return pygame.Surface((48, 48), pygame.SRCALPHA)

    # -----------------------------------------------------------
    #   MOVEMENT — slow drift + wobble
    # -----------------------------------------------------------
    def movement_update(self, player_pos):
        if player_pos is None:
            return

        # Slow drift toward player
        direction = (player_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * BLOB_SPEED_MULT

        # Goo wobble
        t = pygame.time.get_ticks() * 0.003 + self.wobble_offset
        self.pos.x += math.sin(t) * BLOB_WOBBLE_AMOUNT
        self.pos.y += math.cos(t * 0.7) * (BLOB_WOBBLE_AMOUNT * 0.6)

    # -----------------------------------------------------------
    #   ATTACK — blobs do not shoot or dive
    # -----------------------------------------------------------
    def attack_update(self, player_pos):
        pass

    # -----------------------------------------------------------
    #   COLLISION EFFECT — trap + tiny damage
    # -----------------------------------------------------------
    def collision_effect(self, player):
        """
        Called when the blob touches the player.
        The main loop should:
            - apply BLOB_DAMAGE
            - freeze player movement for BLOB_TRAP_TIME ms
        """
        player.apply_trap(BLOB_TRAP_TIME, BLOB_DAMAGE)
