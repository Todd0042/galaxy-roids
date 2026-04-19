import pygame
import math
import random

from settings import (
    BULLET_SPEED, BULLET_LIFESPAN,
    SHRAPNEL_DAMAGE, RED
)


# ============================================================
#   BASE BULLET
# ============================================================
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

        # Initial bounds (dynamic override happens in update)
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(BULLET_SPEED, 0).rotate(angle)

        self.is_bomber_fragment = is_bomber_fragment

    def update(self, **kwargs):
        # Dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.pos += self.vel
        self.rect.center = self.pos

        # Despawn when leaving screen
        if (
            self.pos.x < 0 or
            self.pos.x > self.screen_w or
            self.pos.y < 0 or
            self.pos.y > self.screen_h
        ):
            self.kill()


# ============================================================
#   SHRAPNEL BULLET
# ============================================================
class ShrapnelBullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (6, 6), 6)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(6, 0).rotate(angle)
        self.timer = 40
        self.exploded = False

    def update(self, **kwargs):
        # Dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.pos += self.vel
        self.rect.center = self.pos

        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True

        # Despawn when far outside screen
        if (
            self.pos.x < -50 or
            self.pos.x > self.screen_w + 50 or
            self.pos.y < -50 or
            self.pos.y > self.screen_h + 50
        ):
            self.kill()


# ============================================================
#   GRAVITY BOMB
# ============================================================
class GravityBomb(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h, target_dist):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(4, 0).rotate(angle)

        self.target_dist = target_dist
        self.dist_traveled = 0
        self.exploded = False

    def update(self, **kwargs):
        # Dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

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


# ============================================================
#   LASER BEAM
# ============================================================
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

    def update(self, **kwargs):
        # Dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.pos += self.vel
        self.rect.center = self.pos

        if (
            self.pos.x < 0 or
            self.pos.x > self.screen_w or
            self.pos.y < 0 or
            self.pos.y > self.screen_h
        ):
            self.kill()


# ============================================================
#   HOMING MISSILE
# ============================================================
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
        # Dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

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


# ============================================================
#   EXPLOSION HELPERS
# ============================================================
def spawn_shrapnel_explosion(center, all_sprites=None, group=None):
    if group is None:
        return

    for i in range(12):
        angle = i * 30
        frag = Bullet(
            center,
            angle,
            9999,  # dynamic override in update()
            9999,
            color=(255, 200, 0),
            size=4,
            is_bomber_fragment=True
        )
        frag.vel *= 0.6
        group.add(frag)
        if all_sprites:
            all_sprites.add(frag)


def spawn_gravity_explosion(center, all_sprites=None, group=None):
    if group is None:
        return

    for i in range(20):
        angle = i * 18
        frag = Bullet(
            center,
            angle,
            9999,  # dynamic override in update()
            9999,
            color=RED,
            size=6,
            is_bomber_fragment=True
        )
        frag.vel *= 0.4
        group.add(frag)
        if all_sprites:
            all_sprites.add(frag)
