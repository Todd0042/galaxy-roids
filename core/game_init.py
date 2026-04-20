import pygame
import math

class BaseBoss(pygame.sprite.Sprite):
    ...

# ============================================================
#   INITIALIZE GAME
# ============================================================
def initialize_game():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("GalaxyRoids")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    # ============================================================
    #   AUDIO
    # ============================================================
    from systems.audio import load_sounds, play_music

    # ⭐ Load ALL SFX here
    sfx = load_sounds({
        # Player
        "player_engine": "assets/sfx/player_engine.wav",
        "player_hit": "assets/sfx/player_hit.wav",
        "player_low_health": "assets/sfx/player_low_health.wav",
        "player_power_reset": "assets/sfx/player_power_reset.wav",

        # Powerups
        "powerup_spawn": "assets/sfx/powerup_spawn.wav",
        "powerup_pickup": "assets/sfx/powerup_pickup.wav",

        # Asteroids
        "asteroid_break": "assets/sfx/asteroid_break.wav",
        "asteroid_destroy": "assets/sfx/asteroid_destroy.wav",

        # Boss generic
        "boss_hit": "assets/sfx/boss_hit.wav",
        "boss_death": "assets/sfx/boss_death.wav",
        "boss_laser_warning": "assets/sfx/boss_laser_warning.wav",
        "boss_laser": "assets/sfx/boss_laser.wav",
        "boss_defeated": "assets/sfx/boss_defeated.wav",

        # Boss 1
        "boss1_entry": "assets/sfx/boss1_entry.wav",
        "boss1_hit": "assets/sfx/boss1_hit.wav",
        "boss1_death": "assets/sfx/boss1_death.wav",
        "boss1_laser_warning": "assets/sfx/boss1_laser_warning.wav",
        "boss1_laser": "assets/sfx/boss1_laser.wav",

        # Boss 2
        "boss2_entry": "assets/sfx/boss2_entry.wav",
        "boss2_hit": "assets/sfx/boss2_hit.wav",
        "boss2_death": "assets/sfx/boss2_death.wav",
        "boss2_bomb_launch": "assets/sfx/boss2_bomb_launch.wav",
        "boss2_bomb_explode": "assets/sfx/boss2_bomb_explode.wav",

        # Boss 3
        "boss3_entry": "assets/sfx/boss3_entry.wav",
        "boss3_hit": "assets/sfx/boss3_hit.wav",
        "boss3_death": "assets/sfx/boss3_death.wav",
        "boss3_tail_warning": "assets/sfx/boss3_tail_warning.wav",
        "boss3_tail_strike": "assets/sfx/boss3_tail_strike.wav",
        "boss3_venom_launch": "assets/sfx/boss3_venom_launch.wav",
        "boss3_venom_burst": "assets/sfx/boss3_venom_burst.wav",
        "boss3_dash": "assets/sfx/boss3_dash.wav",
        "boss3_weakspot_hit": "assets/sfx/boss3_weakspot_hit.wav",

        # UI
        "ui_click": "assets/sfx/ui_click.wav",
        "ui_hover": "assets/sfx/ui_hover.wav",
        "ui_popup_open": "assets/sfx/ui_popup_open.wav",
        "ui_confirm": "assets/sfx/ui_confirm.wav",
        "ui_select_harder": "assets/sfx/ui_select_harder.wav",

        # Level flow
        "level_start": "assets/sfx/level_start.wav",
        "level_complete": "assets/sfx/level_complete.wav",
    })

    # Add music loader
    sfx["play_music"] = play_music

    # ============================================================
    #   DEBUGGER
    # ============================================================
    from systems.debugger import DebuggerOverlay
    debugger = DebuggerOverlay()

    # ============================================================
    #   PLAYER
    # ============================================================
    from entities.player import Player
    player = Player(WIDTH, HEIGHT)
    player.sfx = sfx  # ⭐ give player audio access

    # ============================================================
    #   JOYSTICKS
    # ============================================================
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    # ============================================================
    #   GROUPS
    # ============================================================
    groups = {
        "all_sprites": pygame.sprite.Group(),
        "enemies": pygame.sprite.Group(),
        "asteroids": pygame.sprite.Group(),
        "bullets": pygame.sprite.Group(),
        "boss_bullets": pygame.sprite.Group(),
        "boss_group": pygame.sprite.Group(),
        "trail_group": pygame.sprite.Group(),
        "shrapnel_grenades": pygame.sprite.Group(),
        "gravity_bombs": pygame.sprite.Group(),
        "boss_bullets": pygame.sprite.Group(),
        "powerups": pygame.sprite.Group(),
    }

    groups["all_sprites"].add(player)

    # ============================================================
    #   GAME STATE
    # ============================================================
    state = {
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
        "score": 0,
        "lives": 3,
        "level": 1,
        "game_active": False,
        "boss_spawned": False,
        "last_pew_time": 0,
        "last_periodic_spawn": 0,
        "level_start_time": pygame.time.get_ticks(),
        "current_enemy_speed": 1.0,
        "current_boss_speed": 1.0,
        "enemies_per_side": 4,
        "screenshake": 0,
        "sfx": sfx,  # ⭐ global audio access
    }

    return {
        "screen": screen,
        "clock": clock,
        "font": font,
        "debugger": debugger,
        "sfx": sfx,
        "player": player,
        "joysticks": joysticks,
        "groups": groups,
        "state": state,
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
    }
