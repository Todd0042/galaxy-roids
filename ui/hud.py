import pygame
from settings import SHRAPNEL_COOLDOWN_MAX


# ==========================
#   PLAYER HEALTH BAR
# ==========================

def draw_player_health_bar(screen, player):
    bar_width = 200
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

def draw_shrapnel_cooldown(screen, player):
    bar_width = 200
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

def draw_boss_health_bar(screen, boss, screen_width):
    if boss is None:
        return

    bar_width = 220
    bar_height = 20
    x = screen_width - bar_width - 20
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
