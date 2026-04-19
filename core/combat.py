import pygame
from entities.projectiles import Bullet


def handle_autofire(player, groups, sfx, state):
    """
    Handles all automatic firing behavior:
    - Fire button held
    - Powerup-based auto-fire (powerup_hits >= 2)
    - Spread weapon mode
    - Pew sound cooldown
    - Bullet creation + group insertion

    Parameters:
        player  – Player instance
        groups  – dict of sprite groups
        sfx     – sound effects dict
        state   – game state dict (contains last_pew_time)
    """

    # Must be allowed to fire
    if not (player.fire_button_held or player.powerup_hits >= 2):
        return

    # Fire cooldown still active
    if player.fire_cooldown > 0:
        return

    WIDTH = state["WIDTH"]
    HEIGHT = state["HEIGHT"]

    now = pygame.time.get_ticks()

    # --- Pew sound cooldown (150ms) ---
    if sfx.get("pew") and now - state["last_pew_time"] > 150:
        sfx["pew"].play()
        state["last_pew_time"] = now

    # --- Spread shot ---
    if player.weapon_mode == "SPREAD":
        for offset in (-15, 0, 15):
            b = Bullet(player.pos, player.angle + offset, WIDTH, HEIGHT)
            groups["bullets"].add(b)
            groups["all_sprites"].add(b)

    # --- Normal shot ---
    else:
        b = Bullet(player.pos, player.angle, WIDTH, HEIGHT)
        groups["bullets"].add(b)
        groups["all_sprites"].add(b)

    # Reset fire cooldown (matches original behavior)
    player.fire_cooldown = 10
