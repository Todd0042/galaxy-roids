import pygame
import math

class BaseBoss(pygame.sprite.Sprite):
    """
    Shared base class for all bosses.
    Handles:
    - position
    - entry movement
    - hit flash
    - laser timers
    - fire cooldown
    - basic update loop
    """

    def __init__(self, screen_w, screen_h, level, speed):
        super().__init__()

        # Initial bounds (dynamic override happens in update)
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.level = level
        self.speed = speed

        # Positioning
        self.pos = pygame.Vector2(screen_w // 2, -150)
        self.target_y = 120

        # Timers
        self.fire_cooldown = 0
        self.laser_cooldown = 0
        self.laser_warning_timer = 0
        self.laser_active_timer = 0

        self.hit_flash = 0

        # Must be set by subclasses:
        self.image = None
        self.rect = None
        self.max_health = 1
        self.health = 1

    # -------------------------
    #   SHARED UPDATE LOGIC
    # -------------------------
        # -------------------------
    #   SHARED UPDATE LOGIC
    # -------------------------
    def update(self, **kwargs):
        # NEW: dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        player_pos = kwargs.get("player_pos")
        groups = kwargs.get("groups")

        self.update_entry()
        self.update_movement(player_pos)
        self.update_attacks(player_pos, groups, state)
        self.update_timers()

        if self.rect:
            self.rect.center = self.pos



    # -------------------------
    #   ENTRY MOVEMENT
    # -------------------------
    def update_entry(self):
        if self.pos.y < self.target_y:
            self.pos.y += self.speed

    # -------------------------
    #   OVERRIDABLE HOOKS
    # -------------------------
    def update_movement(self):
        pass

    def update_attacks(self):
        pass

    def update_timers(self):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        if self.laser_active_timer > 0:
            self.laser_active_timer -= 1
        elif self.laser_warning_timer > 0:
            self.laser_warning_timer -= 1
