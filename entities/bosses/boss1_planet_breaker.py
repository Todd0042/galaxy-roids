import pygame
import math
from settings import (
    BOSS_HEALTH_BASE, BOSS_SPEED_BASE, BOSS_LASER_COOLDOWN,
    BOSS_LASER_DURATION, BOSS_LASER_WARNING, RED, WHITE
)
from .base_boss import BaseBoss

class Boss1(BaseBoss):
    """
    Boss 1 — Planet Breaker
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed)

        self.max_health = BOSS_HEALTH_BASE * (1.25 ** (level - 1))
        self.health = self.max_health

        self.image = pygame.Surface((150, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 150, 50), border_radius=15)
        pygame.draw.rect(self.image, WHITE, (20, 50, 30, 30))
        pygame.draw.rect(self.image, WHITE, (100, 50, 30, 30))
        self.rect = self.image.get_rect()

        self.fire_rate_max = max(15, 45 - (level * 2))
        self.laser_cooldown = BOSS_LASER_COOLDOWN

    def update_movement(self):
        ticks = pygame.time.get_ticks()
        freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
        self.pos.x = self.screen_w // 2 + math.sin(ticks * freq) * (self.screen_w // 4)

    def update_attacks(self):
        # Laser logic
        if self.laser_active_timer > 0:
            return
        if self.laser_warning_timer > 0:
            return
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
            return

        self.laser_warning_timer = BOSS_LASER_WARNING
        self.laser_cooldown = BOSS_LASER_COOLDOWN
