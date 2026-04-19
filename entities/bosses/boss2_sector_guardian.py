import pygame
import math
import random
from settings import (
    BOSS_HEALTH_BASE, BOSS_SPEED_BASE, WHITE
)
from entities.projectiles import GravityBomb
from .base_boss import BaseBoss

class Boss2(BaseBoss):
    """
    Boss 2 — Sector Guardian
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed * 1.2)

        self.max_health = (BOSS_HEALTH_BASE * 1.4) * (1.25 ** (level - 1))
        self.health = self.max_health

        self.image = pygame.Surface((180, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 0, 255), (0, 0, 180, 60), border_radius=20)
        pygame.draw.rect(self.image, WHITE, (40, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (80, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (120, 60, 20, 40))
        self.rect = self.image.get_rect()

        self.target_y = 150
        self.bomb_cooldown = 180

    def update_movement(self):
        ticks = pygame.time.get_ticks()
        self.pos.x = self.screen_w // 2 + math.sin(ticks * 0.0015) * (self.screen_w // 3)
        self.pos.y = self.target_y + math.cos(ticks * 0.003) * 50

    def update_attacks(self):
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
            return

        # Fire gravity bomb
        dist = random.randint(200, 600)
        angle = random.randint(60, 120)
        bomb = GravityBomb(self.rect.center, angle, self.screen_w, self.screen_h, dist)

        # Add to groups
        if "all_sprites" in self.groups():
            self.groups()["all_sprites"].add(bomb)
        if "gravity_bombs" in self.groups():
            self.groups()["gravity_bombs"].add(bomb)

        self.bomb_cooldown = 180
