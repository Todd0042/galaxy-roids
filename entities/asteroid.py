import pygame
import random

from settings import (
    ASTEROID_HEALTH_LARGE, ASTEROID_HEALTH_MEDIUM, ASTEROID_HEALTH_SMALL,
    ASTEROID_SPEED_RANGE, WHITE
)
from entities.projectiles import Bullet


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h, pos=None, size=3):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h
        self.size = size

        self.has_turret = False
        self.fire_cooldown = 0

        radius = self.size * 15
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        if size == 3:
            self.health = ASTEROID_HEALTH_LARGE
        elif size == 2:
            self.health = ASTEROID_HEALTH_MEDIUM
        else:
            self.health = ASTEROID_HEALTH_SMALL

        pygame.draw.circle(self.image, WHITE, (radius, radius), radius, 2)
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(pos) if pos else pygame.Vector2(
            random.randint(0, screen_w),
            random.randint(0, screen_h)
        )
        self.rect.center = self.pos

        vmin, vmax = ASTEROID_SPEED_RANGE
        self.vel = pygame.Vector2(random.uniform(vmin, vmax),
                                  random.uniform(vmin, vmax))

    def update(self, **kwargs):
        player_pos = kwargs.get("player_pos")
        boss_bullets = kwargs.get("boss_bullets")
        all_sprites = kwargs.get("all_sprites")

        self.pos += self.vel
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos

        if self.has_turret and player_pos and boss_bullets:
            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1
            else:
                angle = (player_pos - self.pos).angle_to(pygame.Vector2(1, 0))
                shot = Bullet(self.rect.center, -angle, self.screen_w, self.screen_h, color=(255, 50, 50), size=8)
                shot.vel *= 0.4
                boss_bullets.add(shot)
                if all_sprites:
                    all_sprites.add(shot)
                self.fire_cooldown = 180
