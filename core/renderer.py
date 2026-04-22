import pygame
import os
import sys
from ui.hud import draw as draw_hud

# ============================================================
#   RESOURCE PATH (PyInstaller-safe)
# ============================================================
def resource_path(relative_path):
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


def render_frame(surface, player, groups, state, debugger, clock):
    """
    Draws the entire frame to the provided surface:
    - Background
    - Trails
    - Thruster glow (behind player)
    - All sprites (player included)
    - Boss laser (if active)
    - HUD (health, cooldown, boss bar)
    - Debugger overlay (if active)

    This function contains ZERO game logic.
    """

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]

    # ==========================
    # Screen Shake Offset
    # ==========================
    shake_x = 0
    shake_y = 0

    if state.get("SCREEN_SHAKE_TIMER", 0) > 0:
        intensity = state.get("SCREEN_SHAKE_INTENSITY", 5)
        shake_x = int((pygame.time.get_ticks() % 3 - 1) * intensity)
        shake_y = int((pygame.time.get_ticks() % 3 - 1) * intensity)
        state["SCREEN_SHAKE_TIMER"] -= 1

    # Apply shake by shifting the entire frame
    def apply_offset(pos):
        return (int(pos[0] + shake_x), int(pos[1] + shake_y))

    # ==========================
    # Background
    # ==========================
    surface.fill((0, 0, 0))

    # ==========================
    # Trails (furthest back)
    # ==========================
    if "trail_group" in groups:
        for sprite in groups["trail_group"]:
            surface.blit(sprite.image, sprite.rect.move(shake_x, shake_y))

    # ==========================
    # Thruster Glow (behind player)
    # ==========================
    if player.thrusting:
        glow_img = pygame.transform.rotate(player.engine_glow_scaled, -player.angle)

        glow_offset = player.image.get_height() * 0.30
        backward_offset = -player.direction * glow_offset

        glow_pos = player.pos + backward_offset
        glow_rect = glow_img.get_rect(center=apply_offset((glow_pos.x, glow_pos.y)))

        surface.blit(glow_img, glow_rect)

    # ==========================
    # Sprites (player + enemies + bullets)
    # ==========================
    for sprite in groups["all_sprites"]:
        surface.blit(sprite.image, sprite.rect.move(shake_x, shake_y))

    # ==========================
    # Boss Laser (if active)
    # ==========================
    for boss in groups["boss_group"]:
        if hasattr(boss, "draw_laser") and boss.laser_active:
            temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            boss.draw_laser(temp_surface)
            surface.blit(temp_surface, (shake_x, shake_y))

    # ==========================
    # Boss Extra Drawing (tails, beams, etc.)
    # ==========================
    for boss in groups["boss_group"]:
        if hasattr(boss, "draw_extra"):
            boss.draw_extra(surface, offset=(shake_x, shake_y))

    # ==========================
    # HUD (no shake)
    # ==========================
    draw_hud(surface, player, state, groups, clock)

    # ==========================
    # Debugger Overlay (no shake)
    # ==========================
    if debugger.active:
        debugger.draw(surface, WIDTH, HEIGHT)

    # NOTE:
    # No pygame.display.flip() here.
    # main.py handles flipping after blitting the render surface.
