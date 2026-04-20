import pygame
import math
import systems.audio as audio

from core.spawner import spawn_shrapnel_explosion
from settings import (
    INITIAL_LIVES,
    ENEMY_SPEED,
    BOSS_SPEED_BASE,
)

class BaseBoss(pygame.sprite.Sprite):
    ...
    
# ============================================================
#   INITIALIZE GAME
# ============================================================
def initialize_game():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(128)
    print("INITIAL_LIVES =", INITIAL_LIVES)


    # 1. Create a borderless resizable window
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE | pygame.NOFRAME)

    # 2. Force the window to appear
    pygame.display.flip()
    pygame.event.pump()

    # 3. Maximize using the fullscreen toggle trick
    pygame.display.toggle_fullscreen()
    pygame.display.toggle_fullscreen()

    # 4. Restore the window frame
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

    # 5. Sync final maximized size
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()





    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    # ============================================================
    #   AUDIO
    # ============================================================
    from systems.audio import load_sounds, play_music

    # ⭐ Load ALL SFX here
    sfx = load_sounds({

    # ==========================
    # PLAYER
    # ==========================    
    "player_engine":        "assets/sfx/player/player_engine.wav",
    "player_hit":           "assets/sfx/player/player_hit.wav",
    "player_low_health":    "assets/sfx/player/player_low_health.wav",
    "player_power_reset":   "assets/sfx/player/player_power_reset.wav",

    # ==========================
    # WEAPONS
    # ==========================
    "weapon_pew":           "assets/sfx/weapons/weapon_pew.wav",
    "weapon_spread":        "assets/sfx/weapons/weapon_spread.wav",
    "weapon_laser_charge":  "assets/sfx/weapons/weapon_laser_charge.wav",
    "weapon_missile":       "assets/sfx/weapons/weapon_missile.wav",
    "grenade_launch":       "assets/sfx/weapons/grenade_launch.wav",
    "grenade_explode":      "assets/sfx/weapons/grenade_explode.wav",

    # ==========================
    # POWERUPS
    # ==========================
    "powerup_spawn":        "assets/sfx/powerups/powerup_spawn.wav",
    "powerup_pickup":       "assets/sfx/powerups/powerup_pickup.wav",

    # ASTEROIDS
    # ==========================
    "asteroid_break":       "assets/sfx/asteroids/asteroid_break.wav",
    "asteroid_destroy":     "assets/sfx/asteroids/asteroid_destroy.wav",

    # ==========================
    # BOSSES (generic)
    # ==========================
    "boss_hit":             "assets/sfx/bosses/boss_hit.wav",
    "boss_death":           "assets/sfx/bosses/boss_death.wav",
    "boss_laser_warning":   "assets/sfx/bosses/boss_laser_warning.wav",
    "boss_laser":           "assets/sfx/bosses/boss_laser.wav",
    "boss_defeated":        "assets/sfx/bosses/boss_defeated.wav",

    # ==========================
    # BOSS 1
    # ==========================
    "boss1_entry":          "assets/sfx/bosses/boss1/boss1_entry.wav",
    "boss1_hit":            "assets/sfx/bosses/boss1/boss1_hit.wav",
    "boss1_death":          "assets/sfx/bosses/boss1/boss1_death.wav",
    "boss1_laser_warning":  "assets/sfx/bosses/boss1/boss1_laser_warning.wav",
    "boss1_laser":          "assets/sfx/bosses/boss1/boss1_laser.wav",

    # ==========================
    # BOSS 2
    # ==========================
    "boss2_entry":          "assets/sfx/bosses/boss2/boss2_entry.wav",
    "boss2_hit":            "assets/sfx/bosses/boss2/boss2_hit.wav",
    "boss2_death":          "assets/sfx/bosses/boss2/boss2_death.wav",
    "boss2_bomb_launch":    "assets/sfx/bosses/boss2/boss2_bomb_launch.wav",
    "boss2_bomb_explode":   "assets/sfx/bosses/boss2/boss2_bomb_explode.wav",

    # ==========================
    # BOSS 3
    # ==========================
    "boss3_entry":          "assets/sfx/bosses/boss3/boss3_entry.wav",
    "boss3_hit":            "assets/sfx/bosses/boss3/boss3_hit.wav",
    "boss3_death":          "assets/sfx/bosses/boss3/boss3_death.wav",
    "boss3_tail_warning":   "assets/sfx/bosses/boss3/boss3_tail_warning.wav",
    "boss3_tail_strike":    "assets/sfx/bosses/boss3/boss3_tail_strike.wav",
    "boss3_venom_launch":   "assets/sfx/bosses/boss3/boss3_venom_launch.wav",
    "boss3_venom_burst":    "assets/sfx/bosses/boss3/boss3_venom_burst.wav",
    "boss3_dash":           "assets/sfx/bosses/boss3/boss3_dash.wav",
    "boss3_weakspot_hit":   "assets/sfx/bosses/boss3/boss3_weakspot_hit.wav",

    # ==========================
    # UI
    # ==========================
    "ui_click":             "assets/sfx/ui/ui_click.wav",
    "ui_hover":             "assets/sfx/ui/ui_hover.wav",
    "ui_popup_open":        "assets/sfx/ui/ui_popup_open.wav",
    "ui_confirm":           "assets/sfx/ui/ui_confirm.wav",
    "ui_select_harder":     "assets/sfx/ui/ui_select_harder.wav",

    # ==========================
    # LEVEL FLOW
    # ==========================
    "level_start":          "assets/sfx/level/level_start.wav",
    "level_complete":       "assets/sfx/level/level_complete.wav",
})

    audio.set_sfx_cooldown("laser", 0.5)
    audio.set_sfx_cooldown("explosion_small", 0.25)
    audio.set_sfx_cooldown("explosion_big", 0.4)
    audio.set_sfx_cooldown("ui_click", 0.1)
    audio.set_sfx_cooldown("weapon_pew", 0.0)
    audio.set_sfx_cooldown("weapon_spread", 0.0)
    audio.set_sfx_cooldown("weapon_laser", 0.0)
    audio.set_sfx_cooldown("weapon_laser_charge", 0.0)
    audio.set_sfx_cooldown("weapon_missile", 0.0)


    # Add music loader
    sfx["play_music"] = audio.play_music

    # ⭐ FORCE DEFAULT MUSIC MODE
    audio.music_mode = "16bit"

    # ⭐ START MENU MUSIC
    audio.play_music("menu_theme")

    # ============================================================
    #   DEBUGGER
    # ============================================================
    from systems.debugger import DebuggerOverlay
    debugger = DebuggerOverlay(font)   # ⭐ FIXED

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
        "lives": INITIAL_LIVES,
        "level": 1,
        "game_active": False,
        "boss_spawned": False,
        "last_pew_time": None,
        "last_periodic_spawn": 0,
        "level_start_time": pygame.time.get_ticks(),

        # Apply difficulty settings
        "current_enemy_speed": ENEMY_SPEED,
        "current_boss_speed": BOSS_SPEED_BASE,

        "enemies_per_side": 4,
        "screenshake": 0,
        "sfx": sfx,
        "spawn_shrapnel_explosion": spawn_shrapnel_explosion,

        # ⭐ REQUIRED FOR SAFE SPAWN DISTANCE
        "player": player,
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

