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

        # ----------------------------------------------------
        # DEFAULT AUDIO MAPPING (subclasses can override)
        # ----------------------------------------------------
        self.sfx = None  # will be injected by update() kwargs

        self.sound_hit = "boss_hit"
        self.sound_death = "boss_death"
        self.sound_laser_warning = "boss_laser_warning"
        self.sound_laser_fire = "boss_laser"
        self.sound_phase = "boss_phase"
        self.sound_entry = "boss_roar"

        # Track if entry sound has played
        self.entry_sound_played = False

    # --------------------------------------------------------
    # Helper: safe sound playback
    # --------------------------------------------------------
    def play_sound(self, sound_name):
        if not self.sfx:
            return
        snd = self.sfx.get(sound_name)
        if snd:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(snd)

    # -------------------------
    #   SHARED UPDATE LOGIC
    # -------------------------
    def update(self, **kwargs):
        # NEW: dynamic world size
        state = kwargs.get("state")
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        # Inject sfx dictionary
        self.sfx = kwargs.get("sfx", None)

        # Play entry sound once
        if not self.entry_sound_played and self.pos.y < self.target_y:
            self.play_sound(self.sound_entry)
            self.entry_sound_played = True

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
    def update_movement(self, player_pos=None):
        pass

    def update_attacks(self, player_pos=None, groups=None, state=None):
        pass

    def update_timers(self):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # Laser timers
        if self.laser_active_timer > 0:
            self.laser_active_timer -= 1

        elif self.laser_warning_timer > 0:
            # Play warning sound at start of warning phase
            if self.laser_warning_timer == 30:  # first frame of warning
                self.play_sound(self.sound_laser_warning)

            self.laser_warning_timer -= 1
