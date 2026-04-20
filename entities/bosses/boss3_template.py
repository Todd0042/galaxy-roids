import pygame
import math

from settings import (
    BOSS_HEALTH_BASE,
    BOSS_SPEED_BASE,
    RED,
    WHITE,
    YELLOW,
    VENOM_ORB_SPREAD,
    VENOM_ORB_SPEED_X,
    VENOM_ORB_SPEED_Y,
)

from .base_boss import BaseBoss
from entities.projectiles import VenomOrb, HazardPool


class Boss3(BaseBoss):
    """
    Boss 3 — Scorpion Dreadnought
    Tail strike + venom orbs + hazard pools.
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed)

        # -----------------------------
        #   CORE STATS
        # -----------------------------
        self.max_health = BOSS_HEALTH_BASE * (1.35 ** (level - 1))
        self.health = self.max_health
        self.contact_damage = 10
        self.tail_damage = 5 + (self.level * 5)

        # -----------------------------
        #   BODY SPRITE
        # -----------------------------
        self.image = pygame.Surface((160, 90), pygame.SRCALPHA)

        # Main armored body
        pygame.draw.rect(self.image, RED, (10, 20, 140, 50), border_radius=18)

        # Head
        pygame.draw.rect(self.image, WHITE, (55, 5, 50, 25), border_radius=10)

        # Weak-spot abdomen (visual only; real hitbox is separate)
        pygame.draw.ellipse(self.image, (200, 80, 80), (60, 55, 40, 25))

        self.rect = self.image.get_rect()
        self.pos.y = 120  # Base vertical position

        # -----------------------------
        #   WEAK SPOT (world-space rect)
        # -----------------------------
        self.weakspot_offset = pygame.Rect(60, 55, 40, 25)
        self.weakspot_rect = pygame.Rect(0, 0, 40, 25)

        # -----------------------------
        #   TAIL SETUP (procedural)
        # -----------------------------
        self.tail_segments = [
            {"length": 45, "angle": -90.0},
            {"length": 40, "angle": -90.0},
            {"length": 35, "angle": -90.0},
        ]
        self.tail_tip = pygame.Vector2(self.pos.x, self.pos.y - 60)

        # Tail base offset
        self.tail_base_offset = pygame.Vector2(40, -20)

        # -----------------------------
        #   TAIL STRIKE TIMERS
        # -----------------------------
        self.tail_warning_timer = 0
        self.tail_active_timer = 0
        self.tail_cooldown = 120

        # -----------------------------
        #   DASH STATE
        # -----------------------------
        self.dashing = False
        self.dash_dir = 0
        self.dash_timer = 0
        self.dash_cooldown = 180

        # -----------------------------
        #   VENOM ORB ATTACK
        # -----------------------------
        self.venom_cooldown = 180

    # ---------------------------------------------------------
    #   MOVEMENT — stalking + occasional dash
    # ---------------------------------------------------------
    def update_movement(self, player_pos=None):
        # Dash logic
        if self.dashing:
            self.pos.x += self.dash_dir * self.speed * 2.5
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False

            self.pos.x = max(80, min(self.screen_w - 80, self.pos.x))
            return

        # Dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        else:
            # Trigger dash
            self.dashing = True
            self.dash_timer = 25

            if self.pos.x < self.screen_w // 2:
                self.dash_dir = 1
            else:
                self.dash_dir = -1

            self.dash_cooldown = 180

        # Base vertical position
        self.pos.y = 120

        # Stalking movement if player_pos provided
        if player_pos is not None:
            dx = player_pos.x - self.pos.x
            self.pos.x += dx * 0.02 * (self.speed / BOSS_SPEED_BASE)
        else:
            # Fallback sway like Boss1
            ticks = pygame.time.get_ticks()
            freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
            self.pos.x = self.screen_w // 2 + math.sin(ticks * freq) * (self.screen_w // 4)

        self.pos.x = max(80, min(self.screen_w - 80, self.pos.x))

    # ---------------------------------------------------------
    #   ATTACKS — tail strike + venom orbs
    # ---------------------------------------------------------
    def update_attacks(self, player_pos=None, groups=None, state=None):
        # Update tail geometry first
        self._update_tail(player_pos)

        # Tail strike state machine
        if self.tail_active_timer > 0:
            self.tail_active_timer -= 1
        elif self.tail_warning_timer > 0:
            self.tail_warning_timer -= 1
        elif self.tail_cooldown > 0:
            self.tail_cooldown -= 1
        else:
            level_scale = 1.0 + (self.level - 1) * 0.15
            self.tail_warning_timer = int(45 / level_scale)
            self.tail_active_timer = int(25 / level_scale)
            self.tail_cooldown = int(120 / level_scale)

        # Venom orb attack
        if self.venom_cooldown > 0:
            self.venom_cooldown -= 1
        else:
            if groups is not None and state is not None:
                self.spawn_venom_orbs(groups, state)
            # Faster at higher levels, but clamped
            self.venom_cooldown = max(60, 180 - (self.level * 10))

    # ---------------------------------------------------------
    #   VENOM ORB SPAWN (settings‑driven)
    # ---------------------------------------------------------
    def spawn_venom_orbs(self, groups, state):
        width = state["WIDTH"]
        height = state["HEIGHT"]

        for spread in VENOM_ORB_SPREAD:
            vx = spread * VENOM_ORB_SPEED_X
            vy = VENOM_ORB_SPEED_Y

            orb = VenomOrb(
                self.tail_tip.x,
                self.tail_tip.y,
                vx,
                vy,
                width,
                height
            )
            groups["boss_bullets"].add(orb)
            groups["all_sprites"].add(orb)

    # ---------------------------------------------------------
    #   TAIL GEOMETRY UPDATE
    # ---------------------------------------------------------
    def _update_tail(self, player_pos=None):
        tail_base = pygame.Vector2(
            self.pos.x + self.tail_base_offset.x,
            self.pos.y + self.tail_base_offset.y
        )

        # Aim tail at player if known
        if player_pos is not None:
            direction = (player_pos - tail_base)
            if direction.length_squared() > 0:
                target_angle = direction.angle_to(pygame.Vector2(1, 0))
            else:
                target_angle = -90.0
        else:
            target_angle = -90.0

        x, y = tail_base.x, tail_base.y
        for seg in self.tail_segments:
            seg["angle"] += (target_angle - seg["angle"]) * 0.15
            rad = math.radians(seg["angle"])
            x += math.cos(rad) * seg["length"]
            y += math.sin(rad) * seg["length"]

        self.tail_tip.update(x, y)

        # Update weakspot rect in world space
        self.weakspot_rect.x = self.pos.x - self.rect.width // 2 + self.weakspot_offset.x
        self.weakspot_rect.y = self.pos.y - self.rect.height // 2 + self.weakspot_offset.y

    # ---------------------------------------------------------
    #   DRAW EXTRA — tail + strike beam
    # ---------------------------------------------------------
    def draw_extra(self, screen):
        tail_base = pygame.Vector2(
            self.pos.x + self.tail_base_offset.x,
            self.pos.y + self.tail_base_offset.y
        )

        # Color based on state
        if self.tail_active_timer > 0:
            tail_color = (255, 80, 80)
        elif self.tail_warning_timer > 0:
            tail_color = YELLOW
        else:
            tail_color = WHITE

        # Build segment points
        points = [tail_base]
        x, y = tail_base.x, tail_base.y
        for seg in self.tail_segments:
            rad = math.radians(seg["angle"])
            x += math.cos(rad) * seg["length"]
            y += math.sin(rad) * seg["length"]
            points.append(pygame.Vector2(x, y))

        # Draw tail polyline
        if len(points) >= 2:
            pygame.draw.lines(screen, tail_color, False, points, 4)

        # Tail tip glow
        pygame.draw.circle(screen, tail_color, (int(self.tail_tip.x), int(self.tail_tip.y)), 8)

        # Draw active strike beam
        if self.tail_active_timer > 0:
            strike_rect = pygame.Rect(
                self.tail_tip.x - 8,
                self.tail_tip.y,
                16,
                self.screen_h - self.tail_tip.y
            )
            pygame.draw.rect(screen, (255, 60, 60), strike_rect)

    # ---------------------------------------------------------
    #   DAMAGE HANDLING — weak spot vs armor
    # ---------------------------------------------------------
    def take_damage(self, amount, hit_rect):
        if hit_rect.colliderect(self.weakspot_rect):
            self.health -= amount
        else:
            self.health -= amount * 0.25

        if self.health <= 0:
            self.alive = False
 