import pygame
import math
import random

from settings import (
    BULLET_SPEED, BULLET_LIFESPAN,
    SHRAPNEL_DAMAGE, RED
)

# ---------------------------------------------------------
#   Helper: forward vector is UP (0, -1)
# ---------------------------------------------------------
def forward_vector(angle):
    return pygame.Vector2(0, -1).rotate(angle)


# ==========================
#   NORMAL BULLET
# ==========================
class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        angle,
        screen_w,
        screen_h,
        color=(255, 255, 255),
        size=4,
        is_bomber_fragment=False
    ):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = forward_vector(angle) * BULLET_SPEED

        self.hitbox_radius = size * 0.5
        self.is_bomber_fragment = is_bomber_fragment

    def update(self, **kwargs):
        self.pos += self.vel
        self.rect.center = self.pos

        if (
            self.pos.x < 0 or
            self.pos.x > self.screen_w or
            self.pos.y < 0 or
            self.pos.y > self.screen_h
        ):
            self.kill()


# ==========================
#   SHRAPNEL BULLET
# ==========================
class ShrapnelBullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (6, 6), 6)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = forward_vector(angle) * 6
        self.timer = 40
        self.exploded = False

        self.hitbox_radius = 6

    def update(self, **kwargs):
        self.pos += self.vel
        self.rect.center = self.pos

        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True

        if (
            self.pos.x < -50 or self.pos.x > self.screen_w + 50 or
            self.pos.y < -50 or self.pos.y > self.screen_h + 50
        ):
            self.kill()


# ==========================
#   GRAVITY BOMB
# ==========================
class GravityBomb(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h, target_dist):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = forward_vector(angle) * 4

        self.target_dist = target_dist
        self.dist_traveled = 0
        self.exploded = False

        self.hitbox_radius = 14

    def update(self, **kwargs):
        self.pos += self.vel
        self.dist_traveled += self.vel.length()
        self.rect.center = self.pos

        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks * 0.01) + 1) * 4

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (100, 0, 150), (20, 20), 14 + pulse, 3)
        pygame.draw.circle(self.image, (30, 0, 50), (20, 20), 10)

        if self.dist_traveled >= self.target_dist:
            self.exploded = True

        if not (0 <= self.pos.x <= self.screen_w and 0 <= self.pos.y <= self.screen_h):
            self.kill()


# ==========================
#   LASER BEAM
# ==========================
class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, pos, direction, screen_w, screen_h):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((6, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 255), (0, 0, 6, 40))
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(direction) * 25

        self.hitbox_radius = 3

    def update(self, **kwargs):
        self.pos += self.vel
        self.rect.center = self.pos

        if (
            self.pos.x < 0 or
            self.pos.x > self.screen_w or
            self.pos.y < 0 or
            self.pos.y > self.screen_h
        ):
            self.kill()


# ==========================
#   HOMING MISSILE
# ==========================
class HomingMissile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, screen_w, screen_h, groups, launch_frames=18):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 150, 50), (6, 6), 6)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(direction) * 8

        self.groups_ref = groups
        self.launch_timer = launch_frames
        self.target = None
        self.speed = 8

        self.hitbox_radius = 6

    def acquire_target(self):
        enemies = self.groups_ref["enemies"]
        if not enemies:
            return None

        closest = None
        closest_dist = 999999

        for e in enemies:
            d = self.pos.distance_to(e.pos)
            if d < closest_dist:
                closest = e
                closest_dist = d

        return closest

    def update(self, **kwargs):
        # Phase 1 — straight launch
        if self.launch_timer > 0:
            self.launch_timer -= 1
            self.pos += self.vel
            self.rect.center = self.pos
            return

        # Phase 2 — acquire target
        if self.target is None or not self.target.alive():
            self.target = self.acquire_target()
            if self.target is None:
                self.pos += self.vel
                self.rect.center = self.pos
                return

        # Phase 3 — homing dash
        direction = (self.target.pos - self.pos).normalize()
        self.speed = min(self.speed + 0.5, 20)
        self.vel = direction * self.speed

        self.pos += self.vel
        self.rect.center = self.pos

        if (
            self.pos.x < 0 or
            self.pos.x > self.screen_w or
            self.pos.y < 0 or
            self.pos.y > self.screen_h
        ):
            self.kill()
