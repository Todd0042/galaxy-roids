import pygame
import random
from settings import CYAN


class Powerup(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, CYAN, (10, 10), 10)
        pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 5)
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(
            random.randint(50, screen_w - 50),
            random.randint(50, screen_h - 50)
        )
        self.rect.center = self.pos

        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self, **kwargs):
        self.pos += self.vel
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos
