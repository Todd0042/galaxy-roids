import pygame
import random
import math
from settings import (
    PLAYER_SIZE, CYAN, GOLDEN_YELLOW, PLAYER_ROT_SPEED, PLAYER_THRUST,
    PLAYER_FRICTION, PLAYER_REVERSE_THRUST, PLAYER_BRAKE_FRICTION,
    PLAYER_MAX_HEALTH, BLOB_STUN_TIME, SHRAPNEL_COOLDOWN_MAX
)


class TrailSegment(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (220, 240, 255), (2, 2), 2)
        self.rect = self.image.get_rect(center=pos)
        self.alpha = 180

    def update(self, **kwargs):
        self.alpha -= 6
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()

        # --- Rapid-fire state ---
        self.fire_cooldown = 0
        self.fire_button_held = False

        # --- Asteroid collision cooldown ---
        self.last_asteroid_hit = 0
        self.asteroid_hit_cooldown = 1000

        # --- Screen size ---
        self.screen_w = screen_w
        self.screen_h = screen_h

        # --- Ship appearance (image-based) ---
        self.base_image = pygame.image.load("assets/player/player_ship.png").convert_alpha()
        self.engine_glow = pygame.image.load("assets/player/engine_glow.png").convert_alpha()

        # Scale both to ~15%
        scale_factor = 0.15

        bw = int(self.base_image.get_width() * scale_factor)
        bh = int(self.base_image.get_height() * scale_factor)
        self.base_image = pygame.transform.smoothscale(self.base_image, (bw, bh))

        gw = int(self.engine_glow.get_width() * scale_factor)
        gh = int(self.engine_glow.get_height() * scale_factor)
        self.engine_glow = pygame.transform.smoothscale(self.engine_glow, (gw, gh))
        self.engine_glow_scaled = self.engine_glow.copy()

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(screen_w // 2, screen_h // 2))

        # --- Movement state ---
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)

        # IMPORTANT FIX — forward = UP
        self.direction = pygame.Vector2(0, -1)

        self.angle = 0
        self.thrusting = False

        self.rotation_speed = PLAYER_ROT_SPEED
        self.thrust = PLAYER_THRUST
        self.friction = PLAYER_FRICTION

        # --- Combat state ---
        self.shrapnel_cooldown = 0
        self.weapon_mode = "NORMAL"
        self.powerup_hits = 0

        # --- Status effects ---
        self.invulnerable_timer = 0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.stun_timer = 0

    # -------------------------------------------------
    #   Appearance
    # -------------------------------------------------
    def update_appearance(self):
        self.color = GOLDEN_YELLOW if self.weapon_mode == "SPREAD" else CYAN
        self.rotate(0)

    def rotate(self, angle_change):
        self.angle += angle_change

        # IMPORTANT FIX — forward = UP
        self.direction = pygame.Vector2(0, -1).rotate(self.angle)

        self.image = pygame.transform.rotate(self.base_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    # -------------------------------------------------
    #   Main Update
    # -------------------------------------------------
    def update(self, **kwargs):
        keys = pygame.key.get_pressed()
        joysticks = kwargs.get("joysticks", [])
        trail_group = kwargs.get("trail_group")
        state = kwargs.get("state")

        # Dynamic screen size
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.thrusting = False

        # --- Invulnerability flicker ---
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # --- Stun stops movement ---
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel = pygame.Vector2(0, 0)

        else:
            # --- Joystick rotation & thrust ---
            for joy in joysticks:
                if joy.get_axis(0) < -0.3:
                    self.rotate(-self.rotation_speed)
                elif joy.get_axis(0) > 0.3:
                    self.rotate(self.rotation_speed)

                if joy.get_axis(1) < -0.3:
                    self.vel += self.direction * self.thrust
                    self.thrusting = True
                elif joy.get_axis(1) > 0.3:
                    self.vel *= PLAYER_BRAKE_FRICTION
                    self.vel -= self.direction * PLAYER_REVERSE_THRUST

            # --- Keyboard rotation & thrust ---
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rotate(-self.rotation_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rotate(self.rotation_speed)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel += self.direction * self.thrust
                self.thrusting = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel *= PLAYER_BRAKE_FRICTION
                self.vel -= self.direction * PLAYER_REVERSE_THRUST

        # --- Engine trail ---
        if self.thrusting and trail_group is not None:
            for side in [-1, 1]:
                offset = self.direction.rotate(90 * side) * 8 - self.direction * 10
                jitter = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                trail_group.add(TrailSegment(self.pos + offset + jitter))

        # --- Movement physics ---
        self.vel *= self.friction
        self.pos += self.vel
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos

        # --- Engine Glow Animation ---
        if self.thrusting:
            t = pygame.time.get_ticks() * 0.01

            # Alpha pulse
            pulse = 180 + int(75 * abs(math.sin(t)))
            self.engine_glow.set_alpha(pulse)

            # Scale pulse
            scale = 1.0 + 0.05 * abs(math.sin(t * 0.5))

            # Velocity stretch
            speed = self.vel.length()
            stretch = 1.0 + min(speed / 12, 0.6)

            w = int(self.engine_glow.get_width() * scale)
            h = int(self.engine_glow.get_height() * stretch)

            self.engine_glow_scaled = pygame.transform.smoothscale(
                self.engine_glow, (w, h)
            )
        else:
            self.engine_glow.set_alpha(0)
            self.engine_glow_scaled = self.engine_glow

        # --- Visual flicker for stun/invulnerability ---
        if self.stun_timer > 0:
            self.image.set_alpha(150)
        elif self.invulnerable_timer % 10 > 5:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        # --- Cooldowns ---
        if self.shrapnel_cooldown > 0:
            self.shrapnel_cooldown -= 1
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    # -------------------------------------------------
    #   Draw
    # -------------------------------------------------
    def draw(self, surface):
        if self.thrusting:
            glow_img = self.engine_glow_scaled
            glow_rect = glow_img.get_rect(center=self.rect.center)
            surface.blit(glow_img, glow_rect)

        surface.blit(self.image, self.rect)

    # -------------------------------------------------
    #   Powerup Loss
    # -------------------------------------------------
    def lose_powerup_level(self):
        if self.powerup_hits > 0:
            self.powerup_hits -= 1

        lvl = self.powerup_hits
        self.weapon_mode = "NORMAL"
        self.has_laser = False
        self.homing_count = 0

        if lvl >= 1:
            self.weapon_mode = "SPREAD"
        if lvl >= 4:
            self.has_laser = True
        if lvl >= 5:
            self.homing_count = 1
        if lvl >= 6:
            self.homing_count = 2

        self.update_appearance()

    def take_damage(self, amount):
        if self.invulnerable_timer > 0:
            return
        self.health -= amount
        self.invulnerable_timer = 60
        self.lose_powerup_level()
        self.stun_timer = 10

    def apply_explosion(self, damage):
        self.health -= damage
        self.lose_powerup_level()
