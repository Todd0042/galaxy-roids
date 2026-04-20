import pygame
from settings import SHRAPNEL_COOLDOWN_MAX


# ==========================
#   PLAYER HEALTH BAR
# ==========================

def draw_player_health_bar(screen, player, state):
    WIDTH = state["WIDTH"]

    # Scale bar width slightly with window size, but clamp it
    bar_width = max(180, min(300, int(WIDTH * 0.20)))
    bar_height = 18

    x = 20
    y = 20

    ratio = max(player.health / player.max_health, 0)

    # Background
    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))

    # Fill
    pygame.draw.rect(
        screen,
        (60, 200, 60),
        (x, y, int(bar_width * ratio), bar_height)
    )

    # Border
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (x, y, bar_width, bar_height),
        2
    )


# ==========================
#   SHRAPNEL COOLDOWN BAR
# ==========================

def draw_shrapnel_cooldown(screen, player, state):
    WIDTH = state["WIDTH"]

    bar_width = max(180, min(300, int(WIDTH * 0.20)))
    bar_height = 12

    x = 20
    y = 50

    ratio = min(player.shrapnel_cooldown / SHRAPNEL_COOLDOWN_MAX, 1)

    # Background
    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))

    # Fill
    pygame.draw.rect(
        screen,
        (200, 200, 40),
        (x, y, int(bar_width * ratio), bar_height)
    )

    # Border
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (x, y, bar_width, bar_height),
        2
    )


# ==========================
#     BOSS HEALTH BAR
# ==========================

def draw_boss_health_bar(screen, boss, state):
    if boss is None:
        return

    WIDTH = state["WIDTH"]

    # Boss bar scales with window width
    bar_width = max(220, min(400, int(WIDTH * 0.25)))
    bar_height = 20

    x = WIDTH - bar_width - 20
    y = 20

    ratio = max(boss.health / boss.max_health, 0)

    # Background
    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))

    # Fill
    pygame.draw.rect(
        screen,
        (255, 60, 60),
        (x, y, int(bar_width * ratio), bar_height)
    )

    # Border
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (x, y, bar_width, bar_height),
        2
    )
