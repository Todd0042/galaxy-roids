import pygame
import math
import random

from settings import (
    BOSS_HEALTH_BASE, BOSS_SPEED_BASE, BOSS_SPEED_SCALE,
    BOSS_LASER_COOLDOWN, BOSS_LASER_DURATION, BOSS_LASER_WARNING,
    RED, WHITE
)
from entities.projectiles import Bullet, GravityBomb


class Boss(pygame.sprite.Sprite):
    """
    Boss 1 — Planet Breaker
    """
    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.max_health = BOSS_HEALTH_BASE * (1.5 ** (level - 1))
        self.health = self.max_health
        self.speed = speed

        self.image = pygame.Surface((150, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 150, 50), border_radius=15)
        pygame.draw.rect(self.image, WHITE, (20, 50, 30, 30))
        pygame.draw.rect(self.image, WHITE, (100, 50, 30, 30))
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(screen_w // 2, -100)
        self.target_y = 120

        self.fire_cooldown = 0
        self.fire_rate_max = max(15, 45 - (level * 2))

        self.laser_cooldown = BOSS_LASER_COOLDOWN
        self.laser_warning_timer = 0
        self.laser_active_timer = 0

        self.hit_flash = 0

    def update(self, **kwargs):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        ticks = pygame.time.get_ticks()

        # Entry movement
        if self.pos.y < self.target_y:
            self.pos.y += self.speed
        else:
            # Horizontal sway
            freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
            self.pos.x = self.screen_w // 2 + math.sin(ticks * freq) * (self.screen_w // 4)

            # Laser logic
            if self.laser_active_timer > 0:
                self.laser_active_timer -= 1
            elif self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active_timer = BOSS_LASER_DURATION
            elif self.laser_cooldown > 0:
                self.laser_cooldown -= 1
            else:
                self.laser_warning_timer = BOSS_LASER_WARNING
                self.laser_cooldown = BOSS_LASER_COOLDOWN

        self.rect.center = self.pos

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1


class Boss2(pygame.sprite.Sprite):
    """
    Boss 2 — Sector Guardian
    """
    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.max_health = (BOSS_HEALTH_BASE * (1.5 ** 2)) * (1.02 ** (level - 3))
        self.health = self.max_health
        self.speed = speed * 1.2

        self.image = pygame.Surface((180, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 0, 255), (0, 0, 180, 60), border_radius=20)
        pygame.draw.rect(self.image, WHITE, (40, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (80, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (120, 60, 20, 40))
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(screen_w // 2, -100)
        self.target_y = 150

        self.fire_cooldown = 0
        self.fire_rate_max = max(10, 30 - level)

        self.laser_cooldown = 400
        self.laser_warning_timer = 0
        self.laser_active_timer = 0

        self.bomb_cooldown = 180
        self.hit_flash = 0

    def update(self, **kwargs):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        ticks = pygame.time.get_ticks()

        if self.pos.y < self.target_y:
            self.pos.y += self.speed
        else:
            # Figure-eight movement
            self.pos.x = self.screen_w // 2 + math.sin(ticks * 0.0015) * (self.screen_w // 3)
            self.pos.y = self.target_y + math.cos(ticks * 0.003) * 50

            # Laser logic
            if self.laser_active_timer > 0:
                self.laser_active_timer -= 1
            elif self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active_timer = 180
            elif self.laser_cooldown > 0:
                self.laser_cooldown -= 1
            else:
                self.laser_warning_timer = 90
                self.laser_cooldown = 400

        self.rect.center = self.pos

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def try_fire_bomb(self, all_sprites, gravity_bombs):
        """Boss2-specific gravity bomb attack."""
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
            return

        dist = random.randint(200, 600)
        angle = random.randint(60, 120)
        bomb = GravityBomb(self.rect.center, angle, self.screen_w, self.screen_h, dist)

        gravity_bombs.add(bomb)
        all_sprites.add(bomb)

        self.bomb_cooldown = 180
