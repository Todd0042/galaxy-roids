import pygame
import random
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
        self.asteroid_hit_cooldown = 1000  # 1 second

        # Store initial size (but dynamic size will override this)
        self.screen_w = screen_w
        self.screen_h = screen_h

        # --- Ship appearance ---
        self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.color = CYAN
        pygame.draw.polygon(
            self.original_image, self.color,
            [(PLAYER_SIZE, PLAYER_SIZE // 2), (0, 0), (5, PLAYER_SIZE // 2), (0, PLAYER_SIZE)]
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(screen_w // 2, screen_h // 2))

        # --- Movement state ---
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(1, 0)
        self.angle = 0

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
    #   Status Effects
    # -------------------------------------------------
    def apply_trap(self, duration_ms, damage):
        self.health -= damage
        frames = int(duration_ms / 1000 * 60)
        self.stun_timer = frames

    # -------------------------------------------------
    #   Appearance
    # -------------------------------------------------
    def update_appearance(self):
        self.color = GOLDEN_YELLOW if self.weapon_mode == "SPREAD" else CYAN
        self.original_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(
            self.original_image, self.color,
            [(PLAYER_SIZE, PLAYER_SIZE // 2), (0, 0), (5, PLAYER_SIZE // 2), (0, PLAYER_SIZE)]
        )
        self.rotate(0)

    def rotate(self, angle_change):
        self.angle += angle_change
        self.direction = pygame.Vector2(1, 0).rotate(self.angle)
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    # -------------------------------------------------
    #   Main Update
    # -------------------------------------------------
    def update(self, **kwargs):
        keys = pygame.key.get_pressed()
        joysticks = kwargs.get("joysticks", [])
        trail_group = kwargs.get("trail_group")
        state = kwargs.get("state")

        # Dynamic screen size (critical for resizing)
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        is_thrusting = False

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
                    is_thrusting = True
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
                is_thrusting = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel *= PLAYER_BRAKE_FRICTION
                self.vel -= self.direction * PLAYER_REVERSE_THRUST

        # --- Engine trail ---
        if is_thrusting and trail_group is not None:
            for side in [-1, 1]:
                offset = self.direction.rotate(90 * side) * 8 - self.direction * 10
                jitter = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                trail_group.add(TrailSegment(self.pos + offset + jitter))

        # --- Movement physics ---
        self.vel *= self.friction
        self.pos += self.vel

        # --- Dynamic wrapping using updated screen size ---
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h

        self.rect.center = self.pos

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
    #   Powerup Loss
    # -------------------------------------------------
    def lose_powerup_level(self):
        if self.powerup_hits > 0:
            self.powerup_hits -= 1

        lvl = self.powerup_hits

        self.weapon_mode = "NORMAL"
        self.has_laser = False
        self.homing_count = 0

        if lvl == 1:
            self.weapon_mode = "SPREAD"
        elif lvl == 2:
            self.weapon_mode = "SPREAD"
        elif lvl == 3:
            self.weapon_mode = "SPREAD"
        elif lvl == 4:
            self.weapon_mode = "SPREAD"
            self.has_laser = True
        elif lvl == 5:
            self.weapon_mode = "SPREAD"
            self.has_laser = True
            self.homing_count = 1
        elif lvl >= 6:
            self.weapon_mode = "SPREAD"
            self.has_laser = True
            self.homing_count = 2

        self.update_appearance()

    def take_damage(self, amount):
        # Ignore damage if invulnerable
        if self.invulnerable_timer > 0:
            return

        # Apply damage
        self.health -= amount

        # Trigger brief invulnerability (same as explosions)
        self.invulnerable_timer = 60  # 1 second at 60 FPS

        # Lose powerup level on hit
        self.lose_powerup_level()

        # Optional: small stun on hit (matches your blob stun system)
        self.stun_timer = 10


    # -------------------------------------------------
    #   Explosion damage hook
    # -------------------------------------------------
    def apply_explosion(self, damage):
        self.health -= damage
        self.lose_powerup_level()
