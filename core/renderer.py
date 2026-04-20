import pygame
from ui.hud import (
    draw_player_health_bar,
    draw_shrapnel_cooldown,
    draw_boss_health_bar
)


def render_frame(surface, player, groups, state, debugger):
    """
    Draws the entire frame to the provided surface:
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
    surface.fill((0, 0, 0))

    # ==========================
    # Sprites
    # ==========================
    groups["all_sprites"].draw(surface)

    # ==========================
    # Trails (draw like normal sprites)
    # ==========================
    groups["trail_group"].draw(surface)

    # ==========================
    # Boss Laser (if active)
    # ==========================
    for boss in groups["boss_group"]:
        if hasattr(boss, "draw_laser") and boss.laser_active:
            boss.draw_laser(surface)

    # ==========================
    # Boss Extra Drawing (tails, beams, etc.)
    # ==========================
    for boss in groups["boss_group"]:
        if hasattr(boss, "draw_extra"):
            boss.draw_extra(surface)

    # ==========================
    # HUD
    # ==========================
    draw_player_health_bar(surface, player, state)
    draw_shrapnel_cooldown(surface, player, state)

    # Boss health bar (if boss exists)
    boss = next(iter(groups["boss_group"]), None)
    if boss:
        draw_boss_health_bar(surface, boss, state)

    # ==========================
    # Debugger Overlay (if active)
    # ==========================
    if debugger.active:
        debugger.draw(surface, WIDTH, HEIGHT)

    # NOTE:
    # No pygame.display.flip() here.
    # main.py handles flipping after blitting the render surface.
