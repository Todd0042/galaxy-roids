import pygame
from ui.hud import (
    draw_player_health_bar,
    draw_shrapnel_cooldown,
    draw_boss_health_bar
)


def render_frame(screen, player, groups, state, debugger):
    """
    Draws the entire frame:
    - Background
    - All sprites
    - Trails
    - HUD (health, cooldown, boss bar)
    - Boss laser (if active)
    - Debugger overlay (if active)

    This function contains ZERO game logic.
    """

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]

    # ==========================
    # Background
    # ==========================
    screen.fill((0, 0, 0))

    # ==========================
    # Sprites
    # ==========================
    groups["all_sprites"].draw(screen)

    # ==========================
    # Trails (draw like normal sprites)
    # ==========================
    groups["trail_group"].draw(screen)

    # ==========================
    # Boss Laser (if active)
    # ==========================
    for boss in groups["boss_group"]:
        if hasattr(boss, "draw_laser") and boss.laser_active:
            boss.draw_laser(screen)

    # ==========================
    # HUD
    # ==========================
    draw_player_health_bar(screen, player)
    draw_shrapnel_cooldown(screen, player)

    # Boss health bar (if boss exists)
    boss = next(iter(groups["boss_group"]), None)
    if boss:
        draw_boss_health_bar(screen, boss, WIDTH)

    # ==========================
    # Debugger Overlay (if active)
    # ==========================
    if debugger.active:
        debugger.draw(screen, WIDTH, HEIGHT)

    # ==========================
    # Flip
    # ==========================
    pygame.display.flip()
