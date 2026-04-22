import pygame
import math
import os
import sys

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

# ============================================================
#   RESOURCE PATH (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


class Boss3(BaseBoss):
    """
    Boss 3 — Scorpion Dreadnought
    Tail strike + venom orbs + hazard pools.
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed)

        # -----------------------------------------
        # AUDIO OVERRIDES FOR SCORPION DREADNOUGHT
        # -----------------------------------------
        self.sound_entry = "boss3_entry"
        self.sound_hit = "boss3_hit"
        self.sound_death = "boss3_death"

        self.sound_tail_warning = "boss3_tail_warning"
        self.sound_tail_strike = "boss3_tail_strike"

        self.sound_venom_launch = "boss3_venom_launch"
        self.sound_venom_burst = "boss3_venom_burst"

        self.sound_dash = "boss3_dash"
        self.sound_weakspot = "boss3_weakspot_hit"

        # -----------------------------------------
        #   CORE STATS
        # -----------------------------------------
        raw_hp = BOSS_HEALTH_BASE * (1.35 ** (level - 1))

        self.max_health = self.apply_health_cap(raw_hp)
        self.health = self.max_health

        self.contact_damage = 10
        self.tail_damage = 5 + (self.level * 5)

        # -----------------------------------------
        #   BODY SPRITE
        # -----------------------------------------
        self.image = pygame.Surface((160, 90), pygame.SRCALPHA)

        pygame.draw.rect(self.image, RED, (10, 20, 140, 50), border_radius=18)
        pygame.draw.rect(self.image, WHITE, (55, 5, 25, 25), border_radius=10)
        pygame.draw.ellipse(self.image, (200, 80, 80), (60, 55, 40, 25))

        self.rect = self.image.get_rect()
        self.pos.y = 120

        # -----------------------------------------
        #   WEAK SPOT
        # -----------------------------------------
        self.weakspot_offset = pygame.Rect(60, 55, 40, 25)
        self.weakspot_rect = pygame.Rect(0, 0, 40, 25)

        # -----------------------------------------
        #   TAIL SETUP
        # -----------------------------------------
        self.tail_segments = [
            {"length": 45, "angle": -90.0},
            {"length": 40, "angle": -90.0},
            {"length": 35, "angle": -90.0},
        ]
        self.tail_tip = pygame.Vector2(self.pos.x, self.pos.y - 60)
        self.tail_base_offset = pygame.Vector2(40, -20)

        # -----------------------------------------
        #   TAIL STRIKE TIMERS
        # -----------------------------------------
        self.tail_warning_timer = 0
        self.tail_active_timer = 0
        self.tail_cooldown = 120

        # -----------------------------------------
        #   DASH STATE
        # -----------------------------------------
        self.dashing = False
        self.dash_dir = 0
        self.dash_timer = 0
        self.dash_cooldown = 180

        # -----------------------------------------
        #   VENOM ORB ATTACK
        # -----------------------------------------
        self.venom_cooldown = 180

    # ---------------------------------------------------------
    #   MOVEMENT — stalking + occasional dash
    # ---------------------------------------------------------
    def update_movement(self, player_pos=None):
        # Dash logic
        if self.dashing:
            self.pos.x += self.dash_dir * self.speed * 2.5
            self.dash_timer -= 1

            # ⭐ AUDIO: dash start
            if self.dash_timer == 24:
                self.play_sound(self.sound_dash)

            # ⭐ SHAKE: dash impact
            if self.dash_timer == 24:
                if self.sfx:
                    self.sfx["screenshake"] = max(self.sfx.get("screenshake", 0), 8)

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

        # Stalking movement
        if player_pos is not None:
            dx = player_pos.x - self.pos.x
            self.pos.x += dx * 0.02 * (self.speed / BOSS_SPEED_BASE)
        else:
            ticks = pygame.time.get_ticks()
            freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
            self.pos.x = self.screen_w // 2 + math.sin(ticks * freq) * (self.screen_w // 4)

        self.pos.x = max(80, min(self.screen_w - 80, self.pos.x))

    # ---------------------------------------------------------
    #   ATTACKS — tail strike + venom orbs
    # ---------------------------------------------------------
    def update_attacks(self, player_pos=None, groups=None, state=None):
        self._update_tail(player_pos)

        # Tail strike state machine
        if self.tail_active_timer > 0:
            self.tail_active_timer -= 1

            # ⭐ AUDIO: tail strike
            if self.tail_active_timer == 24:
                self.play_sound(self.sound_tail_strike)

            # ⭐ SHAKE: tail strike impact
            if self.tail_active_timer == 24 and state is not None:
                state["screenshake"] = max(state.get("screenshake", 0), 14)

        elif self.tail_warning_timer > 0:
            # ⭐ AUDIO: tail warning
            if self.tail_warning_timer == 44:
                self.play_sound(self.sound_tail_warning)

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
                # ⭐ AUDIO: venom launch
                self.play_sound(self.sound_venom_launch)
                self.spawn_venom_orbs(groups, state)

            self.venom_cooldown = max(60, 180 - (self.level * 10))

    # ---------------------------------------------------------
    #   VENOM ORB SPAWN
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

        self.weakspot_rect.x = self.pos.x - self.rect.width // 2 + self.weakspot_offset.x
        self.weakspot_rect.y = self.pos.y - self.rect.height // 2 + self.weakspot_offset.y

    # ---------------------------------------------------------
    #   DRAW — body + tail
    # ---------------------------------------------------------
    def draw(self, surface):
        # Draw main body
        surface.blit(self.image, self.rect)

        # Draw tail segments
        tail_base = pygame.Vector2(
            self.pos.x + self.tail_base_offset.x,
            self.pos.y + self.tail_base_offset.y
        )

        x, y = tail_base.x, tail_base.y

        for seg in self.tail_segments:
            rad = math.radians(seg["angle"])
            nx = x + math.cos(rad) * seg["length"]
            ny = y + math.sin(rad) * seg["length"]

            pygame.draw.line(surface, YELLOW, (x, y), (nx, ny), 6)
            x, y = nx, ny

        # Tail tip
        pygame.draw.circle(surface, YELLOW, (int(self.tail_tip.x), int(self.tail_tip.y)), 8)

    # ---------------------------------------------------------
    #   DAMAGE HANDLING — weak spot vs armor
    # ---------------------------------------------------------
    def take_damage(self, amount, hit_rect):
        if hit_rect.colliderect(self.weakspot_rect):
            self.health -= amount

            # ⭐ AUDIO: weak spot hit
            self.play_sound(self.sound_weakspot)

        else:
            self.health -= amount * 0.25

            # ⭐ AUDIO: normal hit
            self.play_sound(self.sound_hit)

        if self.health <= 0:
            self.alive = False

            # ⭐ AUDIO: death
            self.play_sound(self.sound_death)
