import pygame
import math
from settings import (
    BOSS_HEALTH_BASE, BOSS_SPEED_BASE, BOSS_LASER_COOLDOWN,
    BOSS_LASER_DURATION, BOSS_LASER_WARNING, RED, WHITE
)
from .base_boss import BaseBoss

class Boss1(BaseBoss):
    """
    Boss 1 — Planet Breaker
    """

    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__(screen_w, screen_h, level, speed)

        # -----------------------------------------
        # AUDIO OVERRIDES FOR PLANET BREAKER
        # -----------------------------------------
        self.sound_entry = "boss1_entry"
        self.sound_hit = "boss1_hit"
        self.sound_death = "boss1_death"
        self.sound_laser_warning = "boss1_laser_warning"
        self.sound_laser_fire = "boss1_laser"

        # If you don't have custom files yet, BaseBoss will fall back
        # to generic boss sounds automatically.

        # -----------------------------------------
        # STATS & VISUALS
        # -----------------------------------------
        raw_hp = BOSS_HEALTH_BASE * (1.25 ** (level - 1))

        self.max_health = self.apply_health_cap(raw_hp)
        self.health = self.max_health

        self.contact_damage = 10


        self.image = pygame.Surface((150, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 150, 50), border_radius=15)
        pygame.draw.rect(self.image, WHITE, (20, 50, 30, 30))
        pygame.draw.rect(self.image, WHITE, (100, 50, 30, 30))
        self.rect = self.image.get_rect()

        self.fire_rate_max = max(15, 45 - (level * 2))
        self.laser_cooldown = BOSS_LASER_COOLDOWN

        # NEW: laser state
        self.laser_active = False

    # ---------------------------------------------------------
    #   MOVEMENT — horizontal sway (dynamic width)
    # ---------------------------------------------------------
    def update_movement(self, player_pos=None):
        ticks = pygame.time.get_ticks()
        freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
        self.pos.x = self.screen_w // 2 + math.sin(ticks * freq) * (self.screen_w // 4)

    # ---------------------------------------------------------
    #   ATTACKS — laser logic
    # ---------------------------------------------------------
    def update_attacks(self, player_pos=None, groups=None, state=None):
        # Laser currently firing
        if self.laser_active_timer > 0:
            self.laser_active = True

            # Play laser firing sound on first frame of active timer
            if self.laser_active_timer == BOSS_LASER_DURATION:
                self.play_sound(self.sound_laser_fire)

            return

        # Laser warning phase
        if self.laser_warning_timer > 0:
            self.laser_active = False
            return

        # Cooling down
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
            return

        # Fire laser
        self.laser_warning_timer = BOSS_LASER_WARNING
        self.laser_active_timer = BOSS_LASER_DURATION
        self.laser_cooldown = BOSS_LASER_COOLDOWN

        # Play warning sound immediately when warning starts
        self.play_sound(self.sound_laser_warning)

    # ---------------------------------------------------------
    #   DRAW LASER (renderer calls this)
    # ---------------------------------------------------------
    def draw_laser(self, screen):
        if not self.laser_active:
            return

        # Laser is a vertical beam from boss downward
        laser_rect = pygame.Rect(
            self.pos.x - 10,
            self.pos.y + 40,
            20,
            self.screen_h - (self.pos.y + 40)
        )

        pygame.draw.rect(screen, (255, 50, 50), laser_rect)
