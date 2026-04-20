import pygame
import math
import random
from settings import (
    VENOM_ORB_GRAVITY,
    VENOM_ORB_BOUNCE_FACTOR,
    HAZARD_POOL_DURATION,
    HAZARD_POOL_BASE_WIDTH,
    HAZARD_POOL_BASE_HEIGHT,
    HAZARD_POOL_PULSE_SPEED,
)

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

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(BULLET_SPEED, 0).rotate(angle)

        self.is_bomber_fragment = is_bomber_fragment

    def update(self, **kwargs):
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
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.pos += self.vel
        self.rect.center = self.pos

        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True

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
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        if self.launch_timer > 0:
            self.launch_timer -= 1
            self.pos += self.vel
            self.rect.center = self.pos
            return

        if self.target is None or not self.target.alive():
            self.target = self.acquire_target()
            if self.target is None:
                self.pos += self.vel
                self.rect.center = self.pos
                return

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
            9999,
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
            9999,
            9999,
            color=RED,
            size=6,
            is_bomber_fragment=True
        )
        frag.vel *= 0.4
        group.add(frag)
        if all_sprites:
            all_sprites.add(frag)
            
# ============================================================
#   VENOM ORB (Boss3)
# ============================================================
class VenomOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, screen_w, screen_h):
        super().__init__()

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (8, 8), 8)
        self.rect = self.image.get_rect(center=(x, y))

        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)

        self.gravity = VENOM_ORB_GRAVITY
        self.bounced = False

    def update(self, **kwargs):
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.vel.y += self.gravity
        self.pos += self.vel
        self.rect.center = self.pos

        ground = self.screen_h - 40

        if not self.bounced and self.pos.y >= ground:
            self.vel.y *= VENOM_ORB_BOUNCE_FACTOR
            self.bounced = True

        if self.bounced and self.pos.y >= self.screen_h - 20:
            return "BURST"

        return None


# ============================================================
#   HAZARD POOL (Boss3)
# ============================================================
class HazardPool(pygame.sprite.Sprite):
    def __init__(self, x, y, duration=HAZARD_POOL_DURATION):
        super().__init__()

        self.base_width = HAZARD_POOL_BASE_WIDTH
        self.base_height = HAZARD_POOL_BASE_HEIGHT

        self.image = pygame.Surface((self.base_width, self.base_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.timer = duration
        self.pulse_offset = random.uniform(0, 1000)

    def update(self, **kwargs):
        ticks = pygame.time.get_ticks()
        pulse = (math.sin((ticks + self.pulse_offset) * HAZARD_POOL_PULSE_SPEED) + 1) * 3

        w = self.base_width + pulse
        h = self.base_height + pulse * 0.5

        self.image = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)

        pygame.draw.ellipse(self.image, (0, 255, 0, 120), (0, 0, w, h))
        pygame.draw.ellipse(self.image, (0, 255, 120, 200), (4, 4, w - 8, h - 8))

        glow_alpha = int(120 + pulse * 20)
        pygame.draw.ellipse(self.image, (0, 255, 0, glow_alpha), (-6, -6, w + 12, h + 12), 2)

        self.rect = self.image.get_rect(center=self.rect.center)

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
