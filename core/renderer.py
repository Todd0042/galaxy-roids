from ui.hud import draw as draw_hud


def render_frame(surface, player, groups, state, debugger, clock):
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
    draw_hud(surface, player, state, groups, clock)

    # ==========================
    # Debugger Overlay (if active)
    # ==========================
    if debugger.active:
        debugger.draw(surface, WIDTH, HEIGHT)

    # NOTE:
    # No pygame.display.flip() here.
    # main.py handles flipping after blitting the render surface.
