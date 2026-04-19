import pygame
import random

class SplatterParticle(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (3, 3), 3)

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

        # Random outward velocity
        angle = random.uniform(0, 360)
        speed = random.uniform(2, 6)
        self.vel = pygame.Vector2(speed, 0).rotate(angle)

        self.alpha = 255
        self.decay = random.randint(4, 10)

    def update(self, **kwargs):
        self.pos += self.vel
        self.rect.center = self.pos

        # Fade out
        self.alpha -= self.decay
        if self.alpha <= 0:
            self.kill()
            return

        self.image.set_alpha(self.alpha)
