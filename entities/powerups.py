import pygame
import random
from settings import CYAN


class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Store screen size later via update kwargs
        self.screen_w = None
        self.screen_h = None

        # Visual
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, CYAN, (10, 10), 10)
        pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 5)
        self.rect = self.image.get_rect(center=(x, y))

        # Position + velocity
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self, **kwargs):
        # Screen size is passed in by your main loop
        if "WIDTH" in kwargs:
            self.screen_w = kwargs["WIDTH"]
        if "HEIGHT" in kwargs:
            self.screen_h = kwargs["HEIGHT"]

        # Move
        self.pos += self.vel

        # Wrap (only if screen size is known)
        if self.screen_w and self.screen_h:
            self.pos.x %= self.screen_w
            self.pos.y %= self.screen_h

        self.rect.center = self.pos

    # ⭐ STACKING POWERUPS
    def apply(self, player):
        player.powerup_hits += 1

        # Always use spread shot once ANY powerup is collected
        if player.powerup_hits >= 1:
            player.weapon_mode = "SPREAD"
            player.update_appearance()

        # Laser unlocks at 4
        if player.powerup_hits >= 4:
            player.has_laser = True

        # Homing missiles unlock at 5 and 6
        if player.powerup_hits >= 5:
            player.homing_count = min(player.powerup_hits - 4, 2)  # 1 or 2 missiles
