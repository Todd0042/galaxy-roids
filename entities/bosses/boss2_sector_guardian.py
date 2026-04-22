import pygame
import math
import random
import os
import sys
from settings import (
    BOSS_HEALTH_BASE, BOSS_SPEED_BASE, WHITE
)
from entities.projectiles import GravityBomb
from entities.projectiles import Boss2LaserBeam
from .base_boss import BaseBoss

# ============================================================
#   RESOURCE PATH (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


class Boss2(BaseBoss):
    """
    Boss 2 — Sector Guardian
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed * 1.2)

        # Even-numbered levels get the death laser
        self.enable_death_laser = (level % 2 == 0)
        self.death_laser_cooldown = 30   # ~5 seconds
        print("Laser enabled:", self.enable_death_laser)

        # -----------------------------------------
        # AUDIO OVERRIDES FOR SECTOR GUARDIAN
        # -----------------------------------------
        self.sound_entry = "boss2_entry"
        self.sound_hit = "boss2_hit"
        self.sound_death = "boss2_death"
        self.sound_bomb_launch = "boss2_bomb_launch"

        # -----------------------------------------
        # STATS & VISUALS
        # -----------------------------------------
        raw_hp = (BOSS_HEALTH_BASE * 1.4) * (1.25 ** (level - 1))

        self.max_health = self.apply_health_cap(raw_hp)
        self.health = self.max_health

        self.contact_damage = 10

        self.image = pygame.Surface((180, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 0, 255), (0, 0, 180, 60), border_radius=20)
        pygame.draw.rect(self.image, WHITE, (40, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (80, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (120, 60, 20, 40))
        self.rect = self.image.get_rect()

        self.target_y = 150
        self.bomb_cooldown = 60   # faster bombs

    # ---------------------------------------------------------
    #   MOVEMENT — dynamic horizontal + vertical sway
    # ---------------------------------------------------------
    def update_movement(self, player_pos=None):
        ticks = pygame.time.get_ticks()
        self.pos.x = self.screen_w // 2 + math.sin(ticks * 0.0015) * (self.screen_w // 3)
        self.pos.y = self.target_y + math.cos(ticks * 0.003) * 50

    # ---------------------------------------------------------
    #   ATTACK — gravity bombs + death laser
    # ---------------------------------------------------------
    def update_attacks(self, player_pos=None, groups=None, state=None):

        # -------------------------
        # Gravity Bombs
        # -------------------------
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
        else:
            dist = random.randint(200, 600)

            # Downward cone (your angle system: 180° = down)
            angle = random.randint(135, 225)

            bomb = GravityBomb(self.rect.center, angle, self.screen_w, self.screen_h, dist)

            self.play_sound(self.sound_bomb_launch)

            groups["all_sprites"].add(bomb)
            groups["gravity_bombs"].add(bomb)

            self.bomb_cooldown = 60

        # -------------------------
        # Death Laser (even levels only)
        # -------------------------
        if self.enable_death_laser:

            if self.death_laser_cooldown > 0:
                self.death_laser_cooldown -= 1
            else:
                self.fire_death_laser(groups)
                self.death_laser_cooldown = 300

    # ---------------------------------------------------------
    #   ATTACK — Death Laser (3‑way spread)
    # ---------------------------------------------------------
    def fire_death_laser(self, groups):
        angles = [180, 165, 195]

        # Slow the boss while firing
        self.speed_multiplier = 0.25
        self.laser_slow_timer = 90  # 1.5 seconds

        for ang in angles:
            laser = Boss2LaserBeam(
                boss=self,
                angle=ang,
                screen_w=self.screen_w,
                screen_h=self.screen_h,
                duration=90
            )

            groups["all_sprites"].add(laser)
            groups["boss_bullets"].add(laser)

        self.play_sound("boss1_laser")

    def update(self, player_pos=None, groups=None, state=None, **kwargs):
        # Laser slow-down logic
        if hasattr(self, "laser_slow_timer") and self.laser_slow_timer > 0:
            self.laser_slow_timer -= 1
            self.speed_multiplier = 0.25
        else:
            self.speed_multiplier = 1.0

        # Call BaseBoss update (movement + attacks)
        super().update(player_pos=player_pos, groups=groups, state=state, **kwargs)
