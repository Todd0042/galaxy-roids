import pygame
from settings import (
    INITIAL_LIVES, ENEMY_SPEED, BOSS_SPEED_BASE,
    FPS, BLACK
)

from systems.debugger import DebuggerOverlay
from systems.audio import init_sfx
from entities.player import Player


def initialize_game():
    """
    Initializes pygame, screen, clock, font, debugger, SFX,
    sprite groups, player, joysticks, and game state.
    Returns a dictionary containing all initialized components.
    """

    # --- Pygame setup ---
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galaxyroids — Modular Edition")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # --- Debugger ---
    debugger = DebuggerOverlay(font)

    # --- Audio ---
    sfx = init_sfx()

    # --- Sprite groups ---
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    shrapnel_grenades = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    gravity_bombs = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    trail_group = pygame.sprite.Group()

    # --- Player ---
    player = Player(WIDTH, HEIGHT)
    all_sprites.add(player)

    # --- Joysticks ---
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joysticks.append(joy)

    # --- Game state ---
    state = {
        "lives": INITIAL_LIVES,
        "score": 0,
        "level": 1,
        "game_active": False,

        "enemies_per_side": 6,
        "current_enemy_speed": ENEMY_SPEED,
        "current_boss_speed": BOSS_SPEED_BASE,

        "last_pew_time": 0,
        "last_periodic_spawn": 0,
        "boss_spawned": False,
        "level_start_time": pygame.time.get_ticks(),
    }

    # --- Group bundle for convenience ---
    groups = {
        "all_sprites": all_sprites,
        "enemies": enemies,
        "asteroids": asteroids,
        "bullets": bullets,
        "shrapnel_grenades": shrapnel_grenades,
        "boss_group": boss_group,
        "boss_bullets": boss_bullets,
        "gravity_bombs": gravity_bombs,
        "powerups": powerups,
        "trail_group": trail_group,
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
