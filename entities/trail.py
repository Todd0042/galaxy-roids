import pygame
import random

class TrailSegment(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.lifetime = 20  # frames
        self.alpha = 255

        # Small glowing dot
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 200, 255, self.alpha), (2, 2), 2)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        # Fade out
        self.alpha = int(255 * (self.lifetime / 20))
        self.image.set_alpha(self.alpha)
