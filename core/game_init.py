import pygame

def initialize_game():
    pygame.init()
    pygame.mixer.init()

    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)


    # ⭐ Immediately maximize the window (SDL trick)
    pygame.display.toggle_fullscreen()
    pygame.display.toggle_fullscreen()

    pygame.display.set_caption("GalaxyRoids")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    # --------------------------
    # AUDIO
    # --------------------------
    from systems.audio import load_sounds, play_music
    sfx = load_sounds()
    sfx["play_music"] = play_music

    # --------------------------
    # DEBUGGER
    # --------------------------
    from systems.debugger import DebuggerOverlay
    debugger = DebuggerOverlay(font)

    # --------------------------
    # PLAYER
    # --------------------------
    from entities.player import Player
    player = Player(WIDTH, HEIGHT)

    # --------------------------
    # JOYSTICKS
    # --------------------------
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    # --------------------------
    # GROUPS
    # --------------------------
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
        "powerups": pygame.sprite.Group(),   # holds actual powerup sprites
        "hazards": pygame.sprite.Group(),
    }

    groups["all_sprites"].add(player)

    # --------------------------
    # POWERUP SPAWNER (FIX)
    # --------------------------
    from core.powerup_spawner import PowerupSpawner

    state = {}  # ensure state exists before adding entries

    state["powerup_spawner"] = PowerupSpawner(
        groups["powerups"],      # where powerup sprites go
        groups["all_sprites"]    # ensures they render
    )

    # --------------------------
    # GAME STATE
    # --------------------------
    from core.spawner import spawn_shrapnel_explosion

    state.update({
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

        # ⭐ MUST BE HERE
        "spawn_shrapnel_explosion": spawn_shrapnel_explosion,

        # ⭐ MUST BE HERE
        "debugger": debugger,
    })




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
